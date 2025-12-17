import pytest
import requests
from autofw.utils.response_builder import build_response  # 你 Day15 那个

@pytest.mark.mock
def test_client_retry_success(client, monkeypatch):
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.exceptions.ReadTimeout("boom")
        return build_response(200, {"ok": True, "url": url}, url=url)

    monkeypatch.setattr(client.session, "request", fake_request)

    resp = client.get("/get")
    assert resp.status_code == 200
    assert calls["n"] == 2   # ✅ 证明重试发生了

@pytest.mark.mock
def test_client_retry_fail_final(client,monkeypatch):
    def always_timeout(method, url, **kwargs):
        raise requests.exceptions.ReadTimeout("always")

    monkeypatch.setattr(client.session, "request", always_timeout)

    with pytest.raises(requests.exceptions.ReadTimeout):
        client.get("/get")
