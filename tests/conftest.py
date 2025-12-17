# 让所有用例默认不继承系统/环境代理
import pytest
import os
import sys

PROXY_KEYS = [
    "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
    "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"
]


@pytest.fixture(scope="session", autouse=True)
def disable_proxies():
    """对每个用例自动清理环境代理变量，避免requests走系统/代理。"""
    backup = {k: os.environ.get(k) for k in PROXY_KEYS if os.environ.get(k) is not None}

    for k in PROXY_KEYS:
        os.environ.pop(k, None)

    # 让使用这个fixture的用例继续执行
    yield

    # 结束后恢复（可选，但建议做，避免影响你别的项目）
    for k in PROXY_KEYS:
        os.environ.pop(k, None)
    for k, v in backup.items():
        os.environ[k] = v


# --- force import your local api_client by file path ---
import sys, importlib.util, pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
AUTOFW_ROOT = PROJECT_ROOT / "autofw"

from autofw.utils.config_loader import load_config

API_CLIENT_PATH = PROJECT_ROOT / "autofw" / "utils" / "api_client.py"
# 动态加载 autofw.utils.api_client 模块
spec = importlib.util.spec_from_file_location(
    "autofw.utils.api_client",
    AUTOFW_ROOT / "utils" / "api_client.py")  # 如果你的 api_client 路径不同，按实际改
api_client = importlib.util.module_from_spec(spec)
assert spec and spec.loader, f"Cannot load spec from {API_CLIENT_PATH}"
# ✅ 一定要先把模块注册进 sys.modules
sys.modules["autofw.utils.api_client"] = api_client
# 然后再执行模块代码，这时 @dataclass 才能在 sys.modules 里找到自己
spec.loader.exec_module(api_client)
APIClient = api_client.APIClient
# -------------------------------------------------------

import pytest
import requests
from autofw.api_client import APIClient
from autofw.services.demo_echo_service import EchoService


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


@pytest.fixture(scope="session")
def client() -> APIClient:
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
        timeout=int(cfg.get("timeout", 20)),
        retries=int(cfg.get("retries", 2)),
        backoff=float(cfg.get("backoff", 0.5)),
    )


@pytest.fixture(scope="session")
def network_client(client: APIClient) -> APIClient:
    # 外网用更耐心的配置，不污染默认 client
    return client.__class__(
        base_url=client.base_url,
        timeout=max(client.timeout, 30),
        session=client.session,
        retries=max(getattr(client, "retries", 2), 3),
        backoff=max(getattr(client, "backoff", 0.5), 1.0)
    )


@pytest.fixture(scope="session")
def get_token() -> str:
    """
    Day3的token实例（此处为了演示写死）
    真实项目会在这里调用登录接口拿到token并返回。
    """
    return "test_user_fake_token"


@pytest.fixture
def echo_service(client: APIClient):
    """
    基于通用 client 构造一个 EchoService，给 Service 层用例复用。
    """
    from autofw.services.demo_echo_service import EchoService
    return EchoService(client)
