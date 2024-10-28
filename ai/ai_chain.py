import os
import re
import asyncio
import logging
from enum import Enum
from typing import List, Dict, Tuple, Optional

from six import reraise

from ai.ai_assistants.ai_survey import AiSurvey
from ai.data.config import NOT_RELEVANT
from ai.survey import Survey
from ai.tools.consultation import ConsultationTool
from ai.managers.document_manager import DocumentManager
from ai.managers.embedding_manager import EmbeddingManager

from ai.ai_assistants.ai_helpers import AiHelpers
from ai.ai_assistants.ai_question_answering import AiQuestionAnswering


current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO)


class AiChain:
    """
    AiChain class orchestrates AI interactions, processing user inputs,
    and generating appropriate responses.
    """

    def __init__(self):
        self.decision: Optional[str] = None
        self.responses: Dict[str, str] = {
            'not_relevant': NOT_RELEVANT
        }
        self.doc_loader = DocumentManager()
        self.embedding_manager = EmbeddingManager()
        self.documents, self.documents_kwargs = self.doc_loader.load_documents()
        self.embedding_manager.setup_retriever(self.documents)

        self.helpers = AiHelpers()
        self.qa = AiQuestionAnswering(self.helpers, self.embedding_manager, [ConsultationTool])
        self.survey_ai = AiSurvey()

        self.survey = Survey('/home/malik/PycharmProjects/self_brand/ai/survey.txt')
        self.history = []


    async def _process_function_call(self, message): #todo: define tools in class
        """
        Process any function call returned in the message.

        Args:
            message: The message object from AI modules.

        Returns:
            Dict or None: The response dictionary if a function call is processed, else None.
        """
        print(message.tool_calls)
        for tool_call in message.tool_calls:
            if tool_call.get('name') == 'schedule_consultation':
                response = ConsultationTool()._run(**tool_call.get('args'))
                return {
                    'text': response
                }
        return None

    async def validate_client_answer(self, message, history, full_client_answer, depth=2, **kwargs):
        validation = await self.survey_ai.validate_client_answer(message, history, full_client_answer, **kwargs)
        print(validation)
        if validation.is_relevant or depth == 0:
            self.survey.set_answer(self.survey.current_question_number, full_client_answer)
            return self.survey.get_next_question_message(update_current_question_number=True)

        bot_message = validation.message
        if bot_message:
            return bot_message

        return await self.validate_client_answer(message, history, full_client_answer, depth=depth-1, **kwargs)

    async def identify_question_to_change(self, message, history, depth=2, **kwargs):
        identity_result = await self.survey_ai.identify_question_to_change(message, history, **kwargs)
        print(identity_result)

        changing_answer_number = identity_result.changing_answer_number
        if changing_answer_number:
            bot_message, validation = self.survey.get_change_answer_message(question_number=changing_answer_number)
            if validation:
                self.survey.is_answer_changing = True
                self.survey.changing_answer_number = changing_answer_number
            return bot_message

        bot_message = identity_result.get('message')
        if bot_message:
            return bot_message

        if depth == 0:
            return "Я не совсем понял, на какого вопрос вы хотите изменить ответ. Пожалуйста, дайте корректный номер этого вопроса."

        return await self.identify_question_to_change(message, history, depth=depth-1, **kwargs)

    @staticmethod
    def get_type(message_type: int, **kwargs):
        is_survey_in_process = kwargs.get('is_survey_in_process')
        is_answer_changing = kwargs.get('is_answer_changing')

        if message_type == 1:
            return 'question'
        if message_type == 4:
            return 'default'

        if not is_survey_in_process:
            if message_type == 2:
                return 'start_survey'
            if message_type == 3:
                return 'deny_to_start_survey'
        elif is_answer_changing:
            if message_type == 2:
                return 'set_new_answer_for_question'
            if message_type == 3:
                return 'cancel_changing_answer'
            if message_type == 5:
                return 'change_question_answer'
        else:
            if message_type == 2:
                return 'survey_question_answer'
            if message_type == 3:
                return 'change_question_answer'

    async def get_response(self, message, history) -> str:
        is_survey_in_process = self.survey.is_survey_in_process
        is_answer_changing = self.survey.is_answer_changing
        kwargs = dict(is_answer_changing=is_answer_changing, is_survey_in_process=is_survey_in_process)

        survey_progress = self.survey.get_survey_progress()
        if is_survey_in_process:
            kwargs.update(
                answered_questions_count=survey_progress['passed_questions'],
                remaining_questions_count=survey_progress['remaining_questions']
            )
        else:
            kwargs.update(
                questions_count=survey_progress['total_questions'],
            )

        if is_answer_changing:
            changing_answer_question_number, changing_answer_question = self.survey.get_changing_answer_question()
            kwargs.update(current_question=changing_answer_question)
        else:
            current_question_number, current_question = self.survey.get_current_question()
            kwargs.update(current_question=current_question)

        type_detector_response = await self.helpers.get_message_type(message, history, **kwargs)
        message_type = self.get_type(type_detector_response.type, **kwargs)
        print(type_detector_response, message_type)

        if message_type == 'question':
            return (await self.qa.get_question_response(message, history)).content
        elif message_type == 'default':
            return (await self.qa.get_default_response(message, history, **kwargs)).content

        elif message_type == 'start_survey':
            self.survey.start_survey()
            return self.survey.get_start_survey_message()
        elif message_type == 'deny_to_start_survey':
            return (await self.survey_ai.encourage_survey_beginning(message, history, **kwargs)).content

        elif message_type == 'survey_question_answer':
            full_client_answer = (await self.survey_ai.make_full_client_answer(message, history, **kwargs)).content
            print(full_client_answer)
            return await self.validate_client_answer(message, history, full_client_answer, **kwargs)
        elif message_type == 'change_question_answer':
            return await self.identify_question_to_change(message, history, **kwargs)

        elif message_type == 'set_new_answer_for_question':
            self.survey.set_answer(self.survey.changing_answer_number, message)
            self.survey.is_answer_changing = False
            self.survey.changing_answer_number = None
            return self.survey.get_new_answer_set_message()
        elif message_type == 'cancel_changing_answer':
            self.survey.is_answer_changing = False
            self.survey.changing_answer_number = None
            return self.survey.get_cancel_changing_answer_message()


#todo: сделать команду /change_answer в меню, которая будет интепртироваться как 'я хочу поменять свой ответ на один из вопросов'
# при старте обнулять
# иногда говорит что не по теме, хотя по теме
