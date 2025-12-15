Day15 笔记：Mocking 让 Service 层离线也能跑
Day15目标

在不访问真实网络的情况下跑通 Service 层用例

用 monkeypatch 把 requests.Session.get/post 替换成“假的请求函数”

让测试更稳定（不被 postman-echo 抽风、超时影响）

为以后面试加分：你能讲清楚“为什么要 mock、mock 的粒度怎么选、怎么保证业务断言可信”

1）你今天踩到的坑（并修复）
错误写法

你一开始写的是：

monkeypatch.setattr(echo_service.client.session, "get", fake_get())


这会立刻调用 fake_get()，而 fake_get 需要 url 参数，所以报：
TypeError: missing 1 required positional argument: 'url'

正确写法

把函数对象本身塞进去，不要括号：

monkeypatch.setattr(echo_service.client.session, "get", fake_get)
monkeypatch.setattr(echo_service.client.session, "post", fake_post)


一句话总结：patch 的是“函数”，不是“函数执行结果”。

2）核心实现结构
2.1 fake_get / fake_post

你用 fake 函数模拟 requests 行为：

接收 url, params/json, timeout, **kwargs

拼一个“模拟响应体”

返回一个“假的 Response 对象”（通过 build_response）

示例思路：

def fake_get(url, params=None, timeout=None, **kwargs):
    body = {"args": params or {}, "url": url}
    return build_response(200, body, url=url)

2.2 build_response 的意义

你自己造一个 “像 requests.Response 一样的对象”，至少要满足你框架会用到的字段/方法：

resp.status_code

resp.json()

可能还有 resp.text / resp.url

这样你的断言工具（assert_status_code / assert_json_value / assert_dict_contains）完全照常用。

3）Day15 用例覆盖了什么
用例 1：mock GET

验证点：

status_code == 200

args 回显包含传入参数

url 拼接正确（你还用了 captured 记录 url/params）

用例 2：mock POST

验证点：

status_code == 200

返回结构里 json 回显等于 payload

用 assert_json_value(body, "json.user.id", 10086) 做“路径断言”

4）最重要：Day15 调用链路（你面试可以这样讲）
A. 不 mock 时的真实链路（Day11-14）
test_xxx()
  -> EchoService.get_with_params(params)
      -> APIClient.get("/get", params=...)
          -> requests.Session.get(url, ...)
              -> 网络请求 -> Response
          <- 返回 Response
      <- 返回 Response
  -> assert_status_code(resp, 200)
  -> resp.json() / assert_dict_contains / assert_json_value

B. mock 之后（Day15）的链路
test_echo_get_with_params_mocked()
  -> monkeypatch.setattr(session, "get", fake_get)  ✅替换入口
  -> EchoService.get_with_params(params)
      -> APIClient.get("/get", params=...)
          -> session.get(url, ...)   ✅这里已经不是 requests 了
              -> fake_get(url, params, timeout, ...)
                  -> build_response(200, body)
              <- 返回“假的 Response”
          <- 返回假的 Response
      <- 返回假的 Response
  -> assert_status_code / assert_dict_contains 正常工作


你可以一句话总结 mock 的价值：

Service 层与断言逻辑仍然是真实执行的

只有“HTTP 这一跳”被替换成可控的 fake，实现稳定、快速、离线可跑

5）Day15 你已经具备的面试表达点

为什么要 mock：外部依赖不稳定、测试要可重复、跑得快、离线可用

mock 粒度：mock 在 session.get/post，不破坏 Service/断言层

如何保证可信：返回结构与真实接口保持一致（postman-echo 的回显字段），断言仍然按业务含义写