from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.db.database import db
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # проверяем уникальность email
    for u in db.users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email уже используется")

    new_user = {
        "id": db.next_user_id,
        "email": user.email,
        "login": user.login,
        "password": user.password,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    db.users.append(new_user)
    db.next_user_id += 1
    db.save_data()
    return UserResponse(**new_user)


@router.get("/", response_model=List[UserResponse])
async def get_users():
    return [UserResponse(**user) for user in db.users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    for user in db.users:
        if user["id"] == user_id:
            return UserResponse(**user)
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    for user in db.users:
        if user["id"] == user_id:
            update_data = user_update.dict(exclude_unset=True)

            if 'email' in update_data:
                for u in db.users:
                    if u["email"] == update_data['email'] and u["id"] != user_id:
                        raise HTTPException(status_code=400, detail="Email уже используется")

            for key, value in update_data.items():
                if value is not None:
                    user[key] = value
            user["updated_at"] = datetime.now()
            db.save_data()
            return UserResponse(**user)
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    initial_length = len(db.users)
    db.users = [u for u in db.users if u["id"] != user_id]
    if len(db.users) < initial_length:
        db.save_data()
        return {"message": "Пользователь удален"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")