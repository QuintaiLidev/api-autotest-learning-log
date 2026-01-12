# tests/day16_retry_transport/test_retry_transport.py
import pytest
import requests

from autofw.utils.assertions import assert_json_value, assert_status_code
from tests.day15_mocking.test_echo_service_mocked import build_response


@pytest.mark.retry
@pytest.mark.mock
def test_retry_then_success(echo_service, monkeypatch):
    """
    第一次请求超时，第二次成功：
    - 验证重试机制生效
    - 验证最终返回可正常做断言
    """
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.exceptions.ReadTimeout("boom timeout once")
        body = {"json": {"user": {"id": 10086}}, "url": url}
        return build_response(200, body, url=url)

    monkeypatch.setattr(echo_service.client.session, "request", fake_request)

    # 走 service -> client.get/post 都行，这里用 post 更贴近你后面路径断言
    resp = echo_service.post_json({"user": {"id": 10086}})
    assert_status_code(resp,200)

    body = resp.json()
    assert_json_value(body, "json.user.id",10086)
    assert calls["n"] == 2


@pytest.mark.retry
@pytest.mark.mock
def test_retry_exhausted_raise(echo_service,monkeypatch):
    """
    一直超时：重试耗尽后应抛出 Timeout（不要吞异常）
     """
    def always_timeout(method,url,**kwargs):
        raise requests.exceptions.ReadTimeout("always timeout")

    monkeypatch.setattr(echo_service.client.session, "request", always_timeout)

    with pytest.raises(requests.exceptions.ReadTimeout):
        echo_service.post_json({"user":{"id":10086}})
