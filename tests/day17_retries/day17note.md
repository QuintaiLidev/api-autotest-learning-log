Day17：Retries（客户端级重试用例 + pytest 收集规则）

目标

把 retry 逻辑从“能跑”变成“有测试兜底”。

关键改动/产物

tests/day17_retries/test_retry_client.py：验证 client 的重试行为

关键坑（你遇到过最经典的一个）

pytest 没跑某个文件，最常见原因是：

文件名不符合 python_files = test_*.py

或者你当时文件是 .pyi（类型 stub），pytest 默认不收集

或者路径写错（你截图里也出现过命令行路径找不到文件）

你掌握的能力

你现在对 pytest 的“发现机制”有肌肉记忆了：命名规则 > 玄学 ✅