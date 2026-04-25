from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
