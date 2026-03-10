# utils/logger.py
# ── loguru 全局日志配置 ────────────────────────────────────────────────
import sys
import os
from loguru import logger as _logger

from config.settings import settings

# 移除 loguru 默认 handler，统一自定义
_logger.remove()

# ── 控制台 handler ────────────────────────────────────
_logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL.upper(),
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
    ),
    colorize=True,
)

# ── 文件 handler ──────────────────────────────────────
_log_dir = os.path.dirname(settings.LOG_FILE)
if _log_dir:
    os.makedirs(_log_dir, exist_ok=True)

_logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL.upper(),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
)


def get_logger(name: str):
    """返回绑定了模块名的 logger，用法：logger = get_logger(__name__)"""
    return _logger.bind(name=name)