from aiogram import Router
from aiogram.filters import CommandStart, Command

from telegram_bot.handlers.ai_conversation_handlers import ai_conversation_handler
from telegram_bot.handlers.start_handlers import start_handler, get_answers_handler


# Import your handle

def prepare_router() -> Router:

    router = Router()

    router.message.register(start_handler, CommandStart())

    #удалить
    router.message.register(get_answers_handler, Command('get'))
    router.message.register(ai_conversation_handler)


    return router
