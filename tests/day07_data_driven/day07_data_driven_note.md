Day07 笔记：数据驱动（一）—— YAML + 参数化 GET

目标：
✅ 学会把测试用例写进 YAML 数据文件
✅ 写一个通用 load_yaml() 工具
✅ 用 @pytest.mark.parametrize + YAML 数据，实现数据驱动测试
✅ 学会注册自定义 mark（data_driven）

1. 目录结构（新增部分）
pythonProject/
├─ data/
│  └─ day07_login_cases.yml          # Day07 用的测试数据
├─ autofw/
│  └─ utils/
│     ├─ config_loader.py
│     └─ data_loader.py              # 新增：加载 YAML
└─ tests/
   ├─ conftest.py
   └─ day07_data_driven/
      └─ test_data_driven_get.py     # 数据驱动用例

2. YAML 测试数据文件

文件：data/day07_login_cases.yml

示例内容（跟你现在项目里类似，可以根据自己实际版本调整）：

- name: 正常 GET 请求
  path: /get
  params:
    foo: bar
    hello: world
  expected_status: 200

- name: 访问 headers 接口
  path: /headers
  params: {}
  expected_status: 200


要点：

顶层是一个 列表 - ...，每个元素就是一条用例；

每条用例里包含固定字段：

name: 用例名（用来做测试 ID，方便报告里阅读）

path: 请求路径

params: 查询参数 dict（可以为空 {}）

expected_status: 期望状态码

⚠ 遇到过的坑：
YAML 解析错误 yaml.parser.ParserError
一般是：

缩进不对

顶层不是列表

前面多了奇怪的字符（比如复制时多了 >>> 之类）

3. 数据加载工具：autofw/utils/data_loader.py
# autofw/utils/data_loader.py
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def load_yaml(filename: str):
    """
    从 data 目录加载 YAML 测试数据，并返回 Python 对象（通常是 list）。
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError("YAML 测试数据必须是列表 list")

    return data


要点：

路径拼接统一从 DATA_DIR 开始，而不是测试里写死绝对路径。

对数据类型做了一层校验，避免 YAML 文件写错时默默出 bug。

4. 数据驱动测试用例：test_data_driven_get.py

文件：tests/day07_data_driven/test_data_driven_get.py

import pytest
from autofw.utils.data_loader import load_yaml

# 在模块加载时就把测试数据读出来
cases = load_yaml("day07_login_cases.yml")


@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",
    cases,
    ids=[c["name"] for c in cases]   # 用例名展示在报告上
)
def test_data_driven_get(client, case):
    """
    通过 YAML 数据驱动 GET 请求测试。
    """
    path = case["path"]
    params = case.get("params") or {}
    expected_status = case["expected_status"]

    resp = client.get(path, params=params)
    assert resp.status_code == expected_status


这里有几个关键点：

模块级加载数据

cases = load_yaml("day07_login_cases.yml")


Python 在导入这个 test 文件时就会读取 YAML，后面参数化直接用。

参数化

@pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])


case：每次参数化的一条用例 dict

ids：用来在测试报告 & 终端输出里显示「用例名」

结合 client fixture

依然复用 conftest.py 里的 client，和前面的框架融在一起了。

5. 自定义标记 data_driven 的注册

你有一个 warning：

PytestUnknownMarkWarning: Unknown pytest.mark.data_driven


解决方法：在 pytest.ini 里注册。

文件：pytest.ini

[pytest]
markers =
    smoke: 冒烟用例
    api: 接口相关用例
    config: 配置相关用例（环境切换、config.yml 等）
    data_driven: 数据驱动用例（从 YAML/JSON 读取测试数据）

# （下面是之前 day05 配置的 HTML 报告，可以保留）
htmlpath = reports/report.html
self_contained_html = True


注意别再写成 makers 了 🫠

这样就可以愉快地跑：

pytest -m data_driven


只执行数据驱动标签的用例。

6. Day07 遇到的典型错误 & 排查

ModuleNotFoundError: No module named 'autofw.utils.data_loader'

原因：data_loader.py 文件没放在 autofw/utils/ 下，或者没 __init__.py

解决：

确认 autofw/ 和 autofw/utils/ 目录下都有 __init__.py

文件路径为：autofw/utils/data_loader.py

FileNotFoundError: 测试数据文件不存在

原因：data/day07_login_cases.yml 路径/文件名不对

解决：确保：

目录名是 data/

文件名完全一致 day07_login_cases.yml

放在项目根目录下的 data/ 里，而不是测试目录下

YAML 解析错误：yaml.parser.ParserError

原因：YAML 格式非法：

顶层不是 - 开头的列表

缩进不统一

有不可见字符

排查方式：

用纯文本编辑器，重新手打一遍结构

确保每一行缩进是空格，不要 Tab

✅ Day07 结束时，你已经具备的能力

会写 通用的 YAML 数据加载工具

会用 pytest 的 参数化 + mark 做数据驱动测试

能把测试数据从代码中抽离出来，让用例更干净、更易扩展

能和前面 Day01–Day06 的：

APIClient

config.yml

client fixture
全部串联起来，形成一个「迷你接口自动化框架」。