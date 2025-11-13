import pytest
import requests

BASE_URL = "https://httpbin.org"


@pytest.mark.parametrize("path", ["/get", "/anything"])
def test_use_token_in_header(get_token, path):
    """
    使用fixture提供的token，放在请求头里发送请求
    """
    url = BASE_URL + path

    headers = {
        "Authorization": f"Bearer {get_token}"
    }

    response = requests.get(url, headers=headers)

    print(f"\n[TEST]请求地址：{url}")
    print("[TEST]请求头：", headers)
    print("[TEST]状态码：", response.status_code)

    # 断言:接口必须200
    assert response.status_code == 200

    # 断言：返回里能看到我们传的Authoritarian 头（httpbin会帮我们回显）
    json_data = response.json()
    assert "headers" in json_data
    assert json_data["headers"].get("Authorization") == f"Bearer {get_token}"
