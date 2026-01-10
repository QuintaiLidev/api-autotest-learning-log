Day19：Client Upgrade（统一入口 + 日志系统 + 可覆盖策略）

这一关的核心不是新功能，是“把系统变成可维护的系统”。

_request() 统一入口：get/post 全走同一条管道

per-request overrides：client.get(..., retries=0) 这种请求级覆盖

logging：

[REQ id] / [RESP id] / [ERR id] / [RETRY id] 全链路可追踪

headers 脱敏 ***REDACTED***，避免泄漏 Authorization

你踩过并修掉的两个“高价值坑”

类型注解写法错误导致运行时 TypeError
你已经修成 last_exc: Optional[BaseException] = None ✅

logging 格式化参数错位导致 %.2f 被塞进了字符串
这类坑以后你会一眼就抓出来，因为它会让“异常处理又抛异常”，特别恶心。