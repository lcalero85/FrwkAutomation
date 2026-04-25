from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TemplateCreate(BaseModel):
    name: str
    template_type: str = Field(default="CASE", description="PROJECT, SUITE or CASE")
    category: str = "General"
    description: str | None = None
    priority: str = "MEDIUM"
    tags: str | None = None
    payload: dict[str, Any]
    is_system: bool = False


class TemplateUpdate(BaseModel):
    name: str | None = None
    template_type: str | None = None
    category: str | None = None
    description: str | None = None
    priority: str | None = None
    tags: str | None = None
    payload: dict[str, Any] | None = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    template_type: str
    category: str
    description: str | None = None
    priority: str
    tags: str | None = None
    payload: dict[str, Any]
    is_system: bool


class TemplateApplyRequest(BaseModel):
    project_name: str | None = None
    project_id: int | None = None
    suite_name: str | None = None
    base_url: str | None = None
    default_browser: str = "chrome"


class TemplateApplyResponse(BaseModel):
    message: str
    project_id: int | None = None
    suite_id: int | None = None
    recorded_case_id: int | None = None
    created_items: list[str] = []
