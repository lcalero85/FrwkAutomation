from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime


class LoggerFactory:
    """Creates configured loggers for executions and modules."""

    _created_loggers: dict[str, logging.Logger] = {}

    @classmethod
    def create_logger(cls, name: str = "autotest_pro") -> logging.Logger:
        if name in cls._created_loggers:
            return cls._created_loggers[name]

        root_path = Path(__file__).resolve().parents[2]
        logs_path = root_path / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_name = f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(logs_path / file_name, encoding="utf-8")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._created_loggers[name] = logger
        return logger
