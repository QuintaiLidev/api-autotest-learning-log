# Debug Playbook | 失败定位闭环（Week02）

> 目标：当 CI / 本地测试失败时，做到 **可复现、可定位、可解释、可加固**。  
> 你可以把它当作“故障处理说明书 + 面试故事提词器”。

---

## 0. 快速结论（TL;DR）

当失败发生，我按三步走：

1) **先分层**：unit（稳定层） vs network/integration（真外网层）  
2) **再分类**：超时 / 连接 / 5xx / 断言 / 数据与环境  
3) **最后闭环**：复现 -> 定位 -> 修复/加固 -> 记录（日志/用例/手册）

---

## 1. 运行入口（我只用这三个命令）

### 1.1 稳定层（默认先跑它）
```powershell
.\scripts\run.ps1 -Mode unit
````

### 1.2 真外网层（只在需要时跑）

```powershell
.\scripts\run.ps1 -Mode network
```

### 1.3 全量（本地验收/发布前）

```powershell
.\scripts\run.ps1 -Mode all
```

> ✅ 如果是 CI 失败，我会先在本地用同一条命令复现（保证路径一致）

---

## 2. 一眼判断：失败发生在哪一层？

### 2.1 unit 失败（优先级最高）

特征：

* 不依赖外网
* 重跑大概率依然失败
  结论：
* **大概率是代码/断言/数据驱动/fixture 的稳定性问题**

行动：

* 直接进入 **第 3 节失败分类**

---

### 2.2 network / integration 失败（可疑：外网波动）

特征：

* 报错包含 Timeout / ConnectionError / 5xx / 429
* 重跑可能过、可能不过
  结论：
* **可能是外网波动，也可能是重试/超时策略不足或断言过严**

行动：

* 先看 **重跑是否稳定**（第 4 节）
* 再进入 **第 3 节失败分类**

---

## 3. 失败分类（Fail Taxonomy）

> 每次失败，先把它放进一个“盒子”里。盒子放对了，排查速度会快很多。

### A) Timeout 超时

常见症状：

* `requests.exceptions.Timeout`
* CI 环境更容易出现

排查路径：

1. 查看日志中该请求的 `timeout` 配置（默认 / 覆盖）
2. 看是否属于 network 层（外网波动）
3. 评估是否需要提升 network_client 的 timeout

加固策略（可选填）：

* [ ] network_client 提升 timeout 至：____ 秒
* [ ] 增加重试次数：____ 次
* [ ] 指数退避 backoff：____ 秒起

---

### B) ConnectionError 连接失败 / reset

常见症状：

* `requests.exceptions.ConnectionError`
* `Connection reset by peer`
* `Empty reply from server`

排查路径：

1. 确认当前网络是否可访问目标域名（公司网/代理/VPN）
2. 是否是 CI 网络抖动（尤其是外网 API）
3. 查看是否被代理污染（本项目已默认禁用代理：trust_env=False + disable_proxies）

加固策略：

* [ ] 保持 network 层“条件触发”（不让它污染主门禁）
* [ ] 对外网依赖改为 mock 或录制数据（后续可做）

---

### C) HTTP 5xx / 429

常见症状：

* status=500/502/503/504/429
* 日志中出现 RETRY 记录

排查路径：

1. 看响应码是否在 `retry_statuses` 列表里
2. 看是否触发重试、重试次数是否耗尽
3. 评估是否需要调整 retry_statuses / retries / backoff

加固策略：

* [ ] retry_statuses 增补：____
* [ ] retries 调整为：____
* [ ] backoff 调整为：____

---

### D) AssertionError 断言失败

常见症状：

* 断言字段缺失 / 值不一致 / schema 不匹配
* unit 层常见

排查路径：

1. 打开 pytest-html 报告：`reports/____.html`
2. 对照日志的 `REQ/RESP` 摘要，确认实际返回
3. 判断断言是否“过度严格”（字段可选 / 顺序问题 / 浮动值）

加固策略：

* [ ] 将断言改为“子集断言 / 宽松断言”
* [ ] 对浮动字段做忽略：____（例如 timestamp / request_id）
* [ ] 增加失败时打印关键上下文：____

---

### E) Data/Fixture/Env 问题（数据驱动、fixture 污染）

常见症状：

* 本地能过、CI 偶发失败
* 用例之间互相影响（状态共享）

排查路径：

1. 看 fixture scope 是否过大（session 引入状态污染）
2. 检查测试是否依赖执行顺序
3. 对数据驱动文件（YAML/JSON）做校验与日志输出

加固策略：

* [ ] 缩小 fixture scope：session -> function
* [ ] 清理共享状态（cookie/session）
* [ ] 给数据读取加校验与异常提示

---

## 4. 重跑策略（判断波动还是必现）

> 目的：用最少的重跑次数，判断“这是外网波动”还是“代码必现”。

### 4.1 network 失败时的重跑判定

* 重跑 1 次：仍失败 -> 更像配置/代码问题
* 重跑 1 次：通过 -> 更像外网波动（需要隔离）

建议命令：

```powershell
.\scripts\run.ps1 -Mode network
```

记录（填空）：

* 第一次失败时间：____
* 重跑结果：____（pass/fail）
* 失败类型：____（Timeout/Connection/5xx/Assertion/Other）

---

## 5. 我如何读日志（REQ/RESP/RETRY/ERR）

> Week02 的目标之一：让日志像“飞行记录仪”。

我会在日志里抓这几样：

* `req_id`：一次请求的唯一标识
* `method + url`
* `status_code`
* `elapsed_ms`
* `attempt` 与 `sleep`（重试轨迹）
* 脱敏 headers（Authorization 不落盘）

（填空）日志文件位置：

* `logs/____.log`

---

## 6. 修复后闭环（必须留痕）

每次我修复一个失败，我会做 3 件事：

1. **加固**（比如：更合理的断言、重试策略、超时配置）
2. **补一条用例或补一条日志**（防止同类问题复发）
3. **更新本 Playbook 的“案例库”**（第 7 节）

---

## 7. 案例库（面试讲故事用）

> 每个案例 6 行，面试 60 秒讲完。

### Case-01（模板）

* 背景：____（CI / 本地 / 某次回归）
* 现象：____（报错关键词 / 失败用例）
* 初判：____（属于哪一层：unit/network）
* 定位：____（日志 req_id / 报告截图 / 关键字段）
* 解决：____（改了什么：重试/断言/fixture）
* 收益：____（稳定性提升 / 回归更快 / 可解释）

### Case-02

* 背景：____
* 现象：____
* 初判：____
* 定位：____
* 解决：____
* 收益：____

---

## 8. 面试 60 秒版本（可直接背）

我做了接口自动化的“失败定位闭环”。
首先把测试分层：unit 默认跑、network 条件触发，避免外网波动污染门禁。
当失败发生，我先判断属于哪一层，再按超时/连接/5xx/断言/环境做分类。
同时在 APIClient 里规范日志，记录 req_id、耗时、状态码和重试轨迹。
最后把每次故障沉淀为 playbook + case，做到能复现、能定位、能解释、能加固。

```

---

## Week2 开团任务（你现在就可以做）
你按这 3 个交付物推进就行：

1) ✅ **补齐日志规范**（如果你已在 APIClient 有 logger，就把日志落到 `logs/` 文件 + 控制台）  
2) ✅ **把失败分类写进 Playbook**（你刚才这份已经有了）  
3) ✅ **跑一次故障演练**：故意制造一个失败（比如超时/断言），把 Case-01 填满

---
