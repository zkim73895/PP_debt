from sqlalchemy.orm import Session
from .database import User, Job, Application, Category, Department


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str, full_name: str, user_type: str):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "plaintext"], deprecated="auto")

    hashed_password = pwd_context.hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        user_type=user_type
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Job).filter(Job.is_active == True).offset(skip).limit(limit).all()


def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def create_application(db: Session, user_id: int, job_id: int, cover_letter: str = ""):
    application = Application(
        user_id=user_id,
        job_id=job_id,
        cover_letter=cover_letter,
        status="pending"
    )

    db.add(application)
    db.commit()
    db.refresh(application)
    return application