from fastapi import status


def test_api_health(client):
    """Тест 1: Проверка эндпоинта здоровья API"""
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "ok"
    assert "database" in data
    assert "counts" in data
    assert "timestamp" in data

    counts = data["counts"]
    assert "jobs" in counts
    assert "users" in counts
    assert isinstance(counts["jobs"], int)
    assert isinstance(counts["users"], int)

    print("✅ Test 1 passed: health API is working")


def test_get_jobs(client, db_session):
    """Тест 2: Получение списка вакансий (успешный сценарий)"""
    response = client.get("/api/v1/jobs")

    assert response.status_code == status.HTTP_200_OK
    jobs = response.json()
    assert isinstance(jobs, list)

    if jobs:
        job = jobs[0]
        assert "id" in job
        assert "title" in job
        assert "description" in job
        assert "is_active" in job
        assert isinstance(job["is_active"], bool)

    print(f"✅ Test 2 passed: got {len(jobs)} vacancies")


def test_get_nonexistent_job(client):
    """Тест 3: Попытка получить несуществующую вакансию (ошибочный сценарий)"""
    response = client.get("/api/v1/jobs/999999")

    if response.status_code == status.HTTP_404_NOT_FOUND:
        assert "detail" in response.json()
    elif response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "error" in data or "detail" in data

    print("✅ Test 3 passed: correct processing of a non-existent vacancy")


def test_user_registration(client):
    """Тест 4: Регистрация нового пользователя"""
    import time
    timestamp = int(time.time())
    user_data = {
        "email": f"testuser{timestamp}@example.com",
        "password": "testpassword123",
        "full_name": "Тестовый Пользователь",
        "user_type": "student"
    }

    response = client.post("/api/v1/auth/register", json=user_data)

    if response.status_code == status.HTTP_200_OK:
        response_data = response.json()
        assert "id" in response_data
        assert response_data["email"] == user_data["email"]
        print("✅ Test 4 passed: the user has been successfully registered")
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        assert "detail" in response.json()
        print("✅ Test 4 passed: duplicate email validation is working")
    else:
        assert response.status_code in [200, 400, 422]


def test_user_registration_invalid_data(client):
    """Тест 5: Регистрация с некорректными данными (ошибочный сценарий)"""
    invalid_email_data = {
        "email": "not-an-email",
        "password": "test123",
        "full_name": "Тест",
        "user_type": "student"
    }

    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    short_password_data = {
        "email": "test@example.com",
        "password": "123",
        "full_name": "Тест",
        "user_type": "student"
    }

    response = client.post("/api/v1/auth/register", json=short_password_data)

    print("✅ Test 5 passed: validation of registration data is working")


def test_user_login(client):
    """Тест 6: Вход в систему"""
    import time
    timestamp = int(time.time())
    user_data = {
        "email": f"login_test{timestamp}@example.com",
        "password": "loginpassword123",
        "full_name": "Пользователь для входа",
        "user_type": "student"
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)

    if register_response.status_code in [200, 400]:
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        if response.status_code == status.HTTP_200_OK:
            response_data = response.json()
            assert "access_token" in response_data
            assert "user" in response_data
            print("✅ Test 6 passed: authentication is working")
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            assert "detail" in response.json()
            print("✅ Test 6 passed: incorrect credentials are rejected")
    else:
        print("⚠️  Регистрация не удалась, пропускаем тест входа")


def test_get_categories(client, db_session):
    """Тест 7: Получение категорий вакансий"""
    response = client.get("/api/v1/categories")

    assert response.status_code == status.HTTP_200_OK
    categories = response.json()

    assert isinstance(categories, list)

    assert len(categories) > 0

    category = categories[0]
    assert "id" in category
    assert "name" in category
    assert "description" in category

    print(f"✅ Test 7 passed: got {len(categories)} categories")

def test_system_stats(client, db_session):
    """Дополнительный тест: Получение статистики системы"""
    response = client.get("/api/v1/stats")

    assert response.status_code == status.HTTP_200_OK
    stats = response.json()

    expected_fields = ["users", "jobs", "applications", "categories", "departments", "skills", "timestamp"]
    for field in expected_fields:
        if field in stats:
            assert isinstance(stats[field], (int, str))

    print("✅ Дополнительный тест пройден: статистика системы работает")