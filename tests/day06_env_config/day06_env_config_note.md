Day06 笔记：环境配置 & 可配置化 APIClient

目标：
✅ 把「环境、base_url、超时时间」从代码里抽出来，放到 config.yml
✅ 用 load_config() 统一读取配置
✅ 让 APIClient 自动使用配置里的 base_url / timeout
✅ 用 monkeypatch + 环境变量切换环境

1. 目录结构（跟 Day06 相关的）
pythonProject/
├─ config/
│  └─ config.yml          # 环境配置文件（新增）
├─ autofw/
│  ├─ __init__.py
│  ├─ api_client.py       # 通用 HTTP 客户端（之前就有）
│  └─ utils/
│     ├─ __init__.py
│     └─ config_loader.py # 新增：配置读取工具
└─ tests/
   ├─ conftest.py         # 公共 fixture（client、disable_proxies）
   └─ day06_env_config/
      └─ test_env_config.py   # Day06 的测试

2. config.yml 的设计

文件：config/config.yml

# 默认使用哪个环境
default_env: dev

# 各环境配置
envs:
  dev:
    base_url: "https://postman-echo.com"
    timeout: 10

  staging:
    base_url: "https://postman-echo.com"
    timeout: 5


要点：

顶层有两个 key：default_env + envs

envs 下面是各环境名称（dev, staging 等）

每个环境下至少要有：

base_url

timeout（可选，没写就用默认值）

3. 配置加载工具：autofw/utils/config_loader.py

核心作用：
统一从 config.yml 读取配置，并根据 TEST_ENV 选择环境。

# autofw/utils/config_loader.py
from pathlib import Path
import os
import yaml

# 项目根目录：.../pythonProject
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yml"


def load_config() -> dict:
    """
    读取 config.yml，并根据 TEST_ENV 选择对应环境的配置。

    返回例如：
    {
        "env": "dev",
        "base_url": "https://postman-echo.com",
        "timeout": 10,
    }
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # 1）先取默认环境
    default_env = raw.get("default_env", "dev")

    # 2）再看是否有系统环境变量 TEST_ENV 覆盖
    env_from_os = os.getenv("TEST_ENV")
    env = env_from_os or default_env

    # 3）从 envs 区块里找对应环境配置
    envs = raw.get("envs", {})
    env_cfg = envs.get(env)
    if not env_cfg:
        raise KeyError(f"config.yml 中没有环境 '{env}' 的配置")

    return {
        "env": env,
        "base_url": env_cfg["base_url"],
        "timeout": env_cfg.get("timeout", 10),
    }


关键点记忆：

Path(__file__).resolve().parents[2] ✅
不要写成 parent[2]（WindowsPath 不支持下标）

envs = raw.get("envs", {})
之前写成 raw.get("default", "dev") 会拿到一个字符串，导致 .get() 报错。

4. conftest.py 中的两个关键 fixture

文件：tests/conftest.py

4.1 关闭代理：disable_proxies

这个是为了解决你本机 VPN / 系统代理影响请求的问题。

import pytest
import os
from autofw.utils.api_client import APIClient
from autofw.utils.config_loader import load_config


@pytest.fixture()
def disable_proxies(monkeypatch):
    """
    清理环境变量里的代理，避免 requests 走系统 HTTP/HTTPS 代理。
    """
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        monkeypatch.delenv(key, raising=False)

4.2 全局 APIClient：client
@pytest.fixture()
def client(disable_proxies) -> APIClient:
    """
    提供一个可复用的 API 客户端。

    - base_url / timeout 从 config.yml 读取
    - 依赖 disable_proxies，保证不走代理
    """
    cfg = load_config()

    client = APIClient(
        base_url=cfg["base_url"],
        timeout=cfg["timeout"],
    )
    return client


注意：
这两个 fixture 都是函数级别（默认），解决了之前的 ScopeMismatch 报错。

5. Day06 的测试用例

文件：tests/day06_env_config/test_env_config.py

import os
import pytest
from autofw.utils.config_loader import load_config


@pytest.mark.config
def test_config_default_env():
    """
    不设置 TEST_ENV 时，应该使用 config.yml 里的 default_env（dev）
    """
    # 确保环境变量里没有 TEST_ENV
    os.environ.pop("TEST_ENV", None)

    cfg = load_config()
    assert cfg["env"] == "dev"
    assert cfg["base_url"].startswith("https://")


@pytest.mark.config
def test_config_switch_env_with_monkeypatch(monkeypatch):
    """
    用 monkeypatch 模拟切换 TEST_ENV，验证读取的是 staging 配置
    """
    monkeypatch.setenv("TEST_ENV", "staging")
    cfg = load_config()

    assert cfg["env"] == "staging"
    assert cfg["base_url"].startswith("https://")


def test_client_get_works_with_config(client):
    """
    验证 client fixture 能正常发请求，并且使用配置里的 base_url。
    """
    resp = client.get("/get", params={"foo": "bar"})
    assert resp.status_code == 200

6. Day06 遇到的坑 & 记忆点

WindowsPath object is not subscriptable

错误写法：Path(__file__).resolve().parent[2]

正确写法：Path(__file__).resolve().parents[2]

AttributeError: 'str' object has no attribute 'get'

原因：envs = raw.get("default", "dev")
取到的是字符串 "dev"，不是 dict。

修正：envs = raw.get("envs", {})

ScopeMismatch Fixture 作用域不一致

起因：disable_proxies 是 function-scope，client 是 session-scope（或反之）

解决：都用默认 @pytest.fixture()（函数级）

配置文件不存在

FileNotFoundError: 配置文件不存在: .../config/config.yml

解决：确认 config/config.yml 文件路径和命名完全一致。

✅ Day06 结束时，你已经具备的能力

知道怎么用 YAML + load_config 管理多环境配置

知道如何用 环境变量 / monkeypatch 切换环境

可以让 APIClient 自动读配置，而不是代码里写死 base_url

用 fixture 把「关闭代理」「统一客户端」抽象成 项目级的通用能力