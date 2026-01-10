import pytest
import requests
from autofw.utils.response_builder import build_response
import autofw.utils.api_client as api_client_mod


@pytest.mark.mock
def test_request_override_disable_retry(client, monkeypatch):
    # 把 sleep patch 掉，避免真睡
    sleeps = []
    monkeypatch.setattr(api_client_mod.time, "sleep", lambda s: sleeps.append(s))

    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        raise requests.exceptions.ReadTimeout("boom")

    monkeypatch.setattr(client.session, "request", fake_request)

    with pytest.raises(requests.exceptions.ReadTimeout):
        client.get("/get", retries=0)  # ✅ 覆盖：不重试

        assert calls["n"] == 1
        assert sleeps == []
