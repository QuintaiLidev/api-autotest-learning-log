# tests/day10_advanced_assertions/test_advanced_assertions.py

import pytest
import requests

from autofw.utils.data_loader import load_yaml
from autofw.utils.assertions import assert_status_code, assert_dict_contains

# 启动时一次性加载 YAML 用例
cases = load_yaml("day10_unified_cases.yml")


@pytest.mark.data_driven
@pytest.mark.assertions
@pytest.mark.parametrize(
    "case",
    cases,
    ids=[c["name"] for c in cases],
)
def test_unified_with_advanced_assertions(client, case):
    """
    Day10：在统一 GET/POST 的基础上，引入“期望响应体子集”的断言方式。

    - method: GET / POST
    - path:   接口路径
    - params: GET 查询参数
    - json:   POST 请求体
    - expected_status: 预期 HTTP 状态码
    - expected_subset: 预期响应体中必须包含的字段（子集）
    """
    method = case["method"].upper()
    path = case["path"]
    params = case.get("params") or {}
    json_body = case.get("json") or {}
    expected_status = case["expected_status"]
    expected_subset = case.get("expected_subset") or {}

    # 1. 发送请求(增加网络异常保护)
    try:
        if method == "GET":
            resp = client.get(path, params=params)
        elif method == "POST":
            resp = client.post(path, json=json_body)
        else:
            pytest.skip(f"暂不支持的方法: {method}")
    except requests.exceptions.RequestException as e:
        # ✅ 如果是公司网络/防火墙/外网问题，就优雅地跳过，不算你代码挂
        pytest.skip(f"网络异常，跳过本用例: {e}")

    # 2. 统一断言状态码
    assert_status_code(resp, expected_status)

    # 3. 如果没有配置 expected_subset，表示只关心状态码，直接返回
    if not expected_subset:
        return

    # 4. 尝试解析 JSON
    try:
        body = resp.json()
    except ValueError:
        pytest.fail(f"响应不是合法 JSON: {resp.text[:200]}")

    # 5. 使用我们封装的“字典包含断言”
    assert_dict_contains(body, expected_subset)
