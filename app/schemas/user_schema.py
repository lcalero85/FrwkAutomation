from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role: str | None = None
    role_id: int | None = None
    is_active: bool


class UserCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role_id: int | None = None
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role_id: int | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
