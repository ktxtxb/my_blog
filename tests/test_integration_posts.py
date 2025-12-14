import pytest


def test_create_post_authenticated(client, auth_headers):
    """Тест создания поста авторизованным пользователем"""
    # Пропускаем тест если нет авторизации
    if not auth_headers:
        pytest.skip("No auth token available")

    post_data = {
        "title": "Мой первый пост",
        "content": "Содержание моего первого поста"
    }

    response = client.post("/api/posts/", json=post_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Мой первый пост"
    assert data["author_login"] == "testuser"


def test_create_post_unauthenticated(client):
    """Тест создания поста без авторизации"""
    post_data = {
        "title": "Мой пост",
        "content": "Содержание"
    }

    response = client.post("/api/posts/", json=post_data)

    assert response.status_code == 401  # Unauthorized


def test_get_posts_list(client, test_post):
    """Тест получения списка постов"""
    response = client.get("/api/posts/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_single_post(client, test_post):
    """Тест получения одного поста"""
    response = client.get(f"/api/posts/{test_post.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_post.id
    assert data["title"] == "Тестовый пост"


def test_update_own_post(client, auth_headers, test_post, test_user, db_session):
    """Тест обновления своего поста"""
    if not auth_headers:
        pytest.skip("No auth token available")

    # Исправленный запрос - используем модель Post вместо строки
    from app.database.models import Post

    # Находим и обновляем пост
    post = db_session.query(Post).filter(Post.id == test_post.id).first()
    post.author_id = test_user.id
    db_session.commit()

    update_data = {
        "title": "Обновленный заголовок",
        "content": "Обновленное содержание"
    }

    response = client.put(f"/api/posts/{test_post.id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Обновленный заголовок"
    assert data["content"] == "Обновленное содержание"


def test_search_posts(client, test_post):
    """Тест поиска постов"""
    response = client.get("/api/posts/search/", params={"q": "Тестовый"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_posts_no_results(client):
    """Тест поиска постов (нет результатов)"""
    response = client.get("/api/posts/search/", params={"q": "несуществующийзапрос123"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0