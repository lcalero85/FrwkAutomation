from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BrowserRecordedEventIn(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=80)
    action_type: Optional[str] = Field(None, max_length=80)
    selector_type: Optional[str] = Field("css", max_length=40)
    selector_value: Optional[str] = None
    alternative_selector: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    tag: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None


class BrowserRecorderStatusOut(BaseModel):
    recorded_case_id: int
    total_steps: int
    last_event_type: Optional[str] = None
    last_event_at: Optional[datetime] = None
    message: str


class BrowserRecorderInstructionOut(BaseModel):
    recorded_case_id: int
    ingest_url: str
    extension_path: str
    instructions: list[str]
