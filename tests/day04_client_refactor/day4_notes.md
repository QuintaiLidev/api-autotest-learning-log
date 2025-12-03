Day 04｜API Client 重构与网络坑位实战笔记
目标

用封装的 APIClient + fixture 提供的 token，向公共回显服务发请求，并断言 Authorization 头被正确携带与回显。

你遇到的问题 & 一步步解决

系统/环境代理劫持 → ProxyError/502

现象：requests 走了系统代理或双层 VPN（手机热点开 VPN + 电脑也开 VPN）。

修复：

在 APIClient 中：session.trust_env = False。

在 tests/conftest.py：全局“清代理”fixture（function 级 autouse=True）。

必要时在直接用 requests 的用例里加：proxies={"http": None, "https": None}。

尽量避免“双 VPN/代理链”。

# tests/conftest.py
import pytest

@pytest.fixture(autouse=True)
def disable_proxies(monkeypatch):
    for k in ["HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy","NO_PROXY","no_proxy"]:
        monkeypatch.delenv(k, raising=False)


ScopeMismatch（作用域不匹配）

现象：session 级 fixture 里用到了 function 级的 monkeypatch。

修复：将“清代理”fixture 改成 function 级（如上做法），或用纯 os.environ 做 session 级保存/恢复（不依赖 monkeypatch）。

ReadTimeout 到 httpbin

现象：访问 httpbin.org 超时不稳。

修复：切换为国内更稳的 https://postman-echo.com；同时在 APIClient 加重试+更长超时。

# autofw/api_client.py（关键点）
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class APIClient:
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False  # 忽略系统/环境代理
        retry = Retry(total=3, backoff_factor=1.0, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def with_headers(self, headers: dict):
        clone = APIClient(self.base_url, self.timeout)
        clone.session.headers.update(self.session.headers)  # 继承已有默认头
        clone.session.headers.update(headers or {})
        return clone

    def get(self, path: str, params=None):
        return self.session.get(self.build_url(path), params=params, timeout=self.timeout)


404：Postman Echo 没有 /anything

修复：把参数化里的 "/anything" 改为 "/headers" 或仅保留 "/get"。

Header 大小写问题

现象：Postman Echo 回显的 headers 键名是小写，用 Authorization 取不到值。

修复：断言前统一把键名转成小写。

# 断言示例
body = resp.json()
echoed = {k.lower(): v for k, v in body.get("headers", {}).items()}
assert echoed.get("authorization") == f"Bearer {get_token}"


拼写错误

现象："Beaere" → "Bearer"。

修复：更正拼写，测试即过。

Day 04 最终用例（示例）
# tests/day04_client_refactor/test_with_client.py
import pytest

@pytest.mark.parametrize("path", ["/get", "/headers"])
def test_use_client_with_token_header(client, get_token, path):
    auth_client = client.with_headers({"Authorization": f"Bearer {get_token}"})
    resp = auth_client.get(path)
    assert resp.status_code == 200

    body = resp.json()
    echoed = {k.lower(): v for k, v in body.get("headers", {}).items()}
    assert echoed.get("authorization") == f"Bearer {get_token}"


client fixture 指向 https://postman-echo.com，并已在 APIClient 内部关闭环境代理 + 加重试/超时。

稳定性与可维护性要点

环境隔离：trust_env=False + 全局“清代理”fixture，避免系统代理污染。

幂等测试：尽量使用稳定回显端点（/get、/headers），或上 requests-mock 本地打桩（彻底不依赖网络）。

无副作用：with_headers() 返回“克隆客户端”，不污染原始会话默认头。

参数化：路径参数化时确保端点真实存在且语义清晰。

断言健壮：处理大小写差异；必要时做最小化断言（只断我们关心的字段）。

自测小问答（含答案）

为什么 session.trust_env=False？
防止 requests 继承系统/环境代理，避免被代理劫持导致超时/502。

为什么 Postman Echo 的 headers 要转小写再断言？
它回显的键名是小写，直接取 Authorization 会拿到 None。

ScopeMismatch 的根因是什么？
function 级的 monkeypatch 被 session 级 fixture 使用，引发作用域不匹配。

为什么要把 /anything 改为 /headers？
Postman Echo 无 /anything，有 /headers 并且更贴合“回显请求头”的用例目标。

如何让这类测试完全不依赖外网？
使用 requests-mock 在测试中回显请求头，模拟 200 响应。