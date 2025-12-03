# Day09 - 统一 GET / POST 的数据驱动测试

## 1. 今天解决的核心问题

之前是：
- Day07：单独用 YAML 驱动 GET 接口
- Day08：单独用 YAML 驱动 POST 接口

问题：  
**真实项目里接口一大堆，如果 GET / POST 各写一套数据驱动逻辑，会越来越乱。**

Day09 的目标：  
👉 用一套 YAML + 一套测试代码，**统一驱动 GET 和 POST**，甚至以后可以扩展其他方法。

---

## 2. YAML 用例结构设计

### 2.1 统一的字段设计

`data/day09_unified_cases.yml` 每条用例大致形如：

```yaml
- name: "GET 带查询参数，校验 args 回显"
  method: "GET"
  path: "/get"
  params:
    foo: "bar"
    page: "1"
  expected_status: 200
  expect_echo: "args"

- name: "POST JSON，校验 json 回显"
  method: "POST"
  path: "/post"
  json:
    username: "test_user"
    password: "123456"
  expected_status: 200
  expect_echo: "json"

- name: "POST 空 JSON 也要走通"
  method: "POST"
  path: "/post"
  json: {}
  expected_status: 200
  expect_echo: "json"


关键字段含义：

name: 用例名称（只是为了在 pytest 报告里更好看）

method: "GET" / "POST"，决定用什么 HTTP 方法

path: 接口路径，比如 /get、/post

params: GET 的查询参数（可选）

json: POST 请求体 JSON（可选）

expected_status: 预期 HTTP 状态码

expect_echo:

"args"：期望校验 GET 查询参数回显（resp.json()["args"]）

"json"：期望校验 POST JSON 回显（resp.json()["json"]）

不写 / None：只校验状态码，不管 body

3. 测试代码核心逻辑

文件：tests/day09_unified_data_driven/test_unified_data_driven.py

3.1 启动时一次性加载 YAML
from autofw.utils.data_loader import load_yaml

cases = load_yaml("day09_unified_cases.yml")


统一用我们封装好的 load_yaml，自动从 PROJECT_ROOT / data 下找文件。

避免在每个测试函数里重复读文件。

3.2 pytest 参数化 + data-driven
@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",
    cases,
    ids=[c["name"] for c in cases],
)
def test_unified_get_post(client, case):
    ...


case 是从 YAML 中取出的字典。

ids 里用 name，让 html 报告更可读。

4. 统一 GET / POST 行为
4.1 根据 method 选择请求方式
method = case["method"].upper()
path = case["path"]
params = case.get("params") or {}
json_body = case.get("json") or {}
expected_status = case["expected_status"]
expect_echo = case.get("expect_echo")

if method == "GET":
    resp = client.get(path, params=params)
elif method == "POST":
    resp = client.post(path, json=json_body)
else:
    pytest.skip(f"暂不支持的方法: {method}")


要点：

case.get("params") or {}：即使 YAML 里没写，也不会是 None。

对未知方法直接 pytest.skip，比硬报错更优雅。

4.2 统一状态码断言
assert resp.status_code == expected_status


这一步是所有接口的“底线”断言。

5. 按 expect_echo 决定怎么校验 body
5.1 不配置 expect_echo：只校验状态码
if not expect_echo:
    return

5.2 校验 GET 查询参数回显 (expect_echo == "args")
resp_json = resp.json()

if expect_echo == "args":
    echoed_args = resp_json.get("args", {})
    assert echoed_args == params


postman-echo 的 /get 会把查询参数回显在 args 字段里。

我们只要比对：回显参数 == 我发送的 params。

5.3 校验 POST JSON 回显 (expect_echo == "json")
elif expect_echo == "json":
    echoed_json = resp_json.get("json")

    # ⚠ 空 JSON 的特殊情况：postman-echo 会返回 null（Python 里是 None）
    if json_body == {} and echoed_json is None:
        echoed_json = {}

    assert echoed_json == json_body


重点坑：

当 json_body == {}（空字典）时，postman-echo 回显的是 null，在 Python 里是 None。

为了断言方便，我们让：

如果我发的是 {} 且回显是 None → 手动把 echoed_json 改成 {} 再比较。

5.4 未知类型：skip
else:
    pytest.skip(f"暂不认识的 expect_echo 类型: {expect_echo}")

6. 统一数据驱动的优势总结

YAML 结构统一
GET / POST 用例都通过一套字段描述，扩展性更强。

测试函数唯一
一个 test_unified_get_post 搞定所有 GET/POST 接口，逻辑集中、可维护性高。

新增用例只需改 YAML
不必每加一个接口就复制一份测试函数代码，只要在 YAML 里加一条记录。

更接近真实项目风格
真实项目经常会有 “用例数据 + 通用执行引擎” 这种模式，今天就是一个简化版的“执行引擎”。

7. 今天踩过的小坑回顾

if ... 行末尾漏掉冒号 : → 语法错误 SyntaxError: expected ':'

空 JSON 被回显成 null（None）
→ 需要在断言前做一个兼容处理。

记得给 @pytest.mark.data_driven 配置自定义 mark（可选），否则只是一个 warning。