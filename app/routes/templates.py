from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from app.db.database import db

# настройка путей
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
template_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=template_dir)

router = APIRouter(tags=["templates"])

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "posts": db.posts})

@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    post = next((p for p in db.posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

@router.get("/edit/{post_id}", response_class=HTMLResponse)
async def edit_page(request: Request, post_id: int):
    post = next((p for p in db.posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})

@router.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request, "users": db.users})