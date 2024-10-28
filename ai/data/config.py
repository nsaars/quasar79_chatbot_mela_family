import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
PROMPTS_DIR = BASE_DIR / "prompts"
CACHE_DIR = BASE_DIR / "cache"
DOCUMENTS_DIR = BASE_DIR / "documents"
RAG_DIR = BASE_DIR / "rag"

# Files
TXT_FILES = [str(DOCUMENTS_DIR / path) for path in os.listdir(DOCUMENTS_DIR)]
print(TXT_FILES)
DEFAULT_PROMPT_PATH = PROMPTS_DIR / "default_prompt_templates.json"
SPECIAL_PROMPT_PATH = PROMPTS_DIR / "special_prompt_templates.json"

# Models
LLM_MODEL = 'gpt-4o'
EMBEDDING_MODEL = 'text-embedding-3-large'
SEARCH_QUANTITY = 2

# Prompts information
COMPANY_NAME = "Mela Family Holding"
COMPANY_ABOUT = f"Компания {COMPANY_NAME} занимается продюсированием для создания личного бренда."
THEME = f"компании {COMPANY_NAME}, анкете для создания личного бренда и по её вопросам"
# Texts
NOT_RELEVANT = f"Я бы не прочь поговорить на отвлечённые темы, но я на работе. Если у вас есть вопросы по поводу {THEME}, буду рад помочь!"
NEW_REQUEST_DESCRIPTION = "Изменённый запрос"
PREVIOUS_LANGUAGE_DESCRIPTION = "Язык первоначального запроса (до изменения)."
MESSAGE_TYPE_DESCRIPTION = "Тип сообщения"
ANSWER_MESSAGE_DESCRIPTION ="Сообщение, которое нужно отправить клиенту"
QUESTION_TO_CHANGE_DESCRIPTION = "Номер вопроса, на который клиент хочет заменить ответ."
DOCUMENTS_DESCRIPTION = "Список из двух выбранных тобой разделов или одного файла."

CONSULTATION_DESCRIPTION = ("Получить желаемые клиенту дату и время для бесплатной 30 минутной онлайн консультации. "
                               "Тебе нужно получить точную дату и время от клиента. Убедись, что клиент назвал "
                               "дату и время, не придумывай ничего от себя. Сейчас {current_date_time}. "
                               "Консультации можно назначить на любое время с 13:00 по 18:00 на каждый день, кроме среды и воскресенья. "
                               "Обращай внимание на текущий день прежде чем соглашаться на консультацию или предлагать время для консультации.")
