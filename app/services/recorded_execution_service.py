from __future__ import annotations

import time
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import RecordedCase
from app.schemas.execution_schema import RunRecordedCaseRequest
from app.services.execution_service import ExecutionService
from framework.core.base_page import BasePage
from framework.core.driver_factory import DriverFactory
from framework.logging.logger import LoggerFactory
from framework.reporting.models import execution_context
from framework.reporting.report_builder import ReportBuilder


class RecordedExecutionService:
    """Executes recorded/manual-assisted cases as real Selenium tests."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)

    def run_recorded_case(self, case_id: int, request: RunRecordedCaseRequest):
        recorded_case = self.db.query(RecordedCase).filter(RecordedCase.id == case_id).first()
        if not recorded_case:
            return None
        if not recorded_case.steps:
            raise ValueError("Recorded case has no steps to execute.")

        browser = (request.browser or recorded_case.browser or "chrome").lower()
        environment = request.environment or "recorded"
        base_url = request.base_url or recorded_case.base_url or ""
        report_formats = request.report or "html,excel,pdf"
        headless = bool(request.headless)
        stop_on_failure = True if request.stop_on_failure is None else request.stop_on_failure

        execution_context.reset()
        execution_context.configure(
            project_name="AutoTest Pro Recorded",
            suite_name="Recorded Cases",
            test_name=recorded_case.name,
            browser=browser,
            environment=environment,
            base_url=base_url,
        )

        driver = None
        final_status = "PASSED"
        message = "Recorded case executed successfully."

        try:
            driver = DriverFactory().create_driver(browser=browser, headless=headless)
            page = BasePage(driver, base_url=base_url, timeout=request.timeout or 15)

            for step in sorted(recorded_case.steps, key=lambda item: item.step_order):
                try:
                    self._execute_step(page, recorded_case, step)
                except Exception as exc:
                    final_status = "FAILED"
                    message = f"Recorded case failed at step {step.step_order}: {exc}"
                    self.logger.error(message)
                    if stop_on_failure:
                        break
        except Exception as exc:
            final_status = "FAILED"
            message = f"Recorded execution failed: {exc}"
            self.logger.error(message)
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as exc:
                    self.logger.warning("Could not close browser cleanly: %s", exc)

        if any(step.status == "FAILED" for step in execution_context.steps):
            final_status = "FAILED"
        summary = execution_context.finalize(final_status)
        ReportBuilder().generate(summary, [fmt.strip() for fmt in report_formats.split(",") if fmt.strip()])

        return ExecutionService(self.db).persist_execution(summary.to_dict(), message, headless)

    def _execute_step(self, page: BasePage, recorded_case: RecordedCase, step) -> None:
        action = (step.action_type or "").lower().strip()
        selector = self._normalize_selector(step.selector_type, step.selector_value)
        value = step.input_value or ""

        if action in {"open", "navigate", "go_to"}:
            target_url = step.url or value or recorded_case.base_url
            if not target_url:
                raise ValueError("Open action requires a URL or case base_url.")
            page.open(target_url)
            return

        if action in {"click", "tap"}:
            page.click(selector)
            return

        if action == "double_click":
            page.double_click(selector)
            return

        if action in {"right_click", "context_click"}:
            page.right_click(selector)
            return

        if action in {"type", "write", "input", "send_keys"}:
            page.type(selector, value)
            return

        if action in {"assert_visible", "visible"}:
            page.assert_visible(selector)
            return

        if action in {"assert_text", "text_contains", "assert_text_contains"}:
            page.assert_text_contains(selector, value)
            return

        if action in {"assert_url", "assert_url_contains"}:
            expected = value or step.expected_result or ""
            if not expected:
                raise ValueError("assert_url action requires expected text in input_value.")
            page.assert_url_contains(expected)
            return

        if action in {"scroll", "scroll_to"}:
            page.scroll_to(selector)
            return

        if action == "hover":
            page.hover(selector)
            return

        if action in {"select", "select_by_visible_text"}:
            page.select_by_visible_text(selector, value)
            return

        if action in {"upload", "upload_file"}:
            page.upload_file(selector, value)
            return

        if action == "wait":
            seconds = self._safe_float(value, default=1.0)
            started = time.perf_counter()
            time.sleep(seconds)
            execution_context.record_step(
                name="Wait",
                action="wait",
                selector=str(seconds),
                status="PASSED",
                message=f"Waited {seconds} seconds",
                duration_seconds=time.perf_counter() - started,
            )
            return

        execution_context.record_step(
            name=f"Unsupported action: {step.action_type}",
            action=step.action_type or "unknown",
            selector=selector,
            status="SKIPPED",
            message="Action is not implemented in recorded case executor yet.",
            duration_seconds=0,
        )

    @staticmethod
    def _normalize_selector(selector_type: Optional[str], selector_value: Optional[str]) -> str:
        selector_type = (selector_type or "css").lower().strip()
        selector_value = (selector_value or "").strip()
        if selector_type == "id" and selector_value and not selector_value.startswith("#"):
            return f"#{selector_value}"
        if selector_type == "name" and selector_value and not selector_value.startswith("["):
            return f"[name='{selector_value}']"
        return selector_value

    @staticmethod
    def _safe_float(value: str, default: float = 1.0) -> float:
        try:
            return float(value)
        except Exception:
            return default
