from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend import models, database
from backend.database import get_db, create_tables, seed_initial_data

app = FastAPI(
    title="PP_dept API",
    description="API для платформы вакансий университета",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_tables()
    seed_initial_data()
    print("Таблицы БД созданы/проверены")

@app.get("/api/init-db")
async def init_db():
    create_tables()
    seed_initial_data()
    return {"message": "База данных инициализирована"}
@app.get("/")
async def root():
    return {"message": "PP_dept API работает!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}