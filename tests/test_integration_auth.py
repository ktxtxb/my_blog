import pytest

def test_register_user_success(client):
    """Тест успешной регистрации пользователя"""
    user_data = {
        "login": "newuser",
        "email": "new@example.com",
        "password": "securepass123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "newuser"
    assert "user_id" in data


def test_register_user_duplicate_email(client, test_user):
    """Тест регистрации с существующим email"""
    user_data = {
        "login": "differentuser",
        "email": "test@example.com",  # Такой email уже есть
        "password": "securepass123"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 400
    data = response.json()
    assert "Email already exists" in data["detail"]


def test_login_success(client, test_user):
    """Тест успешного входа"""
    login_data = {
        "username": "testuser",  # ЛОГИН пользователя
        "password": "testpass123"
    }

    response = client.post("/auth/login", data=login_data)

    # Дебаг вывод
    if response.status_code != 200:
        print(f"DEBUG Login failed. Status: {response.status_code}")
        print(f"DEBUG Response: {response.text}")
        print(f"DEBUG Test user: login={test_user.login}, email={test_user.email}")

    assert response.status_code == 200, f"Login failed: {response.text}"

    data = response.json()
    # Проверяем оба возможных ключа
    assert "access_token" in data or "token" in data
    assert data.get("login") == "testuser"


def test_login_wrong_password(client, test_user):
    """Тест входа с неправильным паролем"""
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", data=login_data)

    assert response.status_code == 400
    data = response.json()
    assert "Invalid credentials" in data["detail"]


def test_get_current_user_info(client, auth_headers):
    """Тест получения информации о текущем пользователе"""
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_no_token(client):
    """Тест доступа без токена"""
    response = client.get("/auth/me")

    assert response.status_code == 401  # Unauthorized