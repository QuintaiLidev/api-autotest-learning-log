# Week01 一键化门禁入口

## 目标
- 本地一键：lint / unit / network
- CI 复用同一套入口，减少重复命令
- 报告产物固定路径 + 固定命名，方便追溯

## 交付物
- [ ] Makefile：make lint / make unit / make network / make ci
- [ ] scripts/run.ps1：Windows 一键执行入口
- [ ] reports/：unit.html / network.html 固定输出
- [ ] README：补充 Quick Commands（可选）

## 验收标准
- 新机器 clone 后，能一键跑通 unit（不依赖外网）
- CI 上 job 清晰，artifact 可下载并可打开报告

## 本周遇到的问题与解决
- TBD

## 下周计划（Week02 失败定位闭环）
- 日志规范：REQ/RESP/elapsed/retry
- debug_playbook.md：失败分类与定位流程
