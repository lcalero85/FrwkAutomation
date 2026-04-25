from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    role: str | None = None
    permissions: list[str] = []


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str | None = None
    permissions: list[str] = []
    is_active: bool
