Day11 笔记：统一日志 + 规范标记 + 初级 Service 层
1. 统一日志系统 logging_helper

文件：autofw/utils/logging_helper.py

你做了这些事：

用 Path(__file__).resolve().parents[2] 自动推导出 项目根目录；

创建 logs/ 目录，用于统一存放日志文件；

实现 get_logger(name: str = "autofw")：

如果 logger 已经有 handlers，直接复用（防止重复加 handler 导致多次重复输出）；

同时输出到：

控制台（StreamHandler）

文件 logs/autofw.log（FileHandler）

统一日志格式：

"%(asctime)s [%(levelname)s] %(name)s - %(message)s"


效果：任何模块只要：

from autofw.utils.logging_helper import get_logger

logger = get_logger("autofw.xxx")
logger.info("something")


就能同时打到控制台 + 文件里，而且不会重复叠加 handler。

2. APIClient 接入日志 + 规范化

文件：autofw/utils/api_client.py

你重构成了这样一个风格：

使用 @dataclass 管理：

@dataclass
class APIClient:
    base_url: str
    timeout: int = 10
    session: requests.Session = field(default_factory=requests.Session)


with_headers：

新建 requests.Session()，先拷贝当前 session.headers，再更新新的 headers；

日志：logger.info("Clone APIClient with extra headers: %s", headers)

_full_url：

如果是以 http:// / https:// 开头 → 认为是完整 URL；

否则 base_url.rstrip("/") + "/" + path.lstrip("/") 拼接。

get / post：

发送前后都记日志，比如：

logger.info("GET %s params=%s", url, params)
logger.info("RESP %s %s status=%s", "GET", url, resp.status_code)


现在跑任意用例，你都能在 logs/autofw.log 里看到一条完整记录：

2025-xx-xx xx:xx:xx [INFO] autofw.api_client - GET https://postman-echo.com/get params={'foo': 'bar'}
2025-xx-xx xx:xx:xx [INFO] autofw.api_client - RESP GET https://postman-echo.com/get status=200


现实意义：

定位问题不用再到处 print；

面试说：“我的 API 自动化框架带有统一日志模块，可以追踪每一条请求的 URL / 参数 / 状态码”，非常加分。

3. 规范 pytest markers（标记）

文件：pytest.ini

你修正了：

把错误的 makers 改为正确的 markers；

显式声明现有用到的所有 mark：

[pytest]
testpaths = tests
addopts = -q --html=reports/report.html --self-contained-html

markers =
    smoke: 冒烟用例，最基础、最关键的功能检查
    api: 接口相关用例
    config: 环境配置相关用例（读取 config.yml 等）
    data_driven: 数据驱动相关用例（YAML / 参数化）
    assertions: 高级断言相关用例（字典子集、统一断言等）
    service: Service 业务封装层相关用例


这样：

不会再出现 Unknown mark 的 warning；

你可以按模块 / 维度来跑用例：

pytest -m "smoke" -q

pytest -m "data_driven or assertions" -q

pytest -m "service" -q

这就是“用例分组” + “回归集筛选”的基础能力。

4. 初级 Service 层：EchoService

目录：autofw/services/

你新建了：

autofw/services/__init__.py

autofw/services/demo_echo_service.py

EchoService 大致结构：

from autofw.utils.api_client import APIClient

class EchoService:
    """
    玩具 Service 层示例，封装 postman-echo 的常见操作。
    """

    def __init__(self, client: APIClient) -> None:
        self.client = client

    def get_with_params(self, params: Dict[str, Any]):
        return self.client.get("/get", params=params)

    def post_json(self, json_body: Dict[str, Any]):
        return self.client.post("/post", json=json_body)


测试文件：tests/day11_service_layer/test_echo_service.py

使用 client fixture + EchoService：

@pytest.mark.service
@pytest.mark.smoke
def test_echo_get_with_params(client):
    svc = EchoService(client)
    params = {"foo": "bar", "page": "1"}

    resp = svc.get_with_params(params)

    assert_status_code(resp, 200)

    body = resp.json()
    expected = {"args": params}
    assert_dict_contains(expected, body)


意义：

测试代码不再关心 base_url / requests 的细节；

用例的语义变成：“调用 EchoService.get_with_params，看回显是否正确”；

这是从「接口级测试」往「业务行为级测试」过渡的第一步。

5. Day11 简历 / 面试可以这样讲 🧠

在个人接口自动化练习项目中进一步演进框架：

实现了统一的 日志模块（基于 Python logging），自动在项目根目录创建 logs 目录，并将所有接口请求/响应记录到控制台和日志文件，便于问题排查与追踪。

重构 HTTP 客户端封装 APIClient，引入 with_headers 克隆客户端、统一 URL 拼接与超时时间管理，提升可复用性。

规范化 pytest 标记配置（smoke、api、data_driven、assertions、service 等），支持按功能模块和测试类型选择性执行用例。

引入基础 Service 层（业务封装层），以 EchoService 为例，将 postman-echo 接口调用封装为更贴近业务语义的方法，为后续真实业务模块（用户、订单等）的服务封装打下基础。