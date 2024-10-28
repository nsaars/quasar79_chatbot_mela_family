import os
from datetime import datetime
from typing import List, Tuple, Dict, Any

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from ai.ai_chain import AiChain
from telegram_bot.data.config import TEXT_ONLY_MESSAGE, GREETING_TEMPLATE

ai_chain = AiChain()

async def ai_conversation_handler(message: types.Message, state: FSMContext) -> None:
    if message.content_type != types.ContentType.TEXT:
        await message.answer(TEXT_ONLY_MESSAGE)
        return
    state_data: Dict[str, Any] = await state.get_data()

    # todo: переместить в мидлваре
    if state_data.get('is_bot_answering'):
        seconds_from_last_message = (datetime.now() - state_data.get('start_answering_time')).seconds
        if seconds_from_last_message > 2 and not state_data.get('warned_about_answering'):
            await state.update_data(warned_about_answering=True)

            await message.answer(
                "Секундочку, уже отвечаю на предыдущее смс :)",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        if seconds_from_last_message < 1:
            return


    list_of_messages = state_data.get('list_of_messages', []) + [message.text]
    await state.update_data(is_bot_answering=True, start_answering_time=datetime.now(), list_of_messages=list_of_messages)

    history: List[Tuple[str, str]] = state_data.get('history', [])
    if not history:
        greeting = GREETING_TEMPLATE.format(user_name=message.from_user.full_name)
        history.append(('assistant', greeting))
    async with ChatActionSender.typing(message.chat.id, message.bot):
        full_request = ' '.join(list_of_messages)
        response: str = await ai_chain.get_response(full_request, history)
        history.extend([
            ('user', full_request),
            ('assistant', response)
        ])

        state_data: Dict[str, Any] = await state.get_data()
        # если пользователь написал ещё одно сообщение, запустив этот хендлер повторно, то list_of_messages обновиться
        if len(state_data.get('list_of_messages', [])) > len(list_of_messages):
            return

        print(full_request)
        await message.answer(
            response,
            parse_mode=ParseMode.MARKDOWN
        )

        await state.update_data(history=history, is_bot_answering=False, start_answering_time=None, list_of_messages=[], warned_about_answering=False)

