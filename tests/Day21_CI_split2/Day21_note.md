Day21 你解锁的能力点


CI 概念落地




“push 后 Actions 自动跑”= 你一 git push，GitHub 就在云端自动拉代码、装依赖、跑测试，结果显示在 Actions 页里。




分层执行




unit：默认必跑（快速反馈）


network：不默认跑（慢、受网络影响），用 if: 条件控制触发。




触发器理解




workflow_dispatch：你在网页点 Run workflow 手动触发


schedule：由 cron 定时触发（巡检）




产物归档




测试报告作为 Artifacts 保存，等于你每次跑完都有“战报截图”。


Day21 结论一句话
你已经把“本地能跑”升级成“任何人拉下来都能跑，而且每次 push 都自动验收”，这就是工程化的门槛跨过去了。
