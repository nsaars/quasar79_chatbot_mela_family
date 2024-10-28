from datetime import datetime
from typing import List, Tuple, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, BaseMessage

from ai.managers.prompt_manager import PromptManager
from ai.data.config import LLM_MODEL, NEW_REQUEST_DESCRIPTION, PREVIOUS_LANGUAGE_DESCRIPTION


load_dotenv()


class AiQuestionAnswering:
    """
    Handles AI question-answering functionality.
    """

    def __init__(self, helpers, embeddings_manager, tools):

        self._llm = ChatOpenAI(model=LLM_MODEL)
        self.helpers = helpers
        self._inactive_tools = tools
        self._embeddings = embeddings_manager
        self._retriever = self._embeddings.get_retriever()
        self._prompt_manager = PromptManager()

    @staticmethod
    def format_docs(similar_docs) -> str:
        """
        Format retrieved documents into a string.
        """
        return "\n\n".join(doc.page_content for doc in similar_docs)

    def get_activated_tools(self):
        activated_tools = [tool() for tool in self._inactive_tools]
        return activated_tools


    async def get_question_response(self, text: str, history: List[Tuple[str, str]], **kwargs: Dict) -> BaseMessage:
        """
        Get the specialized response to the user's question.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        new_request_info = await self.helpers.get_new_request(text, history)
        new_request = new_request_info['new_request']
        previous_language = new_request_info['previous_language']

        # Retrieve context
        similar_docs = await self._retriever.ainvoke(new_request)
        print([doc.metadata['file_name'] for doc in similar_docs])
        context = self.format_docs(similar_docs)

        is_survey_in_process = kwargs.get('is_survey_in_process')
        is_answer_changing = kwargs.get('is_answer_changing')

        if not is_survey_in_process:
            user_message = self._prompt_manager.special_prompts['give_question_answer:survey_to_start']
        elif is_answer_changing:
            user_message = self._prompt_manager.special_prompts['give_question_answer:answer_changing']
        else:
            user_message = self._prompt_manager.special_prompts['give_question_answer:survey_in_process']

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', user_message)
        ])

        return await (prompt_template
                          | self._llm
                          ).ainvoke({
                              'message': new_request,
                              'context': context,
                              'language': previous_language,
                              'chat_history': history
                          })


    async def get_default_response(self, text: str, history: List[Tuple[str, str]], **kwargs: Dict) -> BaseMessage:
        """
        Get the response to the user's question.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        is_survey_in_process = kwargs.get('is_survey_in_process')
        is_answer_changing = kwargs.get('is_answer_changing')

        if not is_survey_in_process:
            user_message = self._prompt_manager.special_prompts['give_dialog_answer:survey_to_start']
        elif is_answer_changing:
            user_message = self._prompt_manager.special_prompts['give_dialog_answer:answer_changing']
        else:
            user_message = self._prompt_manager.special_prompts['give_dialog_answer:survey_in_process']

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', user_message)
        ])

        prompt_kwargs = {
                'message': text,
                'chat_history': history}
        if kwargs:
            prompt_kwargs.update(**kwargs)

        return await (prompt_template
                          | self._llm
                          ).ainvoke(prompt_kwargs)

