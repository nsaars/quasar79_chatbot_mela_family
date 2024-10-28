from typing import List, Tuple, Dict, Any, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ai.managers.prompt_manager import PromptManager
from ai.data.config import LLM_MODEL, MESSAGE_TYPE_DESCRIPTION


class AiSurvey:
    """
    Provides various AI helper functionalities.
    """

    def __init__(self):
        self._llm = ChatOpenAI(model=LLM_MODEL)
        self._prompt_manager = PromptManager()

    async def encourage_survey_beginning(self, text: str, history: List[Tuple[str, str]], **kwargs: Dict) -> BaseMessage:
        """
        Determines the type of message based on its content and chat history.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', self._prompt_manager.special_prompts['encourage_survey_beginning']),
        ])

        prompt_kwargs = {
                'message': text,
                'chat_history': history
        }
        if kwargs:
            prompt_kwargs.update(**kwargs)

        return await (prompt_template
                          | self._llm
                          ).ainvoke(prompt_kwargs)



    async def validate_client_answer(self, text: str, history: List[Tuple[str, str]], full_client_answer: str, **kwargs: Dict):
        """
        Determines the type of message based on its content and chat history.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', self._prompt_manager.special_prompts['validate_client_answer']),
        ])

        class MessageTypeModel(BaseModel):
            is_relevant: bool = Field(description="Является ли сообщение клиента подходящим в качестве ответа на вопрос.")
            message: Optional[str] = Field(description="Твоё сообщение клиенту. Необходимо, когда сообщение клиента не подходит в качестве ответа на вопрос. То есть is_relevant=False")

        prompt_kwargs = {
                'message': text,
                'chat_history': history,
                'full_client_answer': full_client_answer
        }
        if kwargs:
            prompt_kwargs.update(**kwargs)

        return await (prompt_template
                          | self._llm.with_structured_output(MessageTypeModel)
                          ).ainvoke(prompt_kwargs)


    async def identify_question_to_change(self, text: str, history: List[Tuple[str, str]], **kwargs: Dict):
        """
        Determines the type of message based on its content and chat history.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', self._prompt_manager.special_prompts['identify_question_to_change']),
        ])

        class MessageTypeModel(BaseModel):
            changing_answer_number: Optional[int] = Field(
                description="Номер вопроса, на который клиент хочет изменить свой ответ. Нужно вернуть, если ты точно понял, какой номер вопроса.")
            message: Optional[str] = Field(
                description="Твоё сообщение клиенту. Необходимо, когда ты не понял, на какой вопрос клиент хочет изменить свой ответ.")

        prompt_kwargs = {
            'message': text,
            'chat_history': history
        }
        if kwargs:
            prompt_kwargs.update(**kwargs)

        return await (prompt_template
                          | self._llm.with_structured_output(MessageTypeModel)
                          ).ainvoke(prompt_kwargs)

    async def make_full_client_answer(self, text: str, history: List[Tuple[str, str]], **kwargs: Dict) -> BaseMessage:
        """
        Determines the type of message based on its content and chat history.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('user', '{message}'),

            ('system', self._prompt_manager.default_prompts['default_backend_system']),
            ('user', self._prompt_manager.special_prompts['make_full_client_answer']),
        ])

        prompt_kwargs = {
            'message': text,
            'chat_history': history
        }
        if kwargs:
            prompt_kwargs.update(**kwargs)

        return await (prompt_template
                          | self._llm
                          ).ainvoke(prompt_kwargs)


