from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database.models import User, Post, favorites
from app.schemas.posts import PostResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("/{post_id}")
async def add_to_favorites(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Добавить пост в избранное"""
    # Проверяем существование поста
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    # Проверяем не добавлен ли уже
    existing_favorite = db.execute(
        favorites.select().where(
            favorites.c.user_id == current_user.id,
            favorites.c.post_id == post_id
        )
    ).first()

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Пост уже в избранном")

    # Добавляем в избранное
    db.execute(
        favorites.insert().values(
            user_id=current_user.id,
            post_id=post_id
        )
    )
    db.commit()

    return {"message": "Пост добавлен в избранное"}


@router.delete("/{post_id}")
async def remove_from_favorites(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Удалить пост из избранного"""
    result = db.execute(
        favorites.delete().where(
            favorites.c.user_id == current_user.id,
            favorites.c.post_id == post_id
        )
    )
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Пост не найден в избранном")

    return {"message": "Пост удален из избранного"}


@router.get("/", response_model=List[PostResponse])
async def get_favorite_posts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить избранные посты пользователя"""
    favorite_posts = db.query(Post, User.login).join(
        User, Post.author_id == User.id
    ).join(
        favorites, favorites.c.post_id == Post.id
    ).filter(
        favorites.c.user_id == current_user.id
    ).order_by(Post.created_at.desc()).all()

    return [
        PostResponse(
            id=post.id,
            author_id=post.author_id,
            author_login=login,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at
        ) for post, login in favorite_posts
    ]


@router.get("/check/{post_id}")
async def check_favorite(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Проверить, есть ли пост в избранном"""
    favorite = db.execute(
        favorites.select().where(
            favorites.c.user_id == current_user.id,
            favorites.c.post_id == post_id
        )
    ).first()

    return {"is_favorite": favorite is not None}