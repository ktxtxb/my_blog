from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.schemas.posts import PostCreate, PostUpdate, PostResponse
from app.db.database import db

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate):
    # проверяем существование автора
    author_exists = any(u["id"] == post.author_id for u in db.users)
    if not author_exists:
        raise HTTPException(status_code=400, detail="Автор не найден")

    new_post = {
        "id": db.next_post_id,
        "author_id": post.author_id,
        "title": post.title,
        "content": post.content,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    db.posts.append(new_post)
    db.next_post_id += 1
    db.save_data()
    return PostResponse(**new_post)

@router.get("/", response_model=List[PostResponse])
async def get_posts():
    return [PostResponse(**post) for post in db.posts]

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    for post in db.posts:
        if post["id"] == post_id:
            return PostResponse(**post)
    raise HTTPException(status_code=404, detail="Пост не найден")

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate):
    for post in db.posts:
        if post["id"] == post_id:
            update_data = post_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    post[key] = value
            post["updated_at"] = datetime.now()
            db.save_data()
            return PostResponse(**post)
    raise HTTPException(status_code=404, detail="Пост не найден")

@router.delete("/{post_id}")
async def delete_post(post_id: int):
    initial_length = len(db.posts)
    db.posts = [p for p in db.posts if p["id"] != post_id]
    if len(db.posts) < initial_length:
        db.save_data()
        return {"message": "Пост удален"}
    raise HTTPException(status_code=404, detail="Пост не найден")