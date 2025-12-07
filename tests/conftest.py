import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.database.database import get_db
from app.database import models
from app.core.security import get_password_hash

# Тестовая БД в памяти
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создает новую сессию БД для каждого теста"""
    # Создаем таблицы
    models.Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Откатываем и закрываем
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент FastAPI"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя"""
    user = models.User(
        email="test@example.com",
        login="testuser",
        hashed_password=get_password_hash("testpass123"),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Получает токен авторизации для тестового пользователя"""
    login_data = {
        "username": "testuser",  # ЛОГИН пользователя
        "password": "testpass123"
    }

    response = client.post("/auth/login", data=login_data)

    # Дебаг
    if response.status_code != 200:
        print(f"DEBUG: Login failed. Status: {response.status_code}")
        print(f"DEBUG: Response: {response.text}")
        print(f"DEBUG: Trying with email instead...")

        # Пробуем с email
        login_data["username"] = "test@example.com"
        response = client.post("/auth/login", data=login_data)

    if response.status_code == 200:
        data = response.json()
        # Проверяем разные возможные ключи
        token = data.get("access_token") or data.get("token")
        if token:
            return {"Authorization": f"Bearer {token}"}

    print(f"ERROR: Cannot get auth token. Response: {response.text}")
    return {}


@pytest.fixture
def test_post(db_session, test_user):
    """Создает тестовый пост"""
    post = models.Post(
        author_id=test_user.id,
        title="Тестовый пост",
        content="Содержание тестового поста"
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post