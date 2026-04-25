from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SchedulerJobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    execution_type: str = "DEMO"
    browser: str = "chrome"
    environment: str = "demo"
    report: str = "html,excel,pdf"
    headless: bool = True
    schedule_type: str = "DAILY"
    cron_expression: Optional[str] = None
    run_at: Optional[str] = None
    next_run: Optional[str] = None
    is_active: bool = True


class SchedulerJobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    browser: Optional[str] = None
    environment: Optional[str] = None
    report: Optional[str] = None
    headless: Optional[bool] = None
    schedule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    run_at: Optional[str] = None
    next_run: Optional[str] = None
    is_active: Optional[bool] = None


class SchedulerJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    execution_type: str
    browser: str
    environment: str
    report: str
    headless: bool
    schedule_type: str
    cron_expression: Optional[str] = None
    run_at: Optional[str] = None
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    last_status: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
