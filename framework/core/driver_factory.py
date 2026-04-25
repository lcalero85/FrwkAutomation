from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

from framework.core.config_manager import ConfigManager
from framework.core.exceptions import BrowserNotSupportedError
from framework.logging.logger import LoggerFactory


class DriverFactory:
    """Creates Selenium WebDriver instances using project configuration."""

    def __init__(self, config: ConfigManager | None = None) -> None:
        self.config = config or ConfigManager()
        self.logger = LoggerFactory.create_logger(self.__class__.__name__)

    def create_driver(self, browser: str = "chrome", headless: bool | None = None) -> WebDriver:
        browser = browser.lower().strip()
        self.logger.info("Creating driver for browser=%s headless=%s", browser, headless)

        if browser == "chrome":
            driver = self._create_chrome(headless)
        elif browser == "firefox":
            driver = self._create_firefox(headless)
        elif browser == "edge":
            driver = self._create_edge(headless)
        else:
            raise BrowserNotSupportedError(f"Browser not supported: {browser}")

        browser_cfg = self.config.get_browser_config(browser)
        if browser_cfg.get("maximize", True):
            driver.maximize_window()
        else:
            width = int(browser_cfg.get("window_width", 1366))
            height = int(browser_cfg.get("window_height", 768))
            driver.set_window_size(width, height)

        return driver

    def _create_chrome(self, headless: bool | None) -> WebDriver:
        cfg = self.config.get_browser_config("chrome")
        options = ChromeOptions()
        use_headless = cfg.get("headless", False) if headless is None else headless
        if use_headless:
            options.add_argument("--headless=new")
        if cfg.get("incognito", False):
            options.add_argument("--incognito")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def _create_firefox(self, headless: bool | None) -> WebDriver:
        cfg = self.config.get_browser_config("firefox")
        options = FirefoxOptions()
        use_headless = cfg.get("headless", False) if headless is None else headless
        if use_headless:
            options.add_argument("--headless")
        if cfg.get("private", False):
            options.add_argument("-private")
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    def _create_edge(self, headless: bool | None) -> WebDriver:
        cfg = self.config.get_browser_config("edge")
        options = EdgeOptions()
        use_headless = cfg.get("headless", False) if headless is None else headless
        if use_headless:
            options.add_argument("--headless=new")
        if cfg.get("inprivate", False):
            options.add_argument("--inprivate")
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
