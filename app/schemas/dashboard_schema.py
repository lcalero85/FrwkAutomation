from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_projects: int
    total_suites: int
    total_test_cases: int
    total_executions: int
    passed_executions: int
    failed_executions: int
    success_percentage: float
