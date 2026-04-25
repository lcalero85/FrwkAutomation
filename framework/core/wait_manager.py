from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class WaitManager:
    """Centralized explicit waits."""

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.timeout = timeout

    @staticmethod
    def resolve_locator(selector: str, by: str | None = None) -> tuple[str, str]:
        if by:
            return by, selector
        selector = selector.strip()
        if selector.startswith("//") or selector.startswith("("):
            return By.XPATH, selector
        return By.CSS_SELECTOR, selector

    def visible(self, selector: str, by: str | None = None) -> WebElement:
        locator = self.resolve_locator(selector, by)
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(locator))

    def clickable(self, selector: str, by: str | None = None) -> WebElement:
        locator = self.resolve_locator(selector, by)
        return WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable(locator))

    def present(self, selector: str, by: str | None = None) -> WebElement:
        locator = self.resolve_locator(selector, by)
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))

    def all_present(self, selector: str, by: str | None = None) -> list[WebElement]:
        locator = self.resolve_locator(selector, by)
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_all_elements_located(locator))
