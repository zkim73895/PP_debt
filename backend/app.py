from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.database import get_db, create_tables, seed_initial_data
from backend import schemas
from backend.database import (
    User, StudentProfile, EmployerProfile, Department,
    Category, Skill, Job, Application, Notification, ApplicationStatus
)

app = FastAPI(
    title="Campus Jobs API",
    description="API для платформы поиска работы в университете",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(FRONTEND_PATH):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
    print(f"✅ Статические файлы настроены: {FRONTEND_PATH}")
else:
    print(f"⚠️  Папка фронтенда не найдена: {FRONTEND_PATH}")
    # Создаем временную папку для тестов
    os.makedirs(FRONTEND_PATH, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Создание таблиц и начальных данных при запуске"""
    create_tables()

    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()

    print("🚀 Campus Jobs API запущен с базой данных!")


@app.get("/")
def root():
    return {
        "message": "Campus Jobs API с базой данных",
        "version": "1.0.0",
        "database": "SQLite (10 сущностей)",
        "docs": "/api/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/health")
def api_health(db: Session = Depends(get_db)):
    """Проверка здоровья API и БД"""
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"

    jobs_count = db.query(Job).count()
    users_count = db.query(User).count()

    return {
        "status": "ok",
        "database": db_status,
        "counts": {
            "jobs": jobs_count,
            "users": users_count
        },
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/api/v1/jobs", response_model=List[schemas.JobResponse])
def get_jobs(
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
        category_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Получить список вакансий ИЗ БАЗЫ ДАННЫХ"""
    query = db.query(Job)

    if active_only:
        query = query.filter(Job.is_active == True)

    if category_id:
        query = query.filter(Job.category_id == category_id)

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    if not jobs:
        print("⚠️ Нет вакансий в БД, создаем тестовые...")
        from .database import Category, Department, EmployerProfile

        category = db.query(Category).first()
        department = db.query(Department).first()
        employer = db.query(EmployerProfile).first()

        if category and department and employer:
            test_jobs = [
                Job(
                    title="Ассистент преподавателя",
                    description="Помощь в проведении лабораторных работ",
                    requirements="Знание Python",
                    salary="15000 руб./мес.",
                    job_type="part_time",
                    category_id=category.id,
                    department_id=department.id,
                    employer_id=employer.id,
                    is_active=True
                ),
                Job(
                    title="Исследователь",
                    description="Научная работа",
                    requirements="Аналитическое мышление",
                    salary="20000 руб./мес.",
                    job_type="internship",
                    category_id=category.id,
                    department_id=department.id,
                    employer_id=employer.id,
                    is_active=True
                )
            ]

            for job in test_jobs:
                db.add(job)
            db.commit()

            jobs = db.query(Job).filter(Job.is_active == True).all()

    return jobs


@app.get("/api/v1/jobs/{job_id}", response_model=schemas.JobDetailResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Получить вакансию по ID ИЗ БАЗЫ ДАННЫХ"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")

    result = {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements,
        "salary": job.salary,
        "job_type": job.job_type,
        "is_active": job.is_active,
        "created_at": job.created_at,
        "category_id": job.category_id,
        "department_id": job.department_id,
        "employer_id": job.employer_id
    }

    if job.category:
        result["category"] = {"id": job.category.id, "name": job.category.name}

    if job.department:
        result["department"] = {"id": job.department.id, "name": job.department.name}

    if job.employer and job.employer.user:
        result["employer"] = {"id": job.employer.id, "name": job.employer.user.full_name}

    result["skills"] = [{"id": skill.id, "name": skill.name} for skill in job.skills]

    return result


@app.post("/api/v1/jobs", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """Создать новую вакансию (для работодателей)"""
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.get("/api/v1/categories", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Получить список категорий ИЗ БАЗЫ ДАННЫХ"""
    categories = db.query(Category).all()

    if not categories:
        categories = [
            Category(name="Преподавание", description="Работа ассистентом"),
            Category(name="Исследования", description="Научная работа"),
            Category(name="Администрация", description="Административная работа")
        ]
        for cat in categories:
            db.add(cat)
        db.commit()
        categories = db.query(Category).all()

    return categories


@app.get("/api/v1/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    """Получить список отделов ИЗ БАЗЫ ДАННЫХ"""
    return db.query(Department).all()


@app.get("/api/v1/skills", response_model=List[schemas.SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    """Получить список навыков"""
    return db.query(Skill).all()


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "plaintext"], deprecated="auto")

    hashed_password = pwd_context.hash(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post("/api/v1/auth/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "plaintext"], deprecated="auto")

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    return {
        "access_token": "demo-token-" + str(user.id),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type
        }
    }


@app.get("/api/v1/applications")
def get_applications(
        db: Session = Depends(get_db)
):
    """Получить список заявок - УПРОЩЕННАЯ ВЕРСИЯ"""
    try:
        applications = db.query(Application).all()

        result = []
        for app in applications:
            app_data = {
                "id": app.id,
                "user_id": app.user_id,
                "job_id": app.job_id,
                "status": app.status,
                "cover_letter": app.cover_letter,
                "created_at": app.created_at
            }

            # Добавляем информацию о вакансии если есть
            if app.job:
                app_data["job"] = {
                    "id": app.job.id,
                    "title": app.job.title,
                    "salary": app.job.salary
                }

            # Добавляем информацию о пользователе если есть
            if app.user:
                app_data["user"] = {
                    "id": app.user.id,
                    "email": app.user.email,
                    "full_name": app.user.full_name,
                    "user_type": app.user.user_type
                }

            result.append(app_data)

        return result

    except Exception as e:
        print(f"❌ Ошибка при получении заявок: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/api/v1/applications", response_model=List[schemas.ApplicationDetailResponse])
def get_applications(db: Session = Depends(get_db)):
    """Получить список заявок"""
    applications = db.query(Application).all()
    return applications


@app.post("/api/v1/admin/seed")
@app.get("/api/v1/admin/seed")
def seed_database(db: Session = Depends(get_db)):
    """Заполнить базу тестовыми данными"""
    try:
        print("Начинаем создание тестовых данных...")

        existing_user = db.query(User).filter(User.email == "student@university.edu").first()
        if existing_user:
            print("✅ Тестовые данные уже существуют")
            return {
                "success": True,
                "message": "Тестовые данные уже существуют",
                "users": [
                    {"email": "student@university.edu", "password": "student123", "type": "student"},
                    {"email": "employer@university.edu", "password": "employer123", "type": "employer"}
                ]
            }

        from passlib.context import CryptContext

        pwd_context = CryptContext(
            schemes=["pbkdf2_sha256", "plaintext"],
            deprecated="auto"
        )

        print("👤 Создаем тестовых пользователей...")

        student_user = User(
            email="student@university.edu",
            hashed_password=pwd_context.hash("student123"),
            full_name="Иван Иванов",
            user_type="student"
        )
        db.add(student_user)
        db.flush()

        student_profile = StudentProfile(
            user_id=student_user.id,
            student_id="2024001",
            faculty="Факультет информационных технологий",
            course=3
        )
        db.add(student_profile)

        employer_user = User(
            email="employer@university.edu",
            hashed_password=pwd_context.hash("employer123"),
            full_name="Петр Петров",
            user_type="employer"
        )
        db.add(employer_user)
        db.flush()

        department = db.query(Department).first()
        if not department:
            department = Department(name="Кафедра информационных технологий")
            db.add(department)
            db.flush()

        employer_profile = EmployerProfile(
            user_id=employer_user.id,
            department_id=department.id,
            position="Заведующий кафедрой"
        )
        db.add(employer_profile)

        print("💼 Создаем тестовые вакансии...")

        category = db.query(Category).first()
        if not category:
            category = Category(name="Преподавание")
            db.add(category)
            db.flush()

        job1 = Job(
            title="Ассистент преподавателя",
            description="Помощь в проведении лабораторных работ",
            requirements="Знание Python",
            salary="15000 руб./мес.",
            job_type="part_time",
            category_id=category.id,
            department_id=department.id,
            employer_id=employer_profile.id,
            is_active=True,
            deadline=datetime.datetime.now() + datetime.timedelta(days=30)
        )
        db.add(job1)

        job2 = Job(
            title="Исследователь",
            description="Научная работа в лаборатории",
            requirements="Аналитическое мышление",
            salary="20000 руб./мес.",
            job_type="internship",
            category_id=category.id,
            department_id=department.id,
            employer_id=employer_profile.id,
            is_active=True,
            deadline=datetime.datetime.now() + datetime.timedelta(days=45)
        )
        db.add(job2)

        print("📝 Создаем тестовую заявку...")

        application = Application(
            user_id=student_user.id,
            job_id=job1.id,
            cover_letter="Хочу работать ассистентом!",
            status="pending"
        )
        db.add(application)

        db.commit()

        print("✅ Тестовые данные успешно созданы!")

        return {
            "success": True,
            "message": "Тестовые данные созданы",
            "test_users": [
                {"email": "student@university.edu", "password": "student123", "type": "student"},
                {"email": "employer@university.edu", "password": "employer123", "type": "employer"}
            ],
            "jobs_created": 2,
            "application_created": True
        }

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка: {str(e)}"
        )


@app.get("/api/v1/stats")
def get_stats(db: Session = Depends(get_db)):
    """Получить статистику системы"""
    return {
        "users": db.query(User).count(),
        "students": db.query(StudentProfile).count(),
        "employers": db.query(EmployerProfile).count(),
        "jobs": db.query(Job).filter(Job.is_active == True).count(),
        "applications": db.query(Application).count(),
        "categories": db.query(Category).count(),
        "departments": db.query(Department).count(),
        "skills": db.query(Skill).count(),
        "notifications": db.query(Notification).count(),
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/")
def serve_frontend():
    """Перенаправляем на фронтенд"""
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))


@app.get("/frontend/{path:path}")
def serve_frontend_file(path: str):
    """Обслуживаем файлы из папки frontend"""
    file_path = os.path.join(FRONTEND_PATH, path)

    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        # Если файл не найден, пробуем добавить .html
        html_path = file_path + ".html"
        if os.path.exists(html_path):
            return FileResponse(html_path)
        else:
            raise HTTPException(status_code=404, detail="Файл не найден")