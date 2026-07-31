import logging
import sys
from app.config.settings import settings


def setup_logging() -> None:
    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )

    for logger_name in ("httpx", "httpcore", "urllib3", "motor"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)
