Day16 笔记：稳定性修复副本（日志格式 + 外网 Timeout 分层）🛡️
1）Day16 遇到的两类“全图怪”

怪 1：TypeError: not enough arguments for format string（全量连锁）
根因通常是日志 Formatter 写错（典型：%(message)% 少了 s），导致任何 logger 输出都会炸，所以你看到几乎所有测试都跟着失败。

你现在这版已经修正为：

"%(asctime)s [%(levelname)s] %(name)s - %(message)s"


并且 logger.propagate = False，避免重复输出或被 root logger 干扰。

怪 2：ReadTimeout（偶发，网络波动）
postman-echo 偶尔慢一下，测试就会被拖死。
Day16 的关键不是“祈祷网络别抽风”，而是把它变成可控变量：

用 @pytest.mark.network 给外网用例打标

默认回归先跑 not network，让你日常稳定全绿

2）你现在框架“链路”怎么讲（面试可用）

以 Service 用例为例：

pytest 启动

conftest.py 提供 fixture：client / echo_service

用例只做业务动作：echo_service.get_with_params(params)

Service 层把业务动作映射成 HTTP：client.get("/get", params=...)

APIClient 负责：

拼 URL、统一 timeout、统一 session

记录请求日志 [REQ id] / [RESP id]

返回 requests.Response

assertions 工具做统一断言（状态码、子集、路径断言等）

一句话：pytest(依赖注入) + Service(业务语义) + Client(HTTP细节) + assertions(可复用断言) + logging(可观测)