from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.schemas.auth_schema import CurrentUserResponse, LoginRequest, TokenResponse
from app.schemas.security_schema import ChangePasswordRequest
from app.security.auth_utils import COOKIE_NAME, create_access_token, get_current_user, get_user_permissions
from app.security.password_utils import hash_password, verify_password
from app.services.audit_service import write_audit_log
from app.services.auth_service import authenticate_user

router = APIRouter(tags=["Authentication"])

# Simple in-memory protection for local MVP. For SaaS, replace with Redis-backed rate limit.
FAILED_LOGIN_ATTEMPTS: dict[str, list[datetime]] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 10


def _login_key(request: Request, username: str) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"{ip}:{username.lower()}"


def _is_locked(key: str) -> bool:
    now = datetime.utcnow()
    recent = [ts for ts in FAILED_LOGIN_ATTEMPTS.get(key, []) if now - ts < timedelta(minutes=LOCKOUT_MINUTES)]
    FAILED_LOGIN_ATTEMPTS[key] = recent
    return len(recent) >= MAX_FAILED_ATTEMPTS


def _register_failed_attempt(key: str) -> None:
    FAILED_LOGIN_ATTEMPTS.setdefault(key, []).append(datetime.utcnow())


def _clear_failed_attempts(key: str) -> None:
    FAILED_LOGIN_ATTEMPTS.pop(key, None)


@router.post("/auth/login", response_model=TokenResponse)
def api_login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    key = _login_key(request, payload.username)
    if _is_locked(key):
        write_audit_log(
            db,
            action="LOGIN_LOCKED",
            module="Authentication",
            username=payload.username,
            description="Login temporarily blocked by failed-attempt protection.",
            request=request,
            status="BLOCKED",
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Try again later.")

    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        _register_failed_attempt(key)
        write_audit_log(
            db,
            action="LOGIN_FAILED",
            module="Authentication",
            username=payload.username,
            description="Invalid username or password.",
            request=request,
            status="FAILED",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    _clear_failed_attempts(key)
    token = create_access_token(user.username)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8,
    )
    write_audit_log(
        db,
        action="LOGIN_SUCCESS",
        module="Authentication",
        user=user,
        description="User logged in successfully.",
        request=request,
        status="SUCCESS",
    )
    return TokenResponse(
        access_token=token,
        username=user.username,
        full_name=user.full_name,
        role=user.role.name if user.role else None,
        permissions=get_user_permissions(db, user),
    )


@router.get("/auth/me", response_model=CurrentUserResponse)
def api_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name if current_user.role else None,
        permissions=get_user_permissions(db, current_user),
        is_active=current_user.is_active,
    )


@router.post("/auth/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        write_audit_log(
            db,
            action="PASSWORD_CHANGE_FAILED",
            module="Security",
            user=current_user,
            description="Invalid current password.",
            request=request,
            status="FAILED",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    write_audit_log(
        db,
        action="PASSWORD_CHANGED",
        module="Security",
        user=current_user,
        description="User changed their password.",
        request=request,
        status="SUCCESS",
    )
    return {"message": "Password updated successfully"}


@router.post("/auth/logout")
def api_logout(request: Request, response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    write_audit_log(
        db,
        action="LOGOUT",
        module="Authentication",
        user=current_user,
        description="User logged out.",
        request=request,
        status="SUCCESS",
    )
    response.delete_cookie(COOKIE_NAME)
    return {"message": "Logged out"}
