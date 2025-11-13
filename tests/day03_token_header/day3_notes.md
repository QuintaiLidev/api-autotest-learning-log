# Day 3：登录接口 + fixture + 参数化

**日期：** 2025-11-10  
**主题：** 使用 fixture 模拟获取 token，并在多接口请求中复用

---

## ✅ 今日完成

- 新建 `conftest.py`，实现 `get_token` fixture：
  - 会在测试前获取一次 token（session 级别）
  - yield 前后分别是“前置”和“后置”
- 新建 `test_login_with_token.py`：
  - 使用 `get_token` 作为入参
  - 把 token 放进请求头 Authorization 中
  - 通过 httpbin 的回显验证请求头是否正确传递

---

## 🧠 今日关键概念

- `@pytest.fixture(scope="session")`：整个测试运行只执行一次
- `yield`：分隔前置（准备）和后置（清理）
- `@pytest.mark.parametrize`：一套测试逻辑，跑多组数据
- 真实项目中：
  - fixture 常用来：登录、建连接、造数据、清理数据

---

## 🤔 自我小问答

1. fixture 和普通函数的区别是什么？
2. 为什么要用 `scope="session"` 来获取 token？
3. 如果以后有 10 个接口都要用 token，怎么用 fixture 简化代码？
Q1. fixture 的核心作用是什么？yield 前后分别做什么？
A1. fixture 用于测试前准备 + 测试后清理的可复用机制；yield 前是前置逻辑，yield 后是后置清理。

Q2. 为什么 assert headers in json_data 报 TypeError: unhashable type: 'dict'？
A2. in 对字典检查的是key，而 headers 本身是一个 dict（不可哈希），不能作为 key 检查，所以报错。应改为断言具体字段，例如：
json_data["headers"].get("Authorization") == f"Bearer {token}"。

Q3. Authorization 里 Bearer 后面为什么要加空格？
A3. 标准写法是 "Bearer <token>"，有空格；没有空格会变成无效的头部值（例如 Bearertoken），服务端解析不了。

Q4. 想让 token 只获取一次、供多条用例复用，应设置 fixture 的什么 scope？
A4. scope="session"，整个测试会话只执行一次并复用。

Q5. 如何让 pytest 只在 tests/ 下找用例？
A5. 在根目录 pytest.ini 写：

[pytest]
testpaths = tests
---

## 🚀 Day 4 预告

- 把这些零散脚本，开始整理成“小框架”的结构：
  - `api_client.py` 用来封装请求
  - `conftest.py` 管配置 & fixture
  - `tests/` 目录专门放测试用例
- 为后续引入 Allure 报告做准备。
