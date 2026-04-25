from __future__ import annotations

import time
from selenium.webdriver.remote.webdriver import WebDriver
from framework.core.wait_manager import WaitManager
from framework.logging.logger import LoggerFactory
from framework.utils.screenshot_utils import ScreenshotUtils
from framework.reporting.models import execution_context


class Assertions:
    """Reusable assertions with logging, screenshots and report tracking."""

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WaitManager(driver, timeout)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)
        self.screenshot = ScreenshotUtils("screenshots")

    def assert_visible(self, selector: str, message: str | None = None) -> None:
        started = time.perf_counter()
        try:
            self.wait.visible(selector)
            self.logger.info("Assertion passed: visible %s", selector)
            execution_context.record_step(name="Assert visible", action="assert_visible", selector=selector, status="PASSED", message="Element is visible", duration_seconds=time.perf_counter() - started)
        except Exception as exc:
            path = self.screenshot.capture(self.driver, "assert_visible_error")
            error = message or f"Expected element to be visible: {selector}"
            execution_context.record_step(name="Assert visible", action="assert_visible", selector=selector, status="FAILED", message=error, screenshot_path=str(path), duration_seconds=time.perf_counter() - started, error_detail=str(exc))
            self.logger.error("%s | screenshot=%s | error=%s", error, path, exc)
            raise AssertionError(error) from exc

    def assert_text_contains(self, selector: str, expected_text: str) -> None:
        started = time.perf_counter()
        try:
            element = self.wait.visible(selector)
            actual = element.text
            assert expected_text in actual, f"Expected '{expected_text}' in '{actual}'"
            self.logger.info("Assertion passed: text contains '%s'", expected_text)
            execution_context.record_step(name="Assert text contains", action="assert_text_contains", selector=selector, status="PASSED", message=f"Expected text found: {expected_text}", duration_seconds=time.perf_counter() - started)
        except Exception as exc:
            path = self.screenshot.capture(self.driver, "assert_text_error")
            execution_context.record_step(name="Assert text contains", action="assert_text_contains", selector=selector, status="FAILED", message="Text assertion failed", screenshot_path=str(path), duration_seconds=time.perf_counter() - started, error_detail=str(exc))
            self.logger.error("Text assertion failed | screenshot=%s | error=%s", path, exc)
            raise

    def assert_url_contains(self, expected_text: str) -> None:
        started = time.perf_counter()
        current = self.driver.current_url
        if expected_text not in current:
            path = self.screenshot.capture(self.driver, "assert_url_error")
            execution_context.record_step(name="Assert URL contains", action="assert_url_contains", selector="current_url", status="FAILED", message=f"Expected URL to contain {expected_text}", screenshot_path=str(path), duration_seconds=time.perf_counter() - started, error_detail=f"Actual URL: {current}")
            self.logger.error("URL assertion failed | expected=%s | actual=%s | screenshot=%s", expected_text, current, path)
            raise AssertionError(f"Expected URL to contain '{expected_text}', actual '{current}'")
        execution_context.record_step(name="Assert URL contains", action="assert_url_contains", selector="current_url", status="PASSED", message=f"URL contains: {expected_text}", duration_seconds=time.perf_counter() - started)
        self.logger.info("Assertion passed: URL contains '%s'", expected_text)
