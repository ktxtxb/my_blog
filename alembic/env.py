from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# добавляем путь к проекту, чтобы Python нашел наши файлы
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# импортируем наши модели и настройки
from app.database.models import Base
from app.core.config import settings

config = context.config

# настраиваем логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# отслеживаемые модели
target_metadata = Base.metadata

def get_url():
    """получаем URL базы данных из настроек"""
    return settings.DATABASE_URL

def run_migrations_offline():
    """запуск миграций без подключения к БД (для тестов)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Запуск миграций с подключением к БД"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    # Подключаемся к БД
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# Запускаем миграции в правильном режиме
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()