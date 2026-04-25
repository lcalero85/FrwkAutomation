from __future__ import annotations

from pathlib import Path
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver


class ScreenshotUtils:
    """Screenshot helper utilities."""

    def __init__(self, screenshots_dir: str | Path = "screenshots") -> None:
        self.screenshots_dir = Path(screenshots_dir)
        if not self.screenshots_dir.is_absolute():
            self.screenshots_dir = Path.cwd() / self.screenshots_dir
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, driver: WebDriver, name: str = "screenshot") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)
        path = self.screenshots_dir / f"{safe_name}_{timestamp}.png"
        driver.save_screenshot(str(path))
        return str(path)
