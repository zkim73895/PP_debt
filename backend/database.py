from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func


DATABASE_URL = "sqlite:///./campus_jobs.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

job_skill_association = Table(
    'job_skill',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)


class User(Base):
    """1. Пользователи"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)  # student, employer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    employer_profile = relationship("EmployerProfile", back_populates="user", uselist=False,
                                    cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class StudentProfile(Base):
    """2. Профиль студента"""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    student_id = Column(String(20), unique=True)  # Номер студенческого
    faculty = Column(String(100))
    course = Column(Integer)
    phone = Column(String(20))
    resume = Column(Text)

    user = relationship("User", back_populates="student_profile")


class EmployerProfile(Base):
    """3. Профиль работодателя"""
    __tablename__ = "employer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    position = Column(String(100))
    phone = Column(String(20))

    user = relationship("User", back_populates="employer_profile")
    department = relationship("Department", back_populates="employers")
    jobs = relationship("Job", back_populates="employer")


class Department(Base):
    """4. Отдел/кафедра"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    employers = relationship("EmployerProfile", back_populates="department")
    jobs = relationship("Job", back_populates="department")


class Category(Base):
    """5. Категория вакансий"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    jobs = relationship("Job", back_populates="category")


class Skill(Base):
    """6. Навык"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    jobs = relationship("Job", secondary=job_skill_association, back_populates="skills")


class Job(Base):
    """7. Вакансия"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    salary = Column(String(50))
    job_type = Column(String(30))  # internship, part_time, full_time
    category_id = Column(Integer, ForeignKey("categories.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    employer_id = Column(Integer, ForeignKey("employer_profiles.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True))

    category = relationship("Category", back_populates="jobs")
    department = relationship("Department", back_populates="jobs")
    employer = relationship("EmployerProfile", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    skills = relationship("Skill", secondary=job_skill_association, back_populates="jobs")


class Application(Base):
    """8. Заявка на вакансию"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String(20), default="pending")  # pending, reviewed, accepted, rejected
    cover_letter = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class Notification(Base):
    """9. Уведомление"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


class ApplicationStatus(Base):
    """10. Статус заявки (отдельная сущность как в ТЗ)"""
    __tablename__ = "application_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    description = Column(Text)


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создание всех таблиц в БД"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы БД созданы")


def seed_initial_data(db):
    """Заполнение начальными данными"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    statuses = [
        {"name": "pending", "description": "На рассмотрении"},
        {"name": "reviewed", "description": "Просмотрено"},
        {"name": "accepted", "description": "Принято"},
        {"name": "rejected", "description": "Отклонено"}
    ]

    for status_data in statuses:
        if not db.query(ApplicationStatus).filter_by(name=status_data["name"]).first():
            status = ApplicationStatus(**status_data)
            db.add(status)

    categories = [
        {"name": "Преподавание", "description": "Работа ассистентом преподавателя"},
        {"name": "Исследования", "description": "Научно-исследовательская работа"},
        {"name": "Администрация", "description": "Административная работа"},
        {"name": "IT", "description": "IT-специальности"},
        {"name": "Библиотека", "description": "Работа в библиотеке"}
    ]

    for category_data in categories:
        if not db.query(Category).filter_by(name=category_data["name"]).first():
            category = Category(**category_data)
            db.add(category)

    skills = ["Python", "Java", "SQL", "Английский язык", "Коммуникабельность", "Организация"]
    for skill_name in skills:
        if not db.query(Skill).filter_by(name=skill_name).first():
            skill = Skill(name=skill_name)
            db.add(skill)

    departments = [
        {"name": "Кафедра информационных технологий", "description": "IT-кафедра"},
        {"name": "Деканат", "description": "Административный отдел"},
        {"name": "Научно-исследовательский центр", "description": "НИЦ университета"},
        {"name": "Библиотека", "description": "Университетская библиотека"}
    ]

    for dept_data in departments:
        if not db.query(Department).filter_by(name=dept_data["name"]).first():
            department = Department(**dept_data)
            db.add(department)

    try:
        db.commit()
        print("✅ Начальные данные добавлены")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении данных: {e}")