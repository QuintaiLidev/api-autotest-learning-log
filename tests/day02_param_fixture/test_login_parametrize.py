import pytest
import requests


@pytest.mark.parametrize("path, expected", [
    ("/get", 200),
    ("/status/200", 200),
    ("/status/404", 404),
])
def test_api_status(path, expected):
    """
    Day02：验证不同 path 下接口返回的 HTTP 状态码是否符合预期。

    这里使用独立的 Session，并显式关闭环境代理（trust_env=False），
    避免系统里的 127.0.0.1:7897 之类代理干扰我们访问 postman-echo.com。
    """
    base = "https://postman-echo.com"
    # Postman Echo 没有 /status/{code}，我们改成 /status/{code} 的等价接口：/status/:code?  — 它支持
    # 实测 postman-echo 支持 /status/:code，所以直接拼：
    url = base + path

    # ✅ 关键：关闭环境代理，和我们的 APIClient 行为保持一致

    session = requests.Session()
    session.trust_env = False      # 不读取系统环境变量里的代理
    session.proxies = {}           # 显式清空代理配置

    # ✅ 关键：一定要用 session.get，而不是 requests.get；
    resp = session.get(url, timeout=20)
    assert resp.status_code == expected
