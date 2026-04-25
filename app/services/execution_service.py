from __future__ import annotations

import argparse

from sqlalchemy.orm import Session

from app.database.models import Execution, ExecutionStep, Report
from app.schemas.execution_schema import RunDemoRequest
from framework.runners.cli_runner import CliRunner


class ExecutionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_executions(self) -> list[Execution]:
        return self.db.query(Execution).order_by(Execution.id.desc()).all()

    def get_execution(self, execution_id: int) -> Execution | None:
        return self.db.query(Execution).filter(Execution.id == execution_id).first()

    def run_demo(self, request: RunDemoRequest) -> Execution:
        args = argparse.Namespace(
            browser=request.browser,
            headless="true" if request.headless else "false",
            env=request.environment,
            test=request.test,
            timeout=None,
            report=request.report,
        )
        result = CliRunner().run(args)
        return self.persist_execution(result.summary, result.message, request.headless)

    def persist_execution(self, summary: dict, message: str, headless: bool) -> Execution:
        execution = Execution(
            execution_uid=summary.get("execution_id"),
            project_name=summary.get("project_name", "AutoTest Pro Framework"),
            suite_name=summary.get("suite_name", "Demo Suite"),
            test_name=summary.get("test_name", "login_demo"),
            execution_type="TEST_CASE",
            browser=summary.get("browser", "chrome"),
            environment=summary.get("environment", "demo"),
            base_url=summary.get("base_url"),
            headless=headless,
            status=summary.get("status", "UNKNOWN"),
            started_at=summary.get("started_at"),
            finished_at=summary.get("finished_at"),
            duration_seconds=summary.get("duration_seconds", 0),
            total_steps=summary.get("total_steps", 0),
            passed_steps=summary.get("passed_steps", 0),
            failed_steps=summary.get("failed_steps", 0),
            skipped_steps=summary.get("skipped_steps", 0),
            success_percentage=summary.get("success_percentage", 0),
            message=message,
        )
        self.db.add(execution)
        self.db.flush()

        for step in summary.get("steps", []):
            self.db.add(ExecutionStep(
                execution_id=execution.id,
                step_order=step.get("order", 0),
                name=step.get("name", ""),
                action=step.get("action", ""),
                selector=step.get("selector"),
                status=step.get("status", "UNKNOWN"),
                message=step.get("message"),
                screenshot_path=step.get("screenshot_path"),
                duration_seconds=step.get("duration_seconds", 0),
                error_detail=step.get("error_detail"),
            ))

        reports = summary.get("report_paths", {}) or {}
        self.db.add(Report(
            execution_id=execution.id,
            html_path=reports.get("html"),
            excel_path=reports.get("excel"),
            pdf_path=reports.get("pdf"),
        ))
        self.db.commit()
        self.db.refresh(execution)
        return execution
