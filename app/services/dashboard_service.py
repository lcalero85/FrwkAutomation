from sqlalchemy.orm import Session

from app.database.models import Execution, Project, TestCase, TestSuite
from app.schemas.dashboard_schema import DashboardMetrics


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_metrics(self) -> DashboardMetrics:
        total_executions = self.db.query(Execution).count()
        passed = self.db.query(Execution).filter(Execution.status == "PASSED").count()
        failed = self.db.query(Execution).filter(Execution.status == "FAILED").count()
        success = round((passed / total_executions) * 100, 2) if total_executions else 0.0
        return DashboardMetrics(
            total_projects=self.db.query(Project).count(),
            total_suites=self.db.query(TestSuite).count(),
            total_test_cases=self.db.query(TestCase).count(),
            total_executions=total_executions,
            passed_executions=passed,
            failed_executions=failed,
            success_percentage=success,
        )
