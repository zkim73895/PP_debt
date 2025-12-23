from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./campus_jobs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def seed_initial_data():
    from sqlalchemy.orm import Session
    from backend import models

    db = SessionLocal()

    try:
        statuses = db.query(models.ApplicationStatus).all()
        if not statuses:
            statuses_data = [
                {"name": "new", "description": "Новая заявка"},
                {"name": "reviewed", "description": "Просмотрена"},
                {"name": "accepted", "description": "Принята"},
                {"name": "rejected", "description": "Отклонена"},
            ]

            for status_data in statuses_data:
                status = models.ApplicationStatus(**status_data)
                db.add(status)

            categories_data = [
                {"name": "Преподавание", "description": "Ассистент преподавателя, ведение семинаров"},
                {"name": "Исследования", "description": "Научно-исследовательская работа"},
                {"name": "Администрация", "description": "Работа в административных отделах"},
                {"name": "IT", "description": "Программирование, техподдержка"},
                {"name": "Библиотека", "description": "Работа в библиотеке"},
            ]

            for category_data in categories_data:
                category = models.Category(**category_data)
                db.add(category)

            db.commit()
            print("Начальные данные созданы успешно")

    except Exception as e:
        print(f"Ошибка при создании начальных данных: {e}")
        db.rollback()

    finally:
        db.close()