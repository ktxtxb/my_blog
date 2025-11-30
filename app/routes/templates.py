from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Post, User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    posts_with_authors = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .order_by(Post.created_at.desc()).all()

    posts = []
    for post, author_login in posts_with_authors:
        post_dict = {
            'id': post.id,
            'author_id': post.author_id,
            'author_login': author_login,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at,
            'updated_at': post.updated_at
        }
        posts.append(post_dict)

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@router.get("/create", response_class=HTMLResponse)
async def create_post_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("create.html", {"request": request, "users": users})


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def read_post(request: Request, post_id: int, db: Session = Depends(get_db)):

    result = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .filter(Post.id == post_id).first()

    if not result:
        return templates.TemplateResponse("post.html", {"request": request, "post": None, "error": "Пост не найден"})

    post, author_login = result

    post_data = {
        'id': post.id,
        'author_id': post.author_id,
        'author_login': author_login,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'updated_at': post.updated_at
    }

    return templates.TemplateResponse("post.html", {"request": request, "post": post_data})


@router.get("/edit/{post_id}", response_class=HTMLResponse)
async def edit_post_page(request: Request, post_id: int, db: Session = Depends(get_db)):
    result = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .filter(Post.id == post_id).first()

    if not result:
        return templates.TemplateResponse("edit.html", {"request": request, "post": None, "error": "Пост не найден"})

    post, author_login = result
    post_data = {
        'id': post.id,
        'author_id': post.author_id,
        'author_login': author_login,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at,
        'updated_at': post.updated_at
    }

    return templates.TemplateResponse("edit.html", {"request": request, "post": post_data})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    posts = []

    if q:
        # Используем существующую функцию поиска
        from app.routes.posts import search_posts
        search_results = await search_posts(q=q, db=db)
        posts = [
            {
                'id': post.id,
                'author_id': post.author_id,
                'author_login': post.author_login,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at,
                'updated_at': post.updated_at
            }
            for post in search_results
        ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": posts,
            "search_query": q
        }
    )