import sys
import os

# Импортируем твой код для coverage
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Импортируем твои модули
from app.core import security, config
from app.schemas import users, posts, likes
from app.database import models


def test_security_functions():
    """Тест функций безопасности"""
    password = "testpassword123"
    hashed = security.get_password_hash(password)
    assert security.verify_password(password, hashed) == True
    assert security.verify_password("wrongpass", hashed) == False


def test_pydantic_schemas():
    """Тест Pydantic схем"""
    # Тест создания пользователя
    user_data = {
        "login": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    user_schema = users.UserCreate(**user_data)
    assert user_schema.login == "testuser"

    # Тест создания поста
    post_data = {
        "title": "Тестовый пост",
        "content": "Содержание поста"
    }
    post_schema = posts.PostCreate(**post_data)
    assert post_schema.title == "Тестовый пост"


def test_models():
    """Тест моделей БД"""
    # Просто проверяем что модели можно импортировать
    assert hasattr(models, 'User')
    assert hasattr(models, 'Post')
    assert hasattr(models, 'Like')


def test_config():
    """Тест конфигурации"""
    assert hasattr(config.settings, 'DATABASE_URL')
    assert hasattr(config.settings, 'SECRET_KEY')


# Простые тесты из предыдущего файла
def test_basic():
    assert 1 + 1 == 2
    assert "hello" in "hello world"