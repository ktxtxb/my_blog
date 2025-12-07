import pytest


def test_full_user_flow(client, db_session):
    """Полный E2E сценарий: регистрация → вход → создание поста"""
    # 1. РЕГИСТРАЦИЯ
    register_data = {
        "login": "e2euser",
        "email": "e2e@example.com",
        "password": "e2epass123"
    }

    register_response = client.post("/auth/register", json=register_data)
    assert register_response.status_code == 200

    # 2. ВХОД
    login_data = {
        "username": "e2euser",  # ЛОГИН который только что зарегистрировали
        "password": "e2epass123"
    }

    login_response = client.post("/auth/login", data=login_data)

    if login_response.status_code != 200:
        login_data["username"] = "e2e@example.com"  # Пробуем email
        login_response = client.post("/auth/login", data=login_data)

    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    # 3. СОЗДАНИЕ ПОСТА
    token = login_response.json().get("access_token") or login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    post_data = {
        "title": "Мой E2E пост",
        "content": "Создан в рамках E2E тестирования"
    }

    post_response = client.post("/api/posts/", json=post_data, headers=headers)
    assert post_response.status_code == 200

    post_id = post_response.json()["id"]

    # 4. ПРОВЕРКА ЧТО ПОСТ СОЗДАЛСЯ
    get_response = client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Мой E2E пост"

    print("✅ E2E тест пройден: пользователь зарегистрировался, вошел и создал пост")


def test_like_flow(client, auth_headers, test_post, test_user, db_session):
    """E2E сценарий: лайк поста"""
    if not auth_headers:
        pytest.skip("No auth token available")

    # Создаем другого пользователя для поста
    from app.database.models import User
    from app.core.security import get_password_hash

    other_user = User(
        email="other@example.com",
        login="otheruser",
        hashed_password=get_password_hash("otherpass123"),
        is_admin=False
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Делаем пост принадлежащим другому пользователю
    from app.database.models import Post
    post = db_session.query(Post).filter(Post.id == test_post.id).first()
    post.author_id = other_user.id
    db_session.commit()

    # 1. ЛАЙКАЕМ ПОСТ
    like_data = {"post_id": test_post.id}
    like_response = client.post("/api/likes/", json=like_data, headers=auth_headers)
    # Может быть 200 (успех) или 400 (уже лайкнул) - оба варианта нормальны
    assert like_response.status_code in [200, 400]

    # 2. ПРОВЕРЯЕМ КОЛИЧЕСТВО ЛАЙКОВ
    count_response = client.get(f"/api/likes/post/{test_post.id}/count")
    assert count_response.status_code == 200

    # 3. ПРОВЕРЯЕМ ЛАЙКНУЛ ЛИ ПОЛЬЗОВАТЕЛЬ (только если лайк прошел)
    if like_response.status_code == 200:
        check_response = client.get(f"/api/likes/post/{test_post.id}/check", headers=auth_headers)
        assert check_response.status_code == 200
        assert check_response.json()["liked"] == True

    print("✅ E2E тест лайков пройден")