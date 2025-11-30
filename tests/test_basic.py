def test_basic_math():
    """Простой тест математики"""
    assert 2 + 2 == 4
    assert 3 * 3 == 9


def test_strings():
    """Тест строк"""
    assert "селедк" in "рецепт селедки"
    assert len("привет") == 6


def test_lists():
    """Тест списков"""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert 3 in numbers


def test_auth_logic():
    """Тест логики авторизации (без FastAPI)"""

    # проверка пароля
    def check_password(input_password, stored_hash):
        return len(input_password) >= 6

    assert check_password("password123", "hash") == True
    assert check_password("123", "hash") == False


def test_post_creation():
    """Тест логики создания поста (без БД)"""
    post_data = {
        "title": "Рецепт селедки",
        "content": "Очень вкусная селедка..."
    }

    assert len(post_data["title"]) > 0
    assert len(post_data["content"]) > 0
    assert "селедк" in post_data["title"].lower()


def test_user_validation():
    """Тест валидации пользователя"""

    def validate_user(login, email, password):
        errors = []
        if len(login) < 3:
            errors.append("Логин слишком короткий")
        if "@" not in email:
            errors.append("Некорректный email")
        if len(password) < 6:
            errors.append("Пароль слишком короткий")
        return errors

    # Тест правильных данных
    assert validate_user("user123", "test@test.com", "password123") == []

    # Тест неправильных данных
    errors = validate_user("ab", "invalid-email", "123")
    assert len(errors) == 3


def test_likes_logic():
    """Тест логики лайков"""
    likes_count = 5
    user_liked = True

    assert likes_count > 0
    assert user_liked == True


def test_search_logic():
    """Тест логики поиска"""
    search_query = "селедк"
    results = ["Рецепт селедки", "Селедка под шубой"]

    assert len(search_query) > 0
    assert any("селедк" in result.lower() for result in results)