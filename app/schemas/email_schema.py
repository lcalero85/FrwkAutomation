from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmailRecipientPayload(BaseModel):
    recipients: str = Field(..., min_length=3, description="Correos separados por coma, punto y coma o salto de línea")
    subject: Optional[str] = Field(default=None, max_length=240)
    message: Optional[str] = Field(default=None, max_length=4000)
    include_html: bool = True
    include_excel: bool = True
    include_pdf: bool = True


class TestEmailPayload(BaseModel):
    recipient: EmailStr


class EmailSendResponse(BaseModel):
    success: bool
    message: str
    recipients: list[str] = []
    attachments: list[str] = []
