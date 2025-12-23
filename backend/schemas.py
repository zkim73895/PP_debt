from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    user_type: str  # student, employer

    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in ['student', 'employer']:
            raise ValueError('Тип пользователя должен быть "student" или "employer"')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    user_type: str
    is_active: bool
    created_at: datetime

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


class JobDetailResponse(JobResponse):
    category: Optional[dict] = None
    department: Optional[dict] = None
    employer: Optional[dict] = None
    skills: List[dict] = []

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
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    job: Optional[JobResponse] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    name: str


class SkillResponse(SkillBase):
    id: int

    class Config:
        from_attributes = True



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class JobWithRelationsResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    is_active: bool
    created_at: datetime
    category: Optional[dict] = None
    department: Optional[dict] = None
    employer: Optional[dict] = None
    skills: List[dict] = []

    class Config:
        from_attributes = True

class JobDetailResponse(JobWithRelationsResponse):
    pass