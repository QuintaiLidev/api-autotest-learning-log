Day14 学习笔记 · Assertions Plus（路径断言版本）
1. 新武器：assert_json_value 路径断言

核心能力：

用一条字符串路径，直戳 JSON 里的某个字段，断言它的值。

函数签名大致是：

assert_json_value(body, path: str, expected: Any)


使用规则：

用 . 分层级：

"json.user.id"

"items.1.id" （访问 list 下标 1 的元素的 id）

支持混合嵌套：dict + list 随意组合：

"data.list.0.details.name" 之类的都可以

例子（Day14 里的本地用例）：

body = {
    "json": {
        "user": {
            "id": 10086,
            "name": "Quintai-Li",
        },
        "tags": ["api", "test"],
    },
    "items": [
        {"id": 1},
        {"id": 2},
    ],
}

assert_json_value(body, "json.user.id", 10086)
assert_json_value(body, "json.tags.0", "api")
assert_json_value(body, "items.1.id", 2)


心智切换：
以前你要写 body["json"]["user"]["id"] == 10086，
现在直接一句 assert_json_value(body, "json.user.id", 10086)，
用例读起来更像“业务语句”，而不是“字典操作”。

2. 底层小引擎：_get_by_path

assert_json_value 背后，是一个通用取值函数 _get_by_path(data, path)：

path.split(".") 拆成一段一段：

"json.user.id" -> ["json", "user", "id"]

从 current = data 开始往里钻：

如果 current 是 Mapping（字典）：

检查 part 是否在 current 里

没有就抛 AssertionError("Path 'xxx' not found: missing key 'yyy' ...")

有就 current = current[part]

如果 current 是 list / tuple：

把 part 转成下标 idx = int(part)

越界就抛 AssertionError("index 99 out of range")

否则 current = current[idx]

否则：

抛 AssertionError("Cannot descend into non-container ...")

最后返回的 current，就是我们要断的那个实际值。

你在日志里看到过类似错误：

("Path 'json.user.id' not found: missing key 'user'",
 "current={'json': {...}, 'items': [...]}") 


这就是 _get_by_path 在告诉你：
“我走到这一步，找不到这一层的 key 了。”

3. 断言失败的文案设计

在 Day14，我们把失败信息也设计成“可读的调试提示”，而不是冷冰冰一个 False。

两种情况：

路径就不对

例如访问错了字段：

assert_json_value(body, "json.profile.id", 10086)


错误会长这样：

("Path 'json.profile.id' not found: missing key 'profile'",
 "current={'json': {...}, 'items': [...]}") 


你一眼就知道：

访问的是哪条路径：json.profile.id

卡在哪一层：missing key 'profile'

当前节点长啥样：current={...}

路径正确，但值不匹配

例如：

assert_json_value(body, "json.user.id", 10010)  # 故意写错


错误大致：

"Path 'json.user.id' expected=10010, actual=10086"


Day14 的测试专门验证了：

with pytest.raises(AssertionError) as excinfo:
    assert_json_value(body, "json.user.id", 10010)

msg = str(excinfo.value)
assert "json.user.id" in msg
assert "expected=10010" in msg


这说明你的断言工具不仅能“对错”，还能给“诊断信息”。

4. 与 Service 层 + 实际接口结合

Day14 最后一枪，是把这套玩意儿用在真实请求上：

resp = echo_service.post_json(payload)
assert_status_code(resp, 200)
body = resp.json()

# postman-echo 的 /post 会在 body["json"] 里回显我们的请求体
assert_json_value(body, "json.user.id", 10086)
assert_json_value(body, "json.meta.page", 1)


整条链路是：

用例
→ 调 EchoService（业务动作）
→ EchoService 用 APIClient 调 HTTP
→ postman-echo 回显请求体
→ 用 assert_status_code + assert_json_value 做断言

用例本身完全不用碰 "json" / "data" / "headers" 的结构细节。
你只用写出“业务视角的路径”。

这就是“用断言工具把 HTTP 细节吃掉”的感觉 👍

5. 到 Day14 为止，你在断言方面已经有：

assert_status_code

标准化状态码断言

assert_dict_contains

字典子集断言，写“只关心的字段”

assert_json_value

用路径精确点名某个字段的值

配合 Service 层，你现在可以写出：

resp = order_service.create_order(payload)

assert_status_code(resp, 201)
body = resp.json()
assert_json_value(body, "data.order_id", not_none)
assert_json_value(body, "data.status", "CREATED")


这已经很接近真实项目里“可读性很高的接口用例”了。