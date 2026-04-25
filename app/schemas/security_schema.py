from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    username: str | None = None
    action: str
    module: str
    description: str | None = None
    ip_address: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
