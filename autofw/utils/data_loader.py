# 数据驱动工具
from pathlib import Path

import yaml

# 项目根目录： .../pythonProject
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def load_yaml(relative_path: str):
    """
    从 data 目录加载一个 YAML 文件内容。
    :param relative_path: 相对于 data/ 的路径，例如 "day07_login_cases.yml"
                          或 "day07/day07_login_cases.yml"
    :return: 解析后的 Python 对象（通常是 list[dict]）
    """
    path = DATA_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError("YAML 测试数据必须是列表 list")

    # 防止None
    return data or []
