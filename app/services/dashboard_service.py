from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Execution, Project, RecordedCase, Report, SchedulerJob, TestCase, TestSuite
from app.schemas.dashboard_schema import DashboardMetrics


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_metrics(self) -> DashboardMetrics:
        total_executions = self.db.query(Execution).count()
        passed = self.db.query(Execution).filter(Execution.status == "PASSED").count()
        failed = self.db.query(Execution).filter(Execution.status == "FAILED").count()
        skipped = self.db.query(Execution).filter(Execution.status == "SKIPPED").count()
        success = round((passed / total_executions) * 100, 2) if total_executions else 0.0
        avg_duration = self.db.query(func.avg(Execution.duration_seconds)).scalar() or 0
        last_execution = self.db.query(Execution).order_by(Execution.id.desc()).first()
        return DashboardMetrics(
            total_projects=self.db.query(Project).count(),
            active_projects=self.db.query(Project).filter(Project.status == "ACTIVE").count(),
            total_suites=self.db.query(TestSuite).count(),
            total_test_cases=self.db.query(TestCase).count(),
            total_recorded_cases=self.db.query(RecordedCase).count(),
            total_executions=total_executions,
            passed_executions=passed,
            failed_executions=failed,
            skipped_executions=skipped,
            success_percentage=success,
            total_reports=self.db.query(Report).count(),
            total_scheduler_jobs=self.db.query(SchedulerJob).count(),
            avg_duration_seconds=round(float(avg_duration), 2),
            last_execution_status=last_execution.status if last_execution else None,
        )
