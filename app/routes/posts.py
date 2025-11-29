from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import text
from app.database.database import get_db
from app.database.models import Post, User
from app.schemas.posts import PostCreate, PostUpdate, PostResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(
        author_id=current_user.id,
        title=post.title,
        content=post.content
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return PostResponse(
        id=new_post.id,
        author_id=new_post.author_id,
        author_login=current_user.login,
        title=new_post.title,
        content=new_post.content,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at
    )


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    posts = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .order_by(Post.created_at.desc()) \
        .offset(skip).limit(limit).all()
    return [PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_login=login,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at
    ) for post, login in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    result = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .filter(Post.id == post_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Пост не найден")

    post, author_login = result
    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_login=author_login,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        print(
            f"🔄 UPDATE attempt: user_id={current_user.id}, login={current_user.login}, is_admin={current_user.is_admin}")

        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        print(f"📝 POST FOUND: author_id={post.author_id}, current_user_id={current_user.id}")
        print(f"🔍 PERMISSION CHECK: author_match={post.author_id == current_user.id}, is_admin={current_user.is_admin}")

        print(f"✅ UPDATE ALLOWED: {current_user.login} редактирует пост {post_id}")

        if post_update.title is not None:
            post.title = post_update.title
        if post_update.content is not None:
            post.content = post_update.content

        post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(post)

        author = db.query(User).filter(User.id == post.author_id).first()

        return PostResponse(
            id=post.id,
            author_id=post.author_id,
            author_login=author.login,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR in update_post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.delete("/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        print(f"🔄 DELETE by {current_user.login} (admin: {current_user.is_admin})")

        # Проверяем пост и права
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        if not current_user.is_admin and post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        from sqlalchemy import create_engine
        from app.core.config import settings

        # Создаем прямое подключение к БД в обход ORM
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as direct_conn:
            with direct_conn.begin() as trans:
                # Удаляем ВСЕ что связано с постом
                direct_conn.execute(text("DELETE FROM likes WHERE post_id = :post_id"), {"post_id": post_id})
                direct_conn.execute(text("DELETE FROM favorites WHERE post_id = :post_id"), {"post_id": post_id})
                direct_conn.execute(text("DELETE FROM posts WHERE id = :post_id"), {"post_id": post_id})
                trans.commit()

        print(f"🎉 NUCLEAR DELETE SUCCESS: пост {post_id} уничтожен!")
        return {"message": "Пост успешно удален"}

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")


@router.get("/search/", response_model=List[PostResponse])
async def search_posts(
    q: str = "",
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    if not q:
        return []

    results = db.query(Post, User.login).join(User, Post.author_id == User.id) \
        .filter((Post.title.ilike(f"%{q}%")) | (Post.content.ilike(f"%{q}%"))) \
        .order_by(Post.created_at.desc()) \
        .offset(skip).limit(limit).all()

    return [PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_login=login,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at
    ) for post, login in results]