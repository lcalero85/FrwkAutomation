from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_projects: int
    active_projects: int = 0
    total_suites: int
    total_test_cases: int
    total_recorded_cases: int = 0
    total_executions: int
    passed_executions: int
    failed_executions: int
    skipped_executions: int = 0
    success_percentage: float
    total_reports: int = 0
    total_scheduler_jobs: int = 0
    avg_duration_seconds: float = 0
    last_execution_status: str | None = None
