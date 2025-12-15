# tests/day15_mocking/test_echo_service_mocked.py
import pytest

from autofw.utils.assertions import assert_status_code, assert_dict_contains, assert_json_value
from autofw.utils.response_builder import build_response


@pytest.mark.service
@pytest.mark.mock
def test_echo_get_with_params_mocked(echo_service, monkeypatch):
    """
    Mock 掉 HTTP GET，让 Service 层在离线环境也能跑：
    - 断言 status_code
    - 断言 args 回显
    - 顺便验证 URL 拼接正确
    """
    captured = {}

    def fake_request(method, url, params=None, timeout=None, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["params"] = params
        body = {"args": params or {}, "url": url}
        return build_response(200, body, url=url)

    # 只替换当前 client.session.get，不影响全局
    monkeypatch.setattr(echo_service.client.session, "request", fake_request)

    params = {"foo": "bar3", "page": "1"}
    resp = echo_service.get_with_params(params)

    assert_status_code(resp, 200)
    assert_dict_contains(resp.json(), {"args": params})

    assert "url" in captured, "mock 没命中：说明请求没有走到 session.request"
    assert captured["url"].endswith("/get")


@pytest.mark.service
@pytest.mark.mock
def test_echo_post_json_mocked(echo_service, monkeypatch):
    """
    Mock 掉 HTTP POST，验证路径断言 assert_json_value 在“真实业务用例”里的写法。
    """

    def fake_request(method, url, json=None, data=None, timeout=None, **kwargs):
        body = {
            "json": json,  # 模拟postman-echo 的回显结构
            "data": json,
            "url": url,
        }
        return build_response(200, body, url=url)

    monkeypatch.setattr(echo_service.client.session, "request", fake_request)

    payload = {"user": {"id": 10086, "name": "Quintai-Li"}, "meta": {"env": "dev", "page": 1}}
    resp = echo_service.post_json(payload)

    assert_status_code(resp, 200)
    body = resp.json()

    # 路径断言更贴近“业务含义”
    assert_json_value(body, "json.user.id", 10086)
    assert_json_value(body, "json.meta.page", 1)
