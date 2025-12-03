# tests/day07_data_driven/test_data_driven_get.py

import pytest

from autofw.utils.data_loader import load_yaml

# 这里直接加载data目录下的yaml文件
cases = load_yaml("day07_login_cases.yml")


@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",
    cases,
    ids=[c["name"] for c in cases],  ## 用 YAML 里的 name 做用例名称
)
def test_get_with_query_params(client, case):
    """
    使用 data/day07_login_cases.yml 中的用例数据，数据驱动 GET 请求测试
    """
    path = case["path"]
    params = case.get("params") or {}
    expected_status = case["expected_status"]
    expected_args = case.get("expected_args") or {}

    # client 来自 tests/conftest.py，会自动用 config.yml 的 base_url
    resp = client.get(path, params=params)

    # 1.校验状态码
    assert resp.status_code == expected_status

    body = resp.json()

    # 2. postman-echo.com/get 会把 query 参数放在 args 字段中
    args = body.get("args", {})

    # 3. 逐个字段校验期望的参数是否在回显中
    for key, value in expected_args.items():
        assert args.get(key) == value
