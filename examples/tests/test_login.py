from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

from examples.pages.login_page import LoginPage


def run_login_demo(driver: WebDriver, base_url: str, timeout: int = 15) -> None:
    page = LoginPage(driver, base_url=base_url, timeout=timeout)
    page.open_base()
    page.login("tomsmith", "SuperSecretPassword!")
    page.assert_success_login()
