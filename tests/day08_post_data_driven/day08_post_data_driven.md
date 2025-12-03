📝 Day08 Note：POST 接口的数据驱动测试
1. 今天我们到底干了什么？

目标：
把「POST 接口」的测试也变成 YAML 数据驱动，做到：

想加用例 → 只改 YAML，不动 Python 代码；

GET / POST 都统一走我们封装好的 APIClient 和 config.yml；

顺带踩一脚真实在线接口（postman-echo）的“坑”，学会根据接口行为调整断言。

2. 新增的核心文件 & 目录结构

大方向：所有“数据”都放 data/ 下，所有“代码”都放 autofw/ & tests/ 下。

1）数据加载工具

autofw/utils/data_loader.py（之前 Day07 已有，这里是继续复用）

核心功能：

从项目根目录出发，拼出 data/xxx.yml 的绝对路径；

帮你检查文件是否存在；

用 yaml.safe_load 读取出 Python 对象（通常是 list[dict]）。

典型实现思路（你现在文件里就是类似这样）：

from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

def load_yaml(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


2）YAML 测试数据

data/day08_post_cases.yml：

用列表形式存多条用例，每条是一个字典，比如：

- name: 空 body
  path: /post
  body: {}
  expected_status: 200

- name: 简单 JSON
  path: /post
  body:
    username: tom
    age: 20
  expected_status: 200


约定字段：

name：用例名（拿来做 ids，报告好看）

path：接口路径（拼在 base_url 后面）

body：POST 的 JSON 请求体

expected_status：预期的 HTTP 状态码

3）数据驱动的 POST 测试

tests/day08_post_data_driven/test_data_driven_post.py：

关键点：

import pytest
from autofw.utils.data_loader import load_yaml

# ① 模块加载时，就把 YAML 全部读进来
cases = load_yaml("day08_post_cases.yml")


@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",          # 测试函数里用的参数名
    cases,           # 传入的用例列表
    ids=[c["name"] for c in cases],  # 每条用例的显示名称
)
def test_data_driven_post(client, case):
    path = case["path"]
    body = case.get("body") or {}
    expected_status = case["expected_status"]

    # 发送 POST 请求
    resp = client.post(path, json=body)

    # 1) 断言状态码
    assert resp.status_code == expected_status

    # 2) 校验回显的 JSON
    resp_json = resp.json()
    echoed_json = resp_json.get("json")

    # ⚠ postman-echo 的特殊行为：
    #   当 body 是 {} 时，它返回的是 json: null（Python 里是 None）
    if body == {} and echoed_json is None:
        echoed_json = {}

    assert echoed_json == body


这里你学到了两个关键技巧：

数据驱动套路：

YAML → load_yaml → cases 列表 → @pytest.mark.parametrize("case", cases)

测试函数只围绕 case 写逻辑，新增用例只需要改 YAML。

对真实服务保持“弹性”断言：

理论上我们希望：发 {} → 回显 {}；

实际：postman-echo 对空 JSON 回显 null；

所以我们在断言前做了一层“修正逻辑”：

如果我们发的是 {}，而服务返回的是 None，就把 None 当成 {} 来对待。

这是很真实的“接口测试思维”：

不是死磕接口必须按你想象的行为来，而是在理解真实行为的前提下，合理设计断言。

3. 你在 Day08 解决的坑

坑 1：In test_data_driven_post: function uses no argument 'cases'

原因：@pytest.mark.parametrize("case", cases, ...) 时，测试函数参数名必须叫 case，不能叫 cases。

修复方式：保证

parametrize 的第一个参数 "case"

测试函数定义 def test_xxx(client, case):
两边保持一致。

坑 2：assert None == {}

原因：空 body 的情况下，resp_json["json"] 为 None，而 body 是 {}；

修复方式：在断言前，对这个特殊情况做一次转换：

if body == {} and echoed_json is None:
    echoed_json = {}
