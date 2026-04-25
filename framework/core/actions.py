from __future__ import annotations

import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

from framework.core.wait_manager import WaitManager
from framework.logging.logger import LoggerFactory
from framework.utils.screenshot_utils import ScreenshotUtils
from framework.reporting.models import execution_context


class Actions:
    """Safe Selenium actions with waits, logging, execution tracking and failure screenshots."""

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WaitManager(driver, timeout)
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)
        self.screenshot = ScreenshotUtils("screenshots")

    def _record_success(self, started: float, name: str, action: str, selector: str = "", message: str = "") -> None:
        execution_context.record_step(
            name=name,
            action=action,
            selector=selector,
            status="PASSED",
            message=message,
            duration_seconds=time.perf_counter() - started,
        )

    def _record_failure(self, started: float, name: str, action: str, selector: str, exc: Exception, screenshot_name: str) -> None:
        path = self.screenshot.capture(self.driver, screenshot_name)
        execution_context.record_step(
            name=name,
            action=action,
            selector=selector,
            status="FAILED",
            message="Action failed",
            screenshot_path=str(path),
            duration_seconds=time.perf_counter() - started,
            error_detail=str(exc),
        )
        self.logger.error("%s failed | selector=%s | screenshot=%s | error=%s", action, selector, path, exc)

    def open(self, url: str) -> None:
        started = time.perf_counter()
        try:
            self.logger.info("Opening URL: %s", url)
            self.driver.get(url)
            self._record_success(started, "Open URL", "open", url, "URL opened successfully")
        except Exception as exc:
            self._record_failure(started, "Open URL", "open", url, exc, "open_error")
            raise

    def click(self, selector: str) -> None:
        started = time.perf_counter()
        try:
            self.logger.info("Clicking selector: %s", selector)
            self.wait.clickable(selector).click()
            self._record_success(started, "Click element", "click", selector, "Click executed successfully")
        except Exception as exc:
            self._record_failure(started, "Click element", "click", selector, exc, "click_error")
            raise

    def double_click(self, selector: str) -> None:
        started = time.perf_counter()
        try:
            element = self.wait.clickable(selector)
            ActionChains(self.driver).double_click(element).perform()
            self._record_success(started, "Double click element", "double_click", selector)
        except Exception as exc:
            self._record_failure(started, "Double click element", "double_click", selector, exc, "double_click_error")
            raise

    def right_click(self, selector: str) -> None:
        started = time.perf_counter()
        try:
            element = self.wait.clickable(selector)
            ActionChains(self.driver).context_click(element).perform()
            self._record_success(started, "Right click element", "right_click", selector)
        except Exception as exc:
            self._record_failure(started, "Right click element", "right_click", selector, exc, "right_click_error")
            raise

    def type(self, selector: str, text: str, clear_first: bool = True) -> None:
        started = time.perf_counter()
        try:
            self.logger.info("Typing into selector: %s", selector)
            element = self.wait.visible(selector)
            if clear_first:
                element.clear()
            element.send_keys(text)
            safe_text = "***" if "password" in selector.lower() else text
            self._record_success(started, "Type text", "type", selector, f"Text entered: {safe_text}")
        except Exception as exc:
            self._record_failure(started, "Type text", "type", selector, exc, "type_error")
            raise

    def get_text(self, selector: str) -> str:
        started = time.perf_counter()
        try:
            text = self.wait.visible(selector).text
            self._record_success(started, "Get text", "get_text", selector, "Text obtained successfully")
            return text
        except Exception as exc:
            self._record_failure(started, "Get text", "get_text", selector, exc, "get_text_error")
            raise

    def get_attribute(self, selector: str, attribute: str) -> str | None:
        started = time.perf_counter()
        try:
            value = self.wait.present(selector).get_attribute(attribute)
            self._record_success(started, "Get attribute", "get_attribute", selector, f"Attribute: {attribute}")
            return value
        except Exception as exc:
            self._record_failure(started, "Get attribute", "get_attribute", selector, exc, "get_attribute_error")
            raise

    def exists(self, selector: str) -> bool:
        started = time.perf_counter()
        try:
            self.wait.present(selector)
            self._record_success(started, "Validate exists", "exists", selector, "Element exists")
            return True
        except Exception:
            execution_context.record_step(name="Validate exists", action="exists", selector=selector, status="FAILED", message="Element does not exist", duration_seconds=time.perf_counter() - started)
            return False

    def is_visible(self, selector: str) -> bool:
        started = time.perf_counter()
        try:
            self.wait.visible(selector)
            self._record_success(started, "Validate visible", "is_visible", selector, "Element is visible")
            return True
        except Exception:
            execution_context.record_step(name="Validate visible", action="is_visible", selector=selector, status="FAILED", message="Element is not visible", duration_seconds=time.perf_counter() - started)
            return False

    def scroll_to(self, selector: str) -> None:
        started = time.perf_counter()
        try:
            element = self.wait.present(selector)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self._record_success(started, "Scroll to element", "scroll_to", selector)
        except Exception as exc:
            self._record_failure(started, "Scroll to element", "scroll_to", selector, exc, "scroll_error")
            raise

    def hover(self, selector: str) -> None:
        started = time.perf_counter()
        try:
            element = self.wait.visible(selector)
            ActionChains(self.driver).move_to_element(element).perform()
            self._record_success(started, "Hover element", "hover", selector)
        except Exception as exc:
            self._record_failure(started, "Hover element", "hover", selector, exc, "hover_error")
            raise

    def upload_file(self, selector: str, file_path: str) -> None:
        started = time.perf_counter()
        try:
            self.wait.present(selector).send_keys(file_path)
            self._record_success(started, "Upload file", "upload_file", selector, "File uploaded successfully")
        except Exception as exc:
            self._record_failure(started, "Upload file", "upload_file", selector, exc, "upload_error")
            raise

    def select_by_visible_text(self, selector: str, text: str) -> None:
        started = time.perf_counter()
        try:
            Select(self.wait.visible(selector)).select_by_visible_text(text)
            self._record_success(started, "Select option", "select_by_visible_text", selector, f"Selected: {text}")
        except Exception as exc:
            self._record_failure(started, "Select option", "select_by_visible_text", selector, exc, "select_error")
            raise

    def execute_js(self, script: str, *args):
        started = time.perf_counter()
        try:
            result = self.driver.execute_script(script, *args)
            self._record_success(started, "Execute JavaScript", "execute_js", "javascript", "Script executed successfully")
            return result
        except Exception as exc:
            self._record_failure(started, "Execute JavaScript", "execute_js", "javascript", exc, "js_error")
            raise
