from loguru import logger
import os
import sys
from pathlib import Path

from .config import global_config


def _env_or(default: str, key: str) -> str:
    return os.getenv(key, default)


logger.remove()

adapter_level = _env_or(global_config.debug.level, "LOG_LEVEL")
mm_level = _env_or(getattr(global_config.debug, "maim_message_level", "INFO"), "LOG_MM_LEVEL")
serialize = bool(os.getenv("LOG_SERIALIZE", str(global_config.debug.serialize).lower()) in ("1", "true", "yes"))
backtrace = getattr(global_config.debug, "backtrace", False)
diagnose = getattr(global_config.debug, "diagnose", False)

common_fmt = (
    "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
mm_fmt = (
    "<red>{time:YYYY-MM-DD HH:mm:ss}</red> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# stderr sinks
logger.add(
    sys.stderr,
    level=adapter_level,
    format=common_fmt,
    backtrace=backtrace,
    diagnose=diagnose,
    filter=lambda r: "name" not in r["extra"] or r["extra"].get("name") != "maim_message",
)
logger.add(
    sys.stderr,
    level=mm_level,
    format=mm_fmt,
    backtrace=backtrace,
    diagnose=diagnose,
    filter=lambda r: r["extra"].get("name") == "maim_message",
)

# optional file sinks
if getattr(global_config.debug, "to_file", False):
    file_path = _env_or(getattr(global_config.debug, "file_path", "logs/telegram-adapter.log"), "LOG_FILE")
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    rotation = getattr(global_config.debug, "rotation", "10 MB")
    retention = getattr(global_config.debug, "retention", "7 days")
    logger.add(
        file_path,
        level=adapter_level,
        format=common_fmt,
        rotation=rotation,
        retention=retention,
        enqueue=True,
        encoding="utf-8",
        serialize=serialize,
        backtrace=backtrace,
        diagnose=diagnose,
        filter=lambda r: "name" not in r["extra"] or r["extra"].get("name") != "maim_message",
    )
    logger.add(
        file_path.replace(".log", ".mm.log"),
        level=mm_level,
        format=mm_fmt,
        rotation=rotation,
        retention=retention,
        enqueue=True,
        encoding="utf-8",
        serialize=serialize,
        backtrace=backtrace,
        diagnose=diagnose,
        filter=lambda r: r["extra"].get("name") == "maim_message",
    )

custom_logger = logger.bind(name="maim_message")
logger = logger.bind(name="MaiBot-Telegram-Adapter")
