from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

from framework.core.actions import Actions
from framework.core.assertions import Assertions


class BasePage(Actions, Assertions):
    """Base class for all Page Objects."""

    def __init__(self, driver: WebDriver, base_url: str = "", timeout: int = 15) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        Actions.__init__(self, driver, timeout)
        Assertions.__init__(self, driver, timeout)

    def open_base(self) -> None:
        if not self.base_url:
            raise ValueError("Base URL is empty. Check environment configuration.")
        self.open(self.base_url)

    def current_url(self) -> str:
        return self.driver.current_url

    def title(self) -> str:
        return self.driver.title
