from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import User
from app.security.password_utils import verify_password


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
