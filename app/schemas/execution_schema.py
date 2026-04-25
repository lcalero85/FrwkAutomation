from pydantic import BaseModel, ConfigDict


class RunDemoRequest(BaseModel):
    browser: str = "chrome"
    headless: bool = False
    environment: str = "demo"
    test: str = "login_demo"
    report: str = "html,excel,pdf"


class RunRecordedCaseRequest(BaseModel):
    browser: str | None = None
    headless: bool = False
    environment: str = "recorded"
    base_url: str | None = None
    report: str = "html,excel,pdf"
    timeout: int = 15
    stop_on_failure: bool = True


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    html_path: str | None = None
    excel_path: str | None = None
    pdf_path: str | None = None


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execution_uid: str
    project_name: str
    suite_name: str
    test_name: str
    browser: str
    environment: str
    status: str
    duration_seconds: float
    total_steps: int
    passed_steps: int
    failed_steps: int
    skipped_steps: int
    success_percentage: float
    message: str | None = None
