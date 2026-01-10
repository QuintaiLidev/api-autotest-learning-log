import pytest
from autofw.utils.response_builder import build_response


@pytest.mark.mock
def test_logging_redaction(client, monkeypatch, caplog):
    def fake_request(method, url, **kwargs):
        return build_response(200, {"ok": True}, url=url)

    monkeypatch.setattr(client.session, "request", fake_request)

    with caplog.at_level("INFO"):
        client.get("/get", headers={"Authorization": "Bearer SECRET"})

    text = "\n".join([r.message for r in caplog.records])
    assert "Bearer SECRET" not in text
    assert "***REDACTED***" in text
