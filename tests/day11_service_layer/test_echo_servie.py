# tests/day11_service_layer/test_echo_service.py
import pytest

from autofw.services.demo_echo_service import EchoService
from autofw.utils.assertions import assert_dict_contains, assert_status_code


@pytest.mark.service
@pytest.mark.smoke
def test_echo_get_with_params(client):
    """
    验证 Service 层 EchoService.get_with_params 是否能正确调用 /get：
    - 状态码 200
    - args 回显包含我们传入的查询参数
    """
    svc = EchoService(client)
    params = {"foo": "bar", "page": "1"}

    resp = svc.get_with_params(params)

    # 使用封装好的状态码断言
    assert_status_code(resp,200)

    body = resp.json()

    # 使用“字典子集断言”只关心 args 是否匹配

    expected = {
        "args": params
    }

    assert_dict_contains(body, expected)

