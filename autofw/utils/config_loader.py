"""
简单的配置加载工具：
- 从项目根目录的 config.yml 里读取配置
- 支持通过环境变量 TEST_ENV 切换环境（默认 dev）
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

# 找到项目根目录下的 config.yml
# __file__ 是当前文件路径：.../autofw/utils/config_loader.py
# parents[2] -> pythonProject 目录
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yml"


def load_config() -> dict:
    """
        读取 config.yml，并根据 TEST_ENV 选择对应环境的配置。

        返回形如：
        {
            "env": "dev",
            "base_url": "https://postman-echo.com",
            "timeout": 10,
        }
        """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    default_env = raw.get("default_env", "dev")
    env_from_os = os.getenv("TEST_ENV")  # 可以通过系统环境变量覆盖
    env = env_from_os or default_env

    envs = raw.get("envs", {})
    env_cfg = envs.get(env)
    if not env_cfg:
        raise KeyError(f"环境 {env} 未在 config.yml 中的 envs 中配置")

    # 拼一个统一的 dict，顺便把 env 名字带上
    return {
        "env": env,
        **env_cfg,
    }
