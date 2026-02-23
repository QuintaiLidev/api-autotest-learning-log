# Week02 - 失败定位闭环（可观测 + 稳定性）

## 目标
把“CI 失败=慌”变成“CI 失败=按流程秒定位”，形成可复用的定位手册与证据链。

## 本周交付物
- [x] docs/debug_playbook.md：失败分类 + 本地复现 + 修复/预防流程（可面试 STAR）
- [ ] APIClient 日志规范（可选加分）：请求/响应摘要、耗时、状态码、重试信息
- [ ] 失败分类标签（可选加分）：timeout / connect / 5xx / assert / schema

## 我做了什么
- 定位过的失败案例（至少 1 个）：
  - 触发方式：【schedule / workflow_dispatch / push】
  - 根因：【例如 Makefile 缩进、依赖缺失、marker 误用】
  - 修复：【怎么改的】
  - 预防：【怎么避免复发】

## 结果
- CI 状态：【unit ✅ / lint ✅ / network ✅】
- 定位效率：【从 X 分钟 -> Y 分钟】
- 复现方式沉淀：【一键命令/文档入口】

## 下周（Week03）计划
- 引入 DB 断言：接口调用后查库验证（新增/更新至少各 1 条链路）
