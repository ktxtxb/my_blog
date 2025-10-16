import json
import os
from typing import Dict, List, Any
from datetime import datetime

DATA_FILE = "blog_data.json"


class Database:
    def __init__(self):
        self.users: List[Dict[str, Any]] = []
        self.posts: List[Dict[str, Any]] = []
        self.next_user_id = 1
        self.next_post_id = 1
        self.load_data()
        self.initialize_sample_data()

    def load_data(self) -> None:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.users = data.get("users", [])
                self.posts = data.get("posts", [])
                self.next_user_id = data.get("next_user_id", 1)
                self.next_post_id = data.get("next_post_id", 1)

    def save_data(self) -> None:
        data = {
            "users": self.users,
            "posts": self.posts,
            "next_user_id": self.next_user_id,
            "next_post_id": self.next_post_id,
        }
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, default=str, ensure_ascii=False, indent=2)

    def initialize_sample_data(self) -> None:
        if not self.users:
            self.users.append({
                "id": 1,
                "email": "admin@blog.com",
                "login": "admin",
                "password": "admin123",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            self.next_user_id = 2

        if not self.posts:
            self.posts.append({
                "id": 1,
                "author_id": 1,
                "title": "Добро пожаловать в блог про селедку!",
                "content": "Это ваша первая запись в блоге. Редактируйте или удаляйте её, и создавайте новые посты!",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            self.next_post_id = 2
            self.save_data()


# Глобальный экземпляр базы данных
db = Database()