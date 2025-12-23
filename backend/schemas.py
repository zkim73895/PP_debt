from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    user_type: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    user_type: str
    is_active: bool

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    category_id: Optional[int] = None
    department_id: Optional[int] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    is_active: bool
    created_at: datetime
    employer_id: Optional[int] = None

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    status_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True