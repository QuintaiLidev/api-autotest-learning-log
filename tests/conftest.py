import os
import pytest
import requests

from autofw.utils.config_loader import load_config
from autofw.api_client import APIClient
from autofw.services.demo_echo_service import EchoService

PROXY_KEYS = [
    "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
    "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"
]

@pytest.fixture(scope="session", autouse=True)
def disable_proxies():
    """对每个用例自动清理环境代理变量，避免 requests 走系统/代理。"""
    backup = {k: os.environ.get(k) for k in PROXY_KEYS if os.environ.get(k) is not None}
    for k in PROXY_KEYS:
        os.environ.pop(k, None)
    yield
    for k in PROXY_KEYS:
        os.environ.pop(k, None)
    for k, v in backup.items():
        os.environ[k] = v


@pytest.fixture(scope="function")
def setup_env():
    print("\n[Fixture]初始化测试环境")
    yield
    print("[Fixture]测试结束，清理环境")


# ✅ 默认离线 token：保证 mock / not network 也稳定
@pytest.fixture(scope="session")
def get_token() -> str:
    return "test_user_fake_token"


# ✅ 需要真实打外网时再用它（只给 network/integration 用例依赖）
@pytest.fixture(scope="session")
def get_token_network() -> str:
    print("\n[Fixture]开始获取token（网络）...")
    url = "https://postman-echo.com/post"
    payload = {"username": "test_user", "password": "123456"}
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        token = resp.json().get("json", {}).get("username", "") + "fake_token"
    else:
        token = ""
    print(f"[Fixture]获取到 token={token}")
    return token


@pytest.fixture(scope="session")
def client() -> APIClient:
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
        backoff=max(getattr(client, "backoff", 0.5), 1.0),
        retry_statuses=getattr(client, "retry_statuses", (429, 500, 502, 503, 504)),
        retry_exceptions=getattr(client, "retry_exceptions", (requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
    )


@pytest.fixture
def echo_service(client: APIClient):
    return EchoService(client)
