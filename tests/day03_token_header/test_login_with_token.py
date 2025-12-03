import pytest
import requests


@pytest.mark.parametrize("path", ["/get", "/headers"])
def test_use_token_in_header(client, get_token, path):
    headers = {
        "Authorization": f"Bearer {get_token}"
    }

    resp = client.with_headers(headers).get(path)

    # 断言:接口必须200
    assert resp.status_code == 200
    body = resp.json()
    # 统一把回显的header键名转换成小写，防止大小写差异
    echoed = {k.lower(): v for k, v in body.get("headers", {}).items()}
    assert echoed.get("authorization") == f"Bearer {get_token}"
