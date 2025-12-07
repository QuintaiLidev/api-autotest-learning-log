import pytest
from autofw.utils.data_loader import load_yaml
import requests
# 1)启动时一习性把 YAML 用例读进来
cases = load_yaml("day09_unified_cases.yml")


@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",
    cases,
    ids=[c["name"] for c in cases]
)
def test_unified_get_post(client, case):
    """
    用一套数据结构，统一驱动GET/POST 的测试。
    """
    method = case["method"].upper()
    path = case["path"]
    params = case.get("params") or {}
    json_body = case.get("json") or {}
    expected_status = case["expected_status"]
    expect_echo = case.get("expect_echo")

    # 2) 根据 method 选择 GET / POST
    if method == "GET":
        resp = client.get(path, params=params)
    elif method == "POST":
        resp = client.post(path, json=json_body)
    else:
        pytest.skip(f"暂不支持的方法: {method}")

    # 3) 断言状态码
    assert resp.status_code == expected_status

    # 4) 根据 expect_echo 决定如何校验响应体
    if not expect_echo:
        # 如果 YAML 没配置 expect_echo，就只校验状态码
        return

    resp_json = resp.json()

    if expect_echo == "args":
        # GET /get 的查询参数回显在 args
        echoed_args = resp_json.get("args",{})
        assert echoed_args == params

    elif expect_echo == "json":
        # POST /post 的 JSON 回显在 json 字段
        echoed_json = resp_json.get("json")

        # ⚠ postman-echo 对空 JSON 会返回 null（Python里是 None）
        if json_body == {} and echoed_json is None:
            echoed_json = {}

        assert echoed_json == json_body

    else:
        pytest.skip(f"暂不认识的expect_echo类型: {expect_echo}")

