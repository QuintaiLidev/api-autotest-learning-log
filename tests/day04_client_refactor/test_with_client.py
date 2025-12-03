import pytest


@pytest.mark.parametrize("path", ["/get", "/headers"])
def test_use_client_with_token_header(client, get_token, path):
    """
    用封装好的APIClient + fixture 的 token，发送请求并校验授权头是否传到服务器
    """
    # with_headers 不会污染元 client 的 默认头，只对当前“克隆客户端”生效
    auth_client = client.with_headers({"Authorization": f"Bearer {get_token}"})

    # 发送 GET 请求（base_url + path 自动拼接）
    resp = auth_client.get(path)

    # 断言：接口200
    assert resp.status_code == 200

    # httpbin 会回显请求，包括我们传过去的headers
    body = resp.json()
    echoed = {k.lower(): v for k, v in body.get("headers", {}).items()}
    assert echoed.get("authorization") == f"Bearer {get_token}"
