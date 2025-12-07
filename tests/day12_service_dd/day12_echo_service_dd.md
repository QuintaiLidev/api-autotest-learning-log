Day12 学习笔记（可直接存成 tests/day12_service_dd/day12_service_notes.md）
# Day12 - Service 层 + 数据驱动联动

## 1. 今日主题

- 在 **Service 层** 基础上：
  - 用 fixture 注入 Service（EchoService）
  - 用 pytest 参数化（data driven）驱动 Service 层测试
  - 继续复用统一断言工具：`assert_status_code` / `assert_dict_contains`
- 目标：让用例从“HTTP 细节”完全抬升到“业务动作”视角。

---

## 2. 代码结构回顾

### 2.1 APIClient（统一 HTTP 封装）

文件：`autofw/utils/api_client.py`

关键点：

- 使用 `@dataclass` 管理 `base_url / timeout / session / default_headers`
- 在 `__post_init__` 中：
  - `self.session.trust_env = False` 关闭系统代理干扰
  - 设置统一默认头：`User-Agent`, `Accept`
- 日志：
  - `get()` / `post()` 中使用 `get_logger("autofw.api_client")`
  - 每个请求生成 `req_id`（短 UUID），日志格式：
    - `[REQ xxxx] GET https://...`
    - `[RESP xxxx] GET https://... status=200`
- **一定返回 `resp`**：
  - `return resp`（这次踩坑的根源就是：封装层没 return，上层就拿到 None）

统一出口：

- 文件：`autofw/api_client.py`
- 内容只是转发：

  ```python
  from autofw.utils.api_client import APIClient
  __all__ = ["APIClient"]


好处：外部统一 from autofw.api_client import APIClient，实现细节藏在 utils 里，后面重构不影响使用方。

2.2 Service 层：EchoService

文件：autofw/services/demo_echo_service.py

from autofw.api_client import APIClient

class EchoService:
    def __init__(self, client: APIClient) -> None:
        self.client = client

    def get_with_params(self, params: Dict[str, Any]):
        return self.client.get("/get", params=params)

    def post_json(self, json_body: Dict[str, Any]):
        return self.client.post("/post", json=json_body)


设计要点：

Service 层只关心“我调用哪个业务接口，带哪些参数”

client 从外部注入（fixture 里构造），符合依赖注入的思路

以后可以扩展多个 Service：

UserService

OrderService

AuthService
等等，每个都用同一个 APIClient。

2.3 测试用例：Service + 数据驱动 + 高级断言

文件：tests/day12_service_dd/test_echo_service_dd.py

1）基础版：单例用例
@pytest.mark.service
@pytest.mark.data_driven
@pytest.mark.smoke
def test_echo_get_with_params_basic(echo_service: EchoService):
    params = {"foo": "bar", "page": "1"}

    resp = echo_service.get_with_params(params)
    assert_status_code(resp, 200)

    body = resp.json()
    expected = {
        "args": params
    }
    assert_dict_contains(body, expected)


特点：

用例只关心：

调用 echo_service.get_with_params(params)

状态码是否为 200

body["args"] 是否回显了 params

完全不关心：

base_url 是多少

path 是 /get 还是别的

requests 细节
这些都被 Service 层吃掉了。

2）数据驱动版：多组参数复用同一业务动作
@pytest.mark.service
@pytest.mark.data_driven
@pytest.mark.parametrize(
    "params",
    [
        {"foo": "bar", "page": "1"},
        {"foo": "baz", "page": "2"},
        {"search": "api", "limit": "10"},
    ],
    ids=[
        "foo=bar,page=1",
        "foo=baz,page=2",
        "search=api,limit=10",
    ]
)
def test_echo_get_params_dd(echo_service: EchoService, params):
    resp = echo_service.get_with_params(params)

    assert_status_code(resp, 200)

    body = resp.json()
    expected = {
        "args": params
    }
    assert_dict_contains(body, expected)


特点：

同一个“业务动作”：EchoService.get_with_params

换不同的参数（params）

通过 assert_dict_contains 只关心 args 子集匹配，无需对整包 JSON 做死板比对

3）POST + 高级断言（字典子集）
@pytest.mark.service
@pytest.mark.assertions
def test_echo_post_json_service(echo_service: EchoService):
    payload = {
        "user": {
            "id": 10086,
            "name": "Quintai-Li",
        },
        "meta": {
            "env": "dev",
        },
    }

    resp = echo_service.post_json(payload)
    assert_status_code(resp, 200)

    body = resp.json()

    expected_subset = {
        "json": payload
    }
    assert_dict_contains(body, expected_subset)


postman-echo 的 /post 会在 json 字段里回显请求体

我们只关心 body["json"] 是否等于 payload

通过 assert_dict_contains 可以很优雅地表达这种“子集/结构匹配”

3. 今天这关，可以怎么写进简历 / 面试？

可以总结成类似一段话（你后面可以按需要优化措辞）：

在自研的 API 自动化测试小框架中，我基于 requests 封装了统一的 APIClient，支持全局日志记录（请求 ID、URL、状态码）、超时配置以及 header 克隆；在此基础上引入了 Service 层（如 EchoService），将 HTTP 细节从测试用例中抽离，使用例以“业务动作 + 数据驱动”的方式组织。同时实现了统一断言工具（状态码断言、字典子集断言），显著提升了用例可读性和可维护性。

这句话你现在完全配得上。