import logging
from pathlib import Path


def init_aiogram_logging(file: Path | str | None = None, level: int = logging.INFO):
    handlers = []
    if file:
        handlers.append(logging.FileHandler(str(file), encoding="utf-8"))
    else:
        handlers.append(logging.NullHandler())

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
    )


def get_debug_logger(
    name: str = "debug", file: Path | str = "logs/debug.txt"
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.FileHandler(file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
