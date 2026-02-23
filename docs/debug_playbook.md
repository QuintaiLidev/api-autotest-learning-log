# Debug Playbook - CI / 接口自动化失败定位手册

> 适用范围：用于快速 **复现**、**定位**、**修复** 以下失败：
> - `lint`（ruff 静态检查）
> - `unit`（不依赖外网的稳定层）
> - `network` / `integration`（真外网层，仅 schedule/手动触发）

---

## 0. 项目信息（填空）
- 仓库：【api-autotest-learning-log】
- 默认分支：【main】
- Workflow：【.github/workflows/ci.yml】
- 统一入口：
  - 本地 Windows：`.\scripts\run.ps1 -Mode unit|network|all`
  - CI/Linux：`make lint|unit|network`

---

## 1. 前 60 秒：快速分诊清单（Triage）

### 1.1 确认失败的 Job
- [ ] Job 名称：`lint` / `unit` / `network`
- [ ] 触发类型：`push` / `pull_request` / `workflow_dispatch` / `schedule`
- [ ] Actions 里失败的 step：【例如：Ruff lint / Run unit tests / Run network tests】

### 1.2 判断“代码问题”还是“环境/基础设施问题”
**代码问题常见信号**
- 断言失败、ImportError、ruff 规则报错、pytest 用例失败

**环境/基础设施问题常见信号**
- pip install 失败、checkout 失败、DNS/连接超时、权限、限流、缓存异常

结论：
- [ ] 本次更像：【代码问题 / 环境问题】

### 1.3 下载报告（如果有 artifact）
- 下载 `reports-unit` / `reports-network`
- 打开 `reports/unit.html` 或 `reports/network.html`，确认：
  - 用例总数、失败列表、错误堆栈（stacktrace）

---

## 2. 本地复现（最短路径）

### 2.1 环境信息采集（把结果贴到 PR/issue）
```bash
python -V
pip -V
pytest --version
ruff --version
2.2 安装依赖
pip install -r requirements-dev.txt
2.3 按“分层”复现
A) Lint（ruff）
ruff check .
B) Unit（不依赖外网）
Windows

.\scripts\run.ps1 -Mode unit
Linux/macOS（或 CI 逻辑一致）

make unit
# 或：
pytest -m "not (network or integration)" -q
C) Network / Integration（真外网）
Windows

.\scripts\run.ps1 -Mode network
Linux/macOS

make network
# 或：
pytest -m "network or integration" -q
3. 失败分类（选一个对号入座）
A) Lint 失败（ruff）
常见原因

导入顺序、未使用变量、格式问题、规则触发等

修复步骤

 运行 ruff check .

 按提示修复文件：【文件路径】

 再次运行 ruff check . 直到全绿

备注

如果某条规则不适合项目，可在 pyproject.toml 里配置 ignore，但必须写清理由。

B) Unit 失败（稳定层）
常见原因

fixture/配置加载问题、导入路径问题、用例依赖外网但没标 marker、时间相关波动

修复步骤

 确认 unit 层 marker 表达式排除了 (network or integration)

 在报告/日志里定位失败用例

 单测单点复现（精准击杀）：

pytest -q path/to/test_file.py::test_name -vv
 修复后再跑 unit 层验证全绿

C) Network / Integration 失败（真外网层）
常见原因

外部服务抖动/限流、超时过小、重试策略不合理、响应字段偶发变化

修复步骤

 确认 network job 是否正确触发（schedule/手动）

 增加信息量复现：

pytest -m "network or integration" -vv --durations=10
 若属于外部抖动：

能 mock 的下沉到 mock 层

保留“最小真外网巡检集”（少而稳定）

 必要时调整 APIClient：timeout / retries / backoff

D) CI 环境/基础设施失败（Infra）
常见原因

依赖安装失败、命令不可用、报告目录未创建导致 artifact 缺失、路径/权限问题

修复步骤

 看失败 step 的原始命令与错误信息

 确认 runner 可用工具（Ubuntu 有 make；Windows 本地未必有）

 确保在生成报告前创建 reports/（例如 mkdir -p reports）

 修复后重跑 workflow 验证

4. 证据包（发 PR/写总结的标准格式）
把下面 6 项贴出来就够了：

失败 job + 触发类型：【例如：network on schedule】

失败 step 的关键日志（10-20 行）

本地复现命令 + 结果（能贴截图更好）

根因总结（1 句话）：【例如：Makefile 用了空格缩进导致 CI make 解析失败】

修复总结（1 句话）：【例如：Makefile 规则行改为 Tab + 修正 target 名称】

预防措施（1 句话）：【例如：CI 强制使用 make target；本地用 run.ps1 同步行为】

5. 面试讲故事模式（60 秒 STAR）
S（Situation 情景）
【什么时候触发、什么场景失败？例如：nightly schedule 触发 network 巡检失败】

T（Task 目标）
【你要保证什么？例如：CI 门禁稳定、报告可追溯、失败能快速定位】

A（Action 行动，建议 3 步）
【先定位：看 job/step + 下载报告】

【再复现：本地按层跑 unit/network，缩小范围】

【再加固：写 playbook/补日志/隔离 mock vs network/调整重试超时】

R（Result 结果，尽量量化）
CI 恢复：【三绿灯】

定位耗时：【从 X 分钟 -> Y 分钟】

稳定性提升：【把不稳定点下沉到 mock，保留最小真外网巡检】

6. Week2 验收标准（Definition of Done）
 Playbook 已创建，结构清晰可读

 任意失败可在 2 分钟内归类 A/B/C/D

 CI 报告 artifact 能支撑定位（unit/network 均可追溯）

 你能用 STAR 讲清楚一次真实修复案例（60 秒）

