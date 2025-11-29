from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database.models import User
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        login=current_user.login,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Только админ может видеть всех пользователей
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            login=user.login,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")

    if db.query(User).filter(User.login == user.login).first():
        raise HTTPException(status_code=400, detail="Логин уже используется")

    # Создаем пользователя
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        login=user.login,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        login=new_user.login,
        is_admin=new_user.is_admin,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponse(
        id=user.id,
        email=user.email,
        login=user.login,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем поля
    if user_update.email is not None:
        # Проверяем уникальность email
        existing_user = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже используется")
        user.email = user_update.email

    if user_update.login is not None:
        # Проверяем уникальность логина
        existing_user = db.query(User).filter(User.login == user_update.login, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Логин уже используется")
        user.login = user_update.login

    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)

    # Только админ может менять is_admin
    if user_update.is_admin is not None and current_user.is_admin:
        user.is_admin = user_update.is_admin

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        login=user.login,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Только админ может удалять пользователей
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Нельзя удалить себя
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")

    db.delete(user)
    db.commit()
    return {"message": "Пользователь удален"}


@router.get("/search/", response_model=List[UserResponse])
async def search_users(
        q: str = "",
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Поиск пользователей по логину и email"""
    if not q:
        return []

    users = db.query(User).filter(
        (User.login.ilike(f"%{q}%")) |
        (User.email.ilike(f"%{q}%"))
    ).offset(skip).limit(limit).all()

    return [
        UserResponse(
            id=user.id,
            email=user.email,
            login=user.login,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]