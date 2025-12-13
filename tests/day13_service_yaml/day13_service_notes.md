📝 Day13 笔记（建议直接复制到 day13_service_notes.md）
1. 今日主线

主题：YAML 数据驱动 + Service 层联动

从 Day12 的「Service 层 + 参数化」往前走一步：
👉 把测试数据完全外置到 YAML 文件里，用例只描述“业务动作”和“期待结果”。

关键词：

Service 层：EchoService

YAML 用例：例如 echo_get_cases.yml

数据驱动：pytest.mark.parametrize + yaml.safe_load

断言：assert_status_code + assert_dict_contains

结构：测试代码彻底不关心 HTTP 细节和具体参数写死问题

2. 代码结构复盘（抽象版）

这一层的结构现在大概是这样：

autofw/
  utils/
    api_client.py        # 带日志的统一 HTTP 客户端
    assertions.py        # 统一断言工具：状态码 + 字典子集
  services/
    demo_echo_service.py # EchoService：get_with_params / post_json

tests/
  day12_service_dd/
    test_echo_service_dd.py         # 代码内参数化的数据驱动
  day13_service_yaml/
    test_echo_service_yaml.py       # 从 YAML 加载的数据驱动
    testdata/
      echo_get_cases.yml            # 用例数据


请求链路现在是：

pytest 用例
➡ EchoService（业务动作：查询、提交 JSON）
➡ APIClient（拼 URL、带 headers、统一超时、打日志）
➡ requests 发送 HTTP 请求
➡ 收到响应后返回到上层用例，通过 assertions 做统一断言。

3. Day13 具体做了什么？
3.1 设计 YAML 用例格式

一个典型的 YAML case 大概是这种结构（示意）：

- name: "foo=bar,page=1"
  params:
    foo: "bar"
    page: "1"
  expected_status: 200
  expected_args:
    foo: "bar"
    page: "1"

- name: "search=api,limit=10"
  params:
    search: "api"
    limit: "10"
  expected_status: 200
  expected_args:
    search: "api"
    limit: "10"


关键点：

name 用来当 pytest 参数化的 id，报告更可读。

params 用来喂给 EchoService.get_with_params(params)。

expected_status 用在 assert_status_code(resp, expected_status)。

expected_args 用来验证响应体中 body["args"] 是否按原样回显。

3.2 在测试里加载 YAML + 参数化

测试文件里大概做了这些事（逻辑层面）：

用 pathlib.Path 找到 echo_get_cases.yml；

用 yaml.safe_load 读成 Python 列表；

用 @pytest.mark.parametrize("case", cases, ids=[...]) 做数据驱动；

测试体内：

resp = echo_service.get_with_params(case["params"])
assert_status_code(resp, case["expected_status"])

body = resp.json()
expected = {
    "args": case["expected_args"]
}
assert_dict_contains(body, expected)


意义：

以后加/改用例，只用改 YAML，不动 Python 代码；

很贴近真实项目里“测试策划 / 用例表 -> YAML/Excel -> 自动化”的那种链路。

3.3 和 Day12 的关系

Day12：参数还写在 @pytest.mark.parametrize 里，测试代码同时承担了“逻辑 + 数据”；

Day13：把“数据”抽出去交给 YAML 文件，
pytest 这边只负责：读数据 → 调用 Service → 做统一断言。

你现在的栈是：

接口细节（URL、headers、超时、日志） ➜ 都被 APIClient 吃掉

业务动作（get / post 某个功能） ➜ 被 Service 层抽象

测试用例 ➜ 尽量只写“业务输入 + 期待业务结果”，数据可以放 YAML 里

4. 面试可以怎么讲 Day13？

可以有这样的表述（你以后可以按自己的语气改）：

在我做的接口自动化小框架里，我把测试用例数据和测试代码分离了。
Service 层负责封装业务动作（比如调用 postman-echo 的 GET/POST），
测试这边用 YAML 存放不同组合的查询参数和期望结果，然后通过 pytest 参数化批量跑。
这样一来：

新增用例只需要改 YAML 文件；

测试代码基本不变，可复用性比较高；

实际项目里也方便测试策划、产品甚至运营一起参与维护用例。

再加一句：

这一层再往下是一个统一封装的 APIClient，有日志、超时、headers 管理，
出问题时可以直接用 request_id 在日志里串起来查请求和响应。

这就是一个完整可讲的“我做了什么 + 为什么这么做 + 有什么好处”。