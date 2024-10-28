from contextlib import contextmanager

from telegram_bot.database.create_connection import SessionLocal


# Контекстный менеджер для сессии
@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()



