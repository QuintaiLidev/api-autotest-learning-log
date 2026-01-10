Day18：Retry Policy（什么时候该重试，什么时候不该）

目标

把重试做成“有边界、有策略”的工程实现：

异常重试（Timeout / ConnectionError）

状态码重试（429/5xx）

不重试（404 这种明确业务失败）

关键改动/产物

retry_exceptions：
Timeout / ConnectionError 进入重试

用例：

test_retry_success_on_timeout：第一次 ReadTimeout，第二次成功

test_no_retry_on_404：404 只打一枪，不连发
关键坑（你已经解决过）

monkeypatch 路径要对：
你最终采用 “显式导入模块对象再 patch”：

import autofw.utils.api_client as api_client_mod
monkeypatch.setattr(api_client_mod.time, "sleep", ...)


这比字符串路径 patch 稳定 ✅

你掌握的能力

你已经会写“策略型重试”，不是无脑重试 ✅