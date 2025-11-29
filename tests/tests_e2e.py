import sys
import os

# Добавляем корень проекта в Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_basic():
    """Простой тест без TestClient"""
    print("🧪 ПРОСТОЙ E2E ТЕСТ...")

    # Проверка импортов модулей
    try:
        from main import app
        print("✅ main.py импортирован успешно")

        # Проверка подключения роутеров
        routes = [route.path for route in app.routes]
        print(f"✅ Найдено {len(routes)} маршрутов")

        # Основные маршруты
        main_routes = ["/", "/health", "/auth/login", "/api/posts/"]
        for route in main_routes:
            if any(route in r.path for r in app.routes if hasattr(r, 'path')):
                print(f"{route} - доступен")
            else:
                print(f"{route} - не найден")

        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def test_imports():
    """Проверяем что все модули импортируются"""
    print("\n🔍 ПРОВЕРКА ИМПОРТОВ...")

    modules_to_check = [
        "app.routes.users",
        "app.routes.posts",
        "app.routes.auth",
        "app.routes.likes",
        "app.routes.favorites",
        "app.database.models",
        "app.core.config",
        "app.core.security"
    ]

    all_imported = True
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"{module_name}")
        except ImportError as e:
            print(f"{module_name}: {e}")
            all_imported = False

    return all_imported


def test_database_models():
    """Проверяем модели БД"""
    print("\n🗄️  ПРОВЕРКА МОДЕЛЕЙ БД...")

    try:
        from app.database.models import User, Post, Like
        print("Модели User, Post, Like импортированы")

        # Проверяем атрибуты
        user_attrs = ['id', 'email', 'login', 'hashed_password']
        post_attrs = ['id', 'title', 'content', 'author_id']

        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"User.{attr} - есть")
            else:
                print(f"User.{attr} - нет")

        return True

    except Exception as e:
        print(f"Ошибка моделей: {e}")
        return False


def test_schemas():
    """Проверяем Pydantic схемы"""
    print("\n📋 ПРОВЕРКА СХЕМ...")
    try:
        from app.schemas.users import UserCreate, UserResponse
        from app.schemas.posts import PostCreate, PostResponse
        from app.schemas.likes import LikeCreate

        schemas = [UserCreate, UserResponse, PostCreate, PostResponse, LikeCreate]
        print(f"   ✅ {len(schemas)} схем импортированы")
        return True

    except Exception as e:
        print(f"   ❌ Ошибка схем: {e}")
        return False


def run_all_checks():
    """Запускаем все проверки"""
    print("🚀 ЗАПУСК ПРОВЕРОК ПРОЕКТА...")
    print("=" * 50)

    checks = [
        test_imports,
        test_database_models,
        test_schemas,
        test_basic
    ]
    passed = 0
    total = len(checks)

    for check in checks:
        try:
            if check():
                passed += 1
            print("")
        except Exception as e:
            print(f"💥 Проверка упала: {e}\n")

    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {passed}/{total} проверок пройдено")

    if passed == total:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к работе.")
        print("\n📝 ЧТО ДАЛЬШЕ:")
        print("1. Запустите: python main.py")
        print("2. Откройте: http://127.0.0.1:8001")
        print("3. Проверьте что сайт работает")
    else:
        print("⚠️  Некоторые проверки не прошли")

    return passed == total


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)