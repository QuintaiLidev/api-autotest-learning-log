# Week01 一键化门禁入口（全绿 ✅）

## 目标
把“能跑的用例”升级为“任何人拉代码都能一键跑”的工程门禁入口：
- 本地：lint / unit / network 分层执行
- 输出：pytest-html 报告稳定产出
- 体验：少记命令，多记入口

## 本周交付物
### 1) scripts/run.ps1（门禁总入口）
支持四类运行方式：
- Mode：unit / network / all
- Marker：自定义 marker 表达式
- Report：自定义报告文件名

常用命令：
- `.\scripts\run.ps1 -Mode unit`
- `.\scripts\run.ps1 -Mode network`
- `.\scripts\run.ps1 -Mode all`
- `.\scripts\run.ps1 -Marker "mock" -Report "mock.html"`

### 2) README.md 补充 Quick Commands
新增「Quick Commands」区，保证新同学只看 README 也能跑起来：
- 创建 venv / 安装依赖
- ruff check
- pytest -q
- scripts/run.ps1 常用入口

### 3) 工程分层原则（当前版）
- unit：不依赖外部网络（默认稳定层）
- network：真外网巡检层（不稳定但必要）
- integration：真实联调层（也可能真打外网，按用例需求）

## CI 关联
- push/PR 默认跑 lint + unit（稳定层门禁）
- network 只在 schedule 或 workflow_dispatch(run_network=true) 时执行（巡检层）

## 结果
- Week01 全绿 ✅
- 门禁入口可复用、可读、可写进简历

## 下周（Week02）预告
失败定位闭环：
- APIClient 日志规范（请求/响应摘要、耗时、重试信息）
- 失败分类（超时/连接/5xx/断言失败）
- debug_playbook：失败如何复现、如何定位、如何加固
