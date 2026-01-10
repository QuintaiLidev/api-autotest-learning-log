# tests/day18_retry_policy/test_retry_policy.py
import pytest
import requests
from autofw.utils.response_builder import build_response
import autofw.utils.api_client as api_client_mod  # ✅ 关键：显式导入子模块


@pytest.mark.mock
def test_retry_success_on_timeout(client, monkeypatch):
    client.retries = 2
    client.backoff = 0.1

    sleeps = []
    monkeypatch.setattr(api_client_mod.time, "sleep", lambda s: sleeps.append(s))

    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.exceptions.ReadTimeout("boom")
        return build_response(200, {"ok": True}, url=url)

    monkeypatch.setattr(client.session, "request", fake_request)

    resp = client.get("/get")
    assert resp.status_code == 200
    assert calls["n"] == 2
    assert len(sleeps) == 1


@pytest.mark.mock
def test_no_retry_on_404(client, monkeypatch):
    client.retries = 3
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        return build_response(404, {"msg": "nope"}, url=url)

    monkeypatch.setattr(client.session, "request", fake_request)
    resp = client.get("/get")
    assert resp.status_code == 404
    assert calls["n"] == 1
