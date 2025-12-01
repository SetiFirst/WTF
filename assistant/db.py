from api_tools import SessionLocal, engine
from base.base import Base


def init_db():
    # Создание таблиц в базе данных
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()