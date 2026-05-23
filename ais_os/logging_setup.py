"""Structured logging for AIS-OS runtime."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ais_os.config import get_config


def setup_logging(level: str | None = None) -> logging.Logger:
    cfg = get_config()
    log_level = (level or cfg.env.ais_log_level).upper()
    numeric = getattr(logging, log_level, logging.INFO)

    logs_dir: Path = cfg.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "ais-os.log"

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger("ais_os")
    root.setLevel(numeric)
    root.handlers.clear()

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(numeric)
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    return root
