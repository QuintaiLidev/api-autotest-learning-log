import pytest
import requests

import pytest, requests

@pytest.mark.parametrize("path, expected", [
    ("/get", 200),
    ("/status/200", 200),
    ("/status/404", 404),
])
def test_api_status(path, expected):
    base = "https://postman-echo.com"
    # Postman Echo 没有 /status/{code}，我们改成 /status/{code} 的等价接口：/status/:code?  — 它支持
    # 实测 postman-echo 支持 /status/:code，所以直接拼：
    url = base + path
    resp = requests.get(url, timeout=20, proxies={"http": None, "https": None})
    assert resp.status_code == expected
