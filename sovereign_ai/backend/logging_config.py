"""
Structured logging configuration for the Sovereign AI Workbench.

Provides a JSON formatter for production and a human-readable
formatter for development.  Call ``setup_logging()`` once at
application startup.
"""

import logging
import sys
import json
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", json_output: bool = False) -> None:
    """
    Configure the root logger for the application.

    Parameters
    ----------
    log_level : str
        One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    json_output : bool
        If True use JSON lines; otherwise use a human-readable format.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Remove any existing handlers to avoid duplicate output
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)

    if json_output:
        console.setFormatter(JsonFormatter())
    else:
        console.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(console)

    # Suppress noisy third-party loggers
    for noisy in ("uvicorn.access", "chromadb", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
