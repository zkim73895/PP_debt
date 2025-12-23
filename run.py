import uvicorn
import sys
import os

print("ЗАПУСК CAMPUS JOBS API С БАЗОЙ ДАННЫХ")

print("\n ПРОВЕРКА БАЗЫ ДАННЫХ:")

try:
    from backend.database import SessionLocal, Job, User, Application

    db = SessionLocal()

    jobs_count = db.query(Job).count()
    users_count = db.query(User).count()
    apps_count = db.query(Application).count()

    print(f"   Вакансий в БД: {jobs_count}")
    print(f"   Пользователей в БД: {users_count}")
    print(f"   Заявок в БД: {apps_count}")

    if jobs_count == 0:
        print("   ⚠️ Нет вакансий в БД! Используйте /api/v1/admin/seed")
    else:
        print("   ✅ База данных содержит данные")

    db.close()

except Exception as e:
    print(f"   ❌ Ошибка проверки БД: {e}")

print(f"Текущая директория: {os.getcwd()}")

app_path = os.path.join(os.getcwd(), "backend", "app.py")
db_path = os.path.join(os.getcwd(), "backend", "database.py")

if not os.path.exists(app_path):
    print(f"❌ ОШИБКА: Файл {app_path} не найден!")
    sys.exit(1)

if not os.path.exists(db_path):
    print(f"❌ ОШИБКА: Файл {db_path} не найден!")
    sys.exit(1)

print("✅ Все необходимые файлы найдены")

try:
    from backend.app import app

    print("✅ Приложение успешно загружено")

    print("\n📋 ЗАРЕГИСТРИРОВАННЫЕ МАРШРУТЫ:")

    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            methods = getattr(route, "methods", ["GET"])
            path = getattr(route, "path", "")
            routes.append((methods, path))

    routes.sort(key=lambda x: x[1])

    for methods, path in routes:
        methods_str = ", ".join(methods) if methods else "GET"
        print(f"  {methods_str:15} {path}")

    print(f"Всего маршрутов: {len(routes)}")

except Exception as e:
    print(f"❌ ОШИБКА при загрузке приложения: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("ССЫЛКИ ДЛЯ ДОСТУПА:")
print("Документация:        http://localhost:8000/api/docs")
print("Статистика:          http://localhost:8000/api/v1/stats")
print("Заполнить тест.дан.: http://localhost:8000/api/v1/admin/seed")
print("Вакансии:            http://localhost:8000/api/v1/jobs")
print("Категории:           http://localhost:8000/api/v1/categories")
print("Отделы:              http://localhost:8000/api/v1/departments")
print("\n Сервер запускается... (Ctrl+C для остановки)\n")

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )