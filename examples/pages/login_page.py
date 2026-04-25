from __future__ import annotations

from framework.core.base_page import BasePage


class LoginPage(BasePage):
    """Demo Page Object for https://the-internet.herokuapp.com/login."""

    USERNAME = "#username"
    PASSWORD = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    FLASH_MESSAGE = "#flash"
    SECURE_AREA = ".example h2"

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def assert_success_login(self) -> None:
        self.assert_url_contains("/secure")
        self.assert_text_contains(self.FLASH_MESSAGE, "You logged into a secure area")
        self.assert_visible(self.SECURE_AREA)
