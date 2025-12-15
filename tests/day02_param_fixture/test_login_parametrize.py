import pytest


@pytest.mark.network
@pytest.mark.parametrize("path, expected", [
    ("/get", 200),
    ("/status/200", 200),
    ("/status/404", 404),
])
def test_api_status(client, path, expected):
    """
    Day02：验证不同 path 下接口返回的 HTTP 状态码是否符合预期。
    """

    resp = client.get(path)
    assert resp.status_code == expected
