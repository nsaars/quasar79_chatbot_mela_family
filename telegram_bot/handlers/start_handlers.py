from aiogram import types
from aiogram.fsm.context import FSMContext
from telegram_bot.data.config import ADMIN


async def start_handler(message: types.Message, state: FSMContext):
    from_user = message.from_user

    greeting_text = f"Здравствуйте, {from_user.full_name}, я виртуальный ассистент компании Mela Family Holding. " \
                    f"Давайте начнём заполнять анкету?"

    await message.answer(greeting_text)

    await state.update_data({'history': [('assistant', greeting_text)]})
    await state.set_state('ai_conversation')
    await message.bot.send_message(ADMIN, f"@{from_user.username} ({from_user.full_name}) написал в бота.")

# удалить
async def get_answers_handler(message: types.Message):
    with open('answers.txt', 'r', encoding='utf-8') as file:
        await message.answer(file.read())

