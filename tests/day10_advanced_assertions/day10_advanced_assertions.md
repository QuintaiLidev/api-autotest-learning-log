🧾 Day10 笔记：高级断言 + 统一数据驱动
1. 技术核心

（1）统一 GET / POST 的数据驱动用例

用 cases = [ {...}, {...} ] 这种统一结构驱动用例，每条 case 包含：

name: 用例名称（用于 ids）

method: "GET" 或 "POST"

path: 接口路径，比如 /get、/post

params: GET 查询参数（可选）

json: POST 请求体（可选）

expected_status: 期望 HTTP 状态码

expected_subset / expect_echo: 期望的响应体子集（可选）

用一个测试函数统一处理：

@pytest.mark.data_driven
@pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])
def test_unified_get_post(client, case):
    method = case["method"].upper()
    path = case["path"]
    params = case.get("params") or {}
    json_body = case.get("json") or {}
    expected_status = case["expected_status"]
    expect_echo = case.get("expect_echo")

    if method == "GET":
        resp = client.get(path, params=params)
    elif method == "POST":
        resp = client.post(path, json=json_body)
    else:
        pytest.fail(f"Unsupported method: {method}")

    assert resp.status_code == expected_status

    if expect_echo == "args":
        body = resp.json()
        # 校验 args 子集
    elif expect_echo == "json":
        body = resp.json()
        # 校验 json 子集


（2）高级断言：字典子集断言

在 autofw/utils/assertions.py 中实现类似：

def assert_dict_contains(expected_subset: dict, actual: dict):
    """
    断言 actual 至少包含 expected_subset 里的所有 key/value（支持嵌套）。
    """
    # 递归检查子集


用法：只关心“必须包含的那一部分”，不用对整个响应 body 做一模一样的对比：

expected = {
    "args": {"foo": "bar", "page": "1"}
}
assert_dict_contains(expected, body)


这个思想非常贴近真实项目的「容错 + 可维护」。

（3）网络异常的“优雅处理”

你已经遇到一堆：

ReadTimeout

SSLError: UNEXPECTED_EOF_WHILE_READING

ConnectionResetError

在 Day10 / Day11 中，你给关键用例加了保护：

import requests

try:
    resp = client.post(path, json=json_body)
except requests.exceptions.RequestException as e:
    pytest.skip(f"网络异常，跳过本用例：{e}")


含义：把“环境问题 / 外网不稳定”从“代码 bug”中剥离出来。
→ 这是很职业的自动化思路：框架要能识别“自身逻辑问题”和“外部依赖问题”。

2. Day10 可以怎么写进简历 / 面试 🎯

在个人 API 自动化练习项目中：

使用 pytest + requests 设计了统一的 数据驱动接口测试用例体系，支持 GET / POST 多 HTTP 方法，通过参数化用例结构（method、path、params/json、expected_status、expected_subset）实现一套代码驱动多场景测试。

编写了通用的 字典子集断言函数，用于校验复杂 JSON 响应中关键字段，提升用例可读性和可维护性。

为外部依赖（公共 API、网络波动）增加 网络异常兜底与用例跳过机制，区分框架自身逻辑错误与环境问题，使自动化结果更稳定可信。/