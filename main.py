from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import json
import os
import webbrowser
import threading
import time

app = FastAPI(title="апи блога про селедку")

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=template_dir)

class User(BaseModel):
    email: str
    login: str
    password: str

class UserUpdate(BaseModel):
    email: str = None
    login: str = None
    password: str = None

class Post(BaseModel):
    authorId: int
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str = None
    content: str = None

users = []
posts = []
next_user_id = 1
next_post_id = 1
DATA_FILE = "blog_data.json"

def load_data():
    global users, posts, next_user_id, next_post_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            posts = data.get('posts', [])
            next_user_id = data.get('next_user_id', 1)
            next_post_id = data.get('next_post_id', 1)

def save_data():
    data = {
        'users': users,
        'posts': posts,
        'next_user_id': next_user_id,
        'next_post_id': next_post_id
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=str)

load_data()

if not users:
    users.append({
        "id": 1,
        "email": "admin@blog.com",
        "login": "admin",
        "password": "admin123",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    next_user_id = 2

if not posts:
    posts.append({
        "id": 1,
        "authorId": 1,
        "title": "первый тайтл при открытии",
        "content": "типо ваша первая запись",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    next_post_id = 2
    save_data()


@app.get("/posts/{post_id}")
async def view_post(request: Request, post_id: int):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return HTMLResponse("<h1>404 - Пост не найден</h1><p>Такого рецепта не существует</p><a href='/'>На главную</a>", status_code=404)
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

@app.get("/edit/{post_id}")
async def edit_page(request: Request, post_id: int):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return HTMLResponse("<h1>404 - Пост не найден</h1><p>Нельзя редактировать несуществующий рецепт</p><a href='/'>На главную</a>", status_code=404)
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})


@app.post("/api/users/")
async def create_user(user: User):
    global next_user_id
    for u in users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email уже используется")
    new_user = {
        "id": next_user_id,
        "email": user.email,
        "login": user.login,
        "password": user.password,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    users.append(new_user)
    next_user_id += 1
    save_data()
    return new_user

@app.get("/api/users/")
async def get_users():
    return users

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Пользователь не найден")

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate):
    for user in users:
        if user["id"] == user_id:
            if user_update.email:
                user["email"] = user_update.email
            if user_update.login:
                user["login"] = user_update.login
            if user_update.password:
                user["password"] = user_update.password
            user["updatedAt"] = datetime.now()
            save_data()
            return user
    raise HTTPException(status_code=404, detail="Пользователь не найден")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    global users
    users = [u for u in users if u["id"] != user_id]
    save_data()
    return {"message": "Пользователь удален"}

@app.post("/api/posts/")
async def create_post(post: Post):
    global next_post_id
    author_exists = any(u["id"] == post.authorId for u in users)
    if not author_exists:
        raise HTTPException(status_code=400, detail="Автор не найден")

    new_post = {
        "id": next_post_id,
        "authorId": post.authorId,
        "title": post.title,
        "content": post.content,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    posts.append(new_post)
    next_post_id += 1
    save_data()
    return new_post

@app.get("/api/posts/")
async def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
async def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="Пост не найден")

@app.put("/api/posts/{post_id}")
async def update_post(post_id: int, post_update: PostUpdate):
    for post in posts:
        if post["id"] == post_id:
            if post_update.title:
                post["title"] = post_update.title
            if post_update.content:
                post["content"] = post_update.content
            post["updatedAt"] = datetime.now()
            save_data()
            return post
    raise HTTPException(status_code=404, detail="Пост не найден")

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int):
    global posts
    posts = [p for p in posts if p["id"] != post_id]
    save_data()
    return {"message": "Пост удален"}

@app.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/create")
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request, "users": users})

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8001")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8001)