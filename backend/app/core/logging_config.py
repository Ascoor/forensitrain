import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging() -> None:
    """Configure application logging with rotation."""
    log_dir = os.getenv(
        "LOG_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs")),
    )
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
