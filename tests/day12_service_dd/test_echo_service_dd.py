# tests/day12_service_dd/test_echo_service_dd.py
import pytest

from autofw.services.demo_echo_service import EchoService
from autofw.utils.assertions import assert_dict_contains, assert_status_code

pytestmark = pytest.mark.network  # ✅ 整个模块默认都是 network


@pytest.mark.service
@pytest.mark.data_driven
@pytest.mark.smoke
def test_echo_get_with_params_basic(echo_service: EchoService):
    """
    Day12-01：基础版——跟 Day11 类似，但通过 echo_service fixture 来调用。
    """
    params = {"foo": "bar", "page": "1"}

    resp = echo_service.get_with_params(params)

    assert_status_code(resp, 200)

    body = resp.json()
    expected = {
        "args": params
    }
    assert_dict_contains(body, expected)


@pytest.mark.service
@pytest.mark.data_driven
@pytest.mark.parametrize(
    "params",
    [
        {"foo": "bar", "page": "1"},
        {"foo": "baz", "page": "2"},
        {"search": "api", "limit": "10"},
    ],
    ids=[
        "foo=bar,page=1",
        "foo=baz,page=2",
        "search=api,limit=10",
    ]
)
def test_echo_get_params_dd(echo_service: EchoService, params):
    """
    Day12-02：数据驱动版 Service 层用例。
    - 同一个业务动作 EchoService.get_with_params
    - 换不同参数，批量验证返回中的 args 回显是否正确
    """
    resp = echo_service.get_with_params(params)

    assert_status_code(resp, 200)

    body = resp.json()
    expected = {
        "args": params
    }
    assert_dict_contains(body, expected)


@pytest.mark.service
@pytest.mark.assertions
def test_echo_post_json_service(echo_service: EchoService):
    """
    Day12-03：Service 层 POST + 高级断言（字典子集）。
    """
    payload = {
        "user": {
            "id": 10086,
            "name": "Quintai-Li",
        },
        "meta": {
            "env": "dev",
        },
    }

    resp = echo_service.post_json(payload)

    assert_status_code(resp, 200)

    body = resp.json()

    # postman-echo 的 /post 会在 json 字段里回显请求体
    expected_subset = {
        "json": payload
    }

    # 我们只关心 body["json"] 是否包含 payload（全量匹配也 ok）
    assert_dict_contains(body, expected_subset)
