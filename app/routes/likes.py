from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Like, Post, User
from app.schemas.likes import LikeCreate, LikeResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/likes", tags=["likes"])


@router.post("/", response_model=LikeResponse)
async def like_post(like: LikeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Проверяем существование поста
    post = db.query(Post).filter(Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    # Проверяем не лайкнул ли уже
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == like.post_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="Вы уже лайкнули этот пост")

    # Создаем лайк
    new_like = Like(
        user_id=current_user.id,
        post_id=like.post_id
    )

    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return LikeResponse(
        id=new_like.id,
        user_id=new_like.user_id,
        post_id=new_like.post_id,
        created_at=new_like.created_at
    )


@router.delete("/{post_id}")
async def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()

    if not like:
        raise HTTPException(status_code=404, detail="Лайк не найден")

    db.delete(like)
    db.commit()

    return {"message": "Лайк удален"}


@router.get("/post/{post_id}/count")
async def get_likes_count(post_id: int, db: Session = Depends(get_db)):
    count = db.query(Like).filter(Like.post_id == post_id).count()
    return {"post_id": post_id, "likes_count": count}


@router.get("/post/{post_id}/check")
async def check_user_like(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()

    return {"liked": like is not None}


# проверка тестовая
@router.get("/test")
async def test_likes():
    return {"message": "Likes router works!"}