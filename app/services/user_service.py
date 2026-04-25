from __future__ import annotations

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database.models import Role, User
from app.schemas.user_schema import UserCreateRequest, UserUpdateRequest
from app.security.password_utils import hash_password


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "username": user.username,
        "role": user.role.name if user.role else None,
        "role_id": user.role_id,
        "is_active": user.is_active,
    }


def list_users(db: Session) -> list[dict]:
    return [serialize_user(user) for user in db.query(User).order_by(User.id.desc()).all()]


def list_roles(db: Session) -> list[dict]:
    roles = db.query(Role).order_by(Role.name.asc()).all()
    return [{"id": role.id, "name": role.name, "description": role.description} for role in roles]


def create_user(db: Session, payload: UserCreateRequest) -> dict:
    existing = db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    user = User(
        full_name=payload.full_name,
        email=str(payload.email),
        username=payload.username,
        password_hash=hash_password(payload.password),
        role_id=payload.role_id,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


def update_user(db: Session, user_id: int, payload: UserUpdateRequest) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data and data["full_name"] is not None:
        user.full_name = data["full_name"]
    if "email" in data and data["email"] is not None:
        user.email = str(data["email"])
    if "role_id" in data:
        user.role_id = data["role_id"]
    if "is_active" in data and data["is_active"] is not None:
        user.is_active = data["is_active"]
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])

    db.commit()
    db.refresh(user)
    return serialize_user(user)
