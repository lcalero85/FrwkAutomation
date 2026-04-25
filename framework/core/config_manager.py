from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import yaml
from dotenv import load_dotenv


class ConfigManager:
    """Loads YAML and environment configuration for AutoTest Pro."""

    def __init__(self, root_path: Path | None = None) -> None:
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        load_dotenv(self.root_path / ".env")
        self.config = self._load_yaml(self.root_path / "config" / "config.yaml")
        self.browsers = self._load_yaml(self.root_path / "config" / "browsers.yaml")

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def get(self, key_path: str, default: Any = None) -> Any:
        current: Any = self.config
        for key in key_path.split("."):
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def get_browser_config(self, browser: str) -> dict[str, Any]:
        return self.browsers.get("browsers", {}).get(browser.lower(), {})

    def get_base_url(self, environment: str) -> str:
        envs = self.config.get("environments", {})
        return envs.get(environment, {}).get("base_url", "")

    def env(self, name: str, default: Any = None) -> Any:
        return os.getenv(name, default)
