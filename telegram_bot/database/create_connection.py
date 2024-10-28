from sqlalchemy import create_engine

from sqlalchemy import orm

from telegram_bot.models.base import Base

from telegram_bot.data import DATABASE_URL


def create_db_connection():

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SessionLocal = create_db_connection()
# session = SessionLocal()