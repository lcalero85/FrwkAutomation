from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field

from framework.core.config_manager import ConfigManager
from framework.core.driver_factory import DriverFactory
from framework.logging.logger import LoggerFactory
from framework.utils.screenshot_utils import ScreenshotUtils
from framework.reporting.models import execution_context
from framework.reporting.report_builder import ReportBuilder
from examples.tests.test_login import run_login_demo


@dataclass
class ExecutionResult:
    status: str
    browser: str
    environment: str
    duration_seconds: float
    message: str
    reports: dict[str, str] = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


class CliRunner:
    """Console runner for AutoTest Pro Framework."""

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="AutoTest Pro Framework CLI Runner")
        parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "edge"], help="Browser to use")
        parser.add_argument("--headless", default="false", choices=["true", "false"], help="Run browser in headless mode")
        parser.add_argument("--env", default="demo", help="Environment name from config/config.yaml")
        parser.add_argument("--test", default="login_demo", help="Test name to execute")
        parser.add_argument("--timeout", default=None, type=int, help="Default explicit wait timeout")
        parser.add_argument("--report", default="html,excel,pdf", help="Report formats: html,excel,pdf")
        return parser

    def run(self, args: argparse.Namespace) -> ExecutionResult:
        started = time.perf_counter()
        browser = args.browser
        environment = args.env
        headless = args.headless.lower() == "true"
        timeout = args.timeout or int(self.config.get("execution.default_timeout", 15))
        base_url = self.config.get_base_url(environment)
        report_formats = [fmt.strip() for fmt in args.report.split(",") if fmt.strip()]

        if not base_url:
            raise ValueError(f"Environment '{environment}' does not have a configured base_url")

        execution_context.reset()
        execution_context.configure(
            project_name="AutoTest Pro Framework",
            suite_name="Demo Suite",
            test_name=args.test,
            browser=browser,
            environment=environment,
            base_url=base_url,
        )

        driver = None
        self.logger.info("Starting execution | test=%s browser=%s env=%s headless=%s", args.test, browser, environment, headless)

        try:
            driver = DriverFactory(self.config).create_driver(browser=browser, headless=headless)

            if args.test == "login_demo":
                run_login_demo(driver, base_url, timeout=timeout)
            else:
                raise ValueError(f"Unknown test: {args.test}")

            duration = round(time.perf_counter() - started, 2)
            summary = execution_context.finalize("PASSED")
            reports = ReportBuilder().generate(summary, report_formats)
            summary.report_paths = reports.__dict__
            self.logger.info("Execution finished successfully in %s seconds", duration)
            return ExecutionResult("PASSED", browser, environment, duration, "Execution completed successfully", reports.__dict__, summary.to_dict())

        except Exception as exc:
            duration = round(time.perf_counter() - started, 2)
            screenshot_path = ""
            if driver:
                screenshot_path = str(ScreenshotUtils("screenshots").capture(driver, "execution_failed"))
            self.logger.exception("Execution failed | screenshot=%s | error=%s", screenshot_path, exc)
            summary = execution_context.finalize("FAILED")
            reports = ReportBuilder().generate(summary, report_formats)
            summary.report_paths = reports.__dict__
            return ExecutionResult("FAILED", browser, environment, duration, str(exc), reports.__dict__, summary.to_dict())

        finally:
            if driver:
                driver.quit()
                self.logger.info("Browser closed")
