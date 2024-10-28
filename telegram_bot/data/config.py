import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
BOT_ID: str = BOT_TOKEN.split(":")[0]
ADMIN: int = int(os.getenv('ADMIN'))

# Texts
GREETING_TEMPLATE = (
    "Здравствуйте, {user_name}, я виртуальный ассистент компании Leading Group. "
    "Какой у вас вопрос?"
)
TEXT_ONLY_MESSAGE = "Меня настроили отвечать только на текстовые сообщения :)"
