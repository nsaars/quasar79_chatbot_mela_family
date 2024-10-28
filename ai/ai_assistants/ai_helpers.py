import base64
from typing import List, Tuple, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage

from ai.managers.prompt_manager import PromptManager
from ai.data.config import LLM_MODEL, MESSAGE_TYPE_DESCRIPTION, NEW_REQUEST_DESCRIPTION, PREVIOUS_LANGUAGE_DESCRIPTION


load_dotenv('/data/.env')

class AiHelpers:
    """
    Provides various AI helper functionalities.
    """

    def __init__(self):
        self._llm = ChatOpenAI(model=LLM_MODEL)
        self._prompt_manager = PromptManager()

    async def get_message_type(self, text: str, history: List[Tuple[str, str]]) -> Dict[str, int]:
        """
        Determines the type of message based on its content and chat history.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            self._prompt_manager.default_prompts['type_detector'],
            ('user', '{message}')
        ])

        class MessageTypeModel(BaseModel):
            type: int = Field(description=MESSAGE_TYPE_DESCRIPTION)

        response = await (prompt_template
                          | self._llm.with_structured_output(MessageTypeModel)
                          ).ainvoke({
                              'message': text,
                              'chat_history': history
                          })
        return {'type': response.type}

    async def get_new_request(self, text: str, history: List[Tuple[str, str]]) -> Dict[str, str]:
        """
        Modify the user's input if necessary.
        """
        if not text:
            raise ValueError("Input text cannot be empty")
        if not isinstance(history, list):
            raise TypeError("History must be a list of tuples")

        prompt_template = ChatPromptTemplate.from_messages([
            MessagesPlaceholder('chat_history'),
            ('system', self._prompt_manager.default_prompts['default_system']),
            ('user', self._prompt_manager.default_prompts['change_question'])
        ])

        class RequestModel(BaseModel):
            new_request: str = Field(description=NEW_REQUEST_DESCRIPTION)
            previous_language: str = Field(description=PREVIOUS_LANGUAGE_DESCRIPTION)

        response = await (prompt_template
                          | self._llm.with_structured_output(RequestModel)
                          ).ainvoke({'input': text, 'chat_history': history})

        return {'new_request': response.new_request, 'previous_language': response.previous_language}
    async def get_image_description(self, image_path: str, prev_text: str) -> Dict[str, str]:
        """
        Generates a description of an image based on the previous text.
        """
        if not image_path:
            raise ValueError("Image path cannot be empty")
        if not prev_text:
            raise ValueError("Previous text cannot be empty")

        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            self._prompt_manager.special_prompts['image_description'],
            HumanMessage(
                content=[
                    {"type": "text", "text": prev_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                ],
            ),
        ]

        response = await self._llm.ainvoke(messages)
        return {'image_description': response.content}

