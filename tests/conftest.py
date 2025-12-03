# 让所有用例默认不继承系统/环境代理
import pytest
import os
import sys

@pytest.fixture(autouse=True)
def disable_proxies(monkeypatch):
    """对每个用例自动清理环境代理变量，避免requests走系统/代理。"""
    for k in [
        "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
        "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"
    ]:
        monkeypatch.delenv(k, raising=False)
    # 让使用这个fixture的用例继续执行
    yield


# --- force import your local api_client by file path ---
import sys, importlib.util, pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from autofw.utils.api_client import APIClient
from autofw.utils.config_loader import load_config

API_CLIENT_PATH = PROJECT_ROOT / "autofw" / "api_client.py"
spec = importlib.util.spec_from_file_location("my_api_client", str(API_CLIENT_PATH))
api_client = importlib.util.module_from_spec(spec)
assert spec and spec.loader, f"Cannot load spec from {API_CLIENT_PATH}"
spec.loader.exec_module(api_client)
APIClient = api_client.APIClient
# -------------------------------------------------------

import pytest
import requests
from autofw.utils.api_client import APIClient


@pytest.fixture(scope="function")
def setup_env():
    print("\n[Fixture]初始化测试环境")
    yield
    print("[Fixture]测试结束，清理环境")


@pytest.fixture(scope="session")
def get_token():
    """
    模拟获取登录token的前置操作
    scope=“session” 表示整个测试运行期间只执行一次
    """
    print("\n[Fixture]开始获取token...")
    url = "https://postman-echo.com/post"
    payload = {
        "username": "test_user",
        "password": "123456"
    }

    # 这里用httpbin模拟登录接口
    response = requests.post(url, json=payload)

    # 模拟从响应中“提取token”
    # 实际项目中你会从response.json()里拿真实字段
    if response.status_code == 200:
        # 随便拿一个字段当作token（这里只是一个模拟）
        token = response.json().get("json", {}).get("username", "") + "fake_token"
    else:
        token = ""

    print(f"[Fixture]获取到的 token{token}")
    # yield 前 = 前置逻辑
    yield token
    # yield 后 = 后置逻辑
    print("[Fixture] 测试结束，清理token（这里暂时只是打印）")


@pytest.fixture()
def client(disable_proxies) -> APIClient:
    """
    提供一个全局可复用的 API 客户端（session 级别：整个测试周期仅初始化一次）。
    优点：性能更好；缺点：少数情况下要注意状态共享（如 cookie）。

    统一从配置文件里读取 base_url 和 timeout。
    以后只改 config.yml 就能切环境，而不用改代码。
    """
    cfg = load_config()
    print(f"[Fixture] 使用环境: {cfg['env']} | base_url={cfg['base_url']}")
    return APIClient(
        base_url=cfg["base_url"],
        timeout=cfg["timeout"],)


@pytest.fixture(scope="session")
def get_token() -> str:
    """
    Day3的token实例（此处为了演示写死）
    真实项目会在这里调用登录接口拿到token并返回。
    """
    return "test_user_fake_token"
