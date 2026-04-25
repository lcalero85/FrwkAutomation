from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordedCaseCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=180)
    description: Optional[str] = None
    project_id: Optional[int] = None
    suite_id: Optional[int] = None
    base_url: Optional[str] = None
    browser: str = "chrome"
    status: str = "DRAFT"


class RecordedCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    suite_id: Optional[int] = None
    base_url: Optional[str] = None
    browser: Optional[str] = None
    status: Optional[str] = None


class RecordedStepCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    action_type: str = Field(..., min_length=2, max_length=80)
    selector_type: Optional[str] = "css"
    selector_value: Optional[str] = None
    alternative_selector: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None


class RecordedStepUpdate(BaseModel):
    step_order: Optional[int] = Field(None, ge=1)
    action_type: Optional[str] = None
    selector_type: Optional[str] = None
    selector_value: Optional[str] = None
    alternative_selector: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None


class RecordedStepOut(BaseModel):
    id: int
    recorded_case_id: int
    step_order: int
    action_type: str
    selector_type: Optional[str] = None
    selector_value: Optional[str] = None
    alternative_selector: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordedCaseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    suite_id: Optional[int] = None
    base_url: Optional[str] = None
    browser: str
    status: str
    created_at: datetime
    updated_at: datetime
    steps: list[RecordedStepOut] = []

    model_config = {"from_attributes": True}


class SelectorSuggestionRequest(BaseModel):
    element_id: Optional[str] = None
    name: Optional[str] = None
    data_testid: Optional[str] = None
    aria_label: Optional[str] = None
    tag: Optional[str] = None
    text: Optional[str] = None
    css: Optional[str] = None
    xpath: Optional[str] = None


class SelectorSuggestionOut(BaseModel):
    selector_type: str
    selector_value: str
    priority: int
    reason: str


class GeneratedCodeOut(BaseModel):
    recorded_case_id: int
    code: str


class BrowserRecordedEventIn(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=80)
    action_type: Optional[str] = None
    selector_type: Optional[str] = "css"
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


class BrowserRecorderInstructionOut(BaseModel):
    recorded_case_id: int
    ingest_url: str
    extension_path: str
    instructions: list[str]


class BrowserRecorderStatusOut(BaseModel):
    recorded_case_id: int
    total_steps: int
    last_event_type: Optional[str] = None
    last_event_at: Optional[datetime] = None
    last_step_summary: Optional[str] = None
    message: str


class RecorderCleanupOut(BaseModel):
    recorded_case_id: int
    before_steps: int
    after_steps: int
    removed_steps: int
    message: str


class RecordedCaseExportPreviewOut(BaseModel):
    recorded_case_id: int
    case_name: str
    page_object_filename: str
    test_filename: str
    readme_filename: str
    page_object_code: str
    test_code: str
    readme: str


class RecordedCaseExportOut(BaseModel):
    recorded_case_id: int
    case_name: str
    export_folder: str
    zip_path: str
    zip_filename: str
    files: list[str]
    created_at: datetime
    message: str
