# autofw/utils/logging_helper.py
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# 项目根目录：.../pythonProject
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 日志目录：.../pythonProject/logs
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str = "autofw") -> logging.Logger:
    """
    获取一个全局可复用的 logger：
    - 同时输出到控制台和 logs/autofw.log 文件
    - 避免重复添加 handler（多次调用不会重复打日志）
    """
    logger = logging.getLogger(name)

    # ✅ 每次调用都保证 level / propagate 正确
    logger.setLevel(logging.INFO)

    # ✅ pytest 下打开 propagate，caplog 才能抓到
    is_pytest = ("PYTEST_CURRENT_TEST" in os.environ) or ("pytest" in sys.modules)
    logger.propagate = True if is_pytest else False

    # ✅ 避免重复添加 handler：用自定义标记
    if getattr(logger, "_autofw_configured", False):
        return logger

    # 日志格式：时间 等级 模块名 - 消息
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件输出
    log_file = LOG_DIR / "autofw.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger._autofw_configured = True
    return logger
