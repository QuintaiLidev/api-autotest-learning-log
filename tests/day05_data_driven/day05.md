# Day05 - Pytest 配置 & 报告 & 标记

## 1. 今天的目标
- 能用 pytest-html 生成测试报告。
- 会写 pytest.ini，让项目有统一的测试配置。
- 会用 pytest.mark 给用例打标签，并按标签执行测试。

## 2. 今天用到的重要命令

1. 手动生成报告：
   - `pytest --html=reports/report_day05.html --self-contained-html`

2. 使用 pytest.ini 默认配置跑测试：
   - `pytest`
   - `pytest -m smoke`
   - `pytest -m "not smoke"`

## 3. 新认识的配置文件：pytest.ini

- `addopts`：设置默认命令行参数。
- `testpaths`：告诉 pytest 去哪里找测试。
- `python_files / python_classes / python_functions`：控制 pytest 怎么识别用例。
- `markers`：提前声明自定义标记，避免警告。

## 4. 修改过的代码（关键片段）

- 在 test_get_demo.py 增加：
  - `@pytest.mark.smoke`
  - `@pytest.mark.api`

## 5. 易错点 / 踩坑记录

- pytest.ini 必须放在项目根目录，跟 tests 同级。
- markers 一定要在 pytest.ini 的 [pytest] 下面先声明，否则会有 warning。
- 用 `pytest -m smoke` 时，如果没有任何用例带 smoke，就会显示 0 tests collected。

## 6. 我的体会

- 项目一旦加上 pytest.ini + 报告，整体感觉就像个“真正的自动化项目”了。
- 标记（markers）让用例集更有结构感，后面可以针对不同阶段跑不同用例集。

Day05 小问答（自测用）+ 标准答案

你可以先自己在脑子里/纸上写答案，再对照下面👇

Q1：为什么要写 pytest.ini，而不是每次都用一大串命令行参数？

参考答案：

pytest.ini 可以把 全局的、固定不变的配置（比如：测试路径、默认 addopts）写死在项目里；

一旦配置好，团队里所有人只要执行 pytest 就能用同样的规则跑测试；

避免每个人记不同的命令，也减少敲错参数的概率；

对于你自己来说，像一个“项目级启动脚本”，专业项目基本都有。

Q2：@pytest.mark.smoke 是做什么的？一定要在 pytest.ini 里声明吗？

参考答案：

@pytest.mark.smoke 是给用例打一个「标签」或「分类」，方便后面用 pytest -m smoke 只跑这一类用例；

不声明也能跑，但 pytest 会给出 PytestUnknownMarkWarning，提示这个标记没有在配置文件里注册；

在 pytest.ini 的 markers 里提前声明，可以：

消除 warning

起到「文档」作用，让看项目的人知道有哪些标签、每个标签的含义。

Q3：现在项目里已经有 APIClient + fixture + markers + HTML 报告了，如果你写到简历上，你会怎么表述？

参考答案示例：

参与并搭建了基于 Python + Pytest 的接口自动化测试脚手架，
封装通用 APIClient 请求类，结合 fixture 复用会话、token 等测试上下文，
支持用例参数化与标记（smoke / regression / api），
并通过 pytest-html 生成自包含的 HTML 测试报告，方便本地调试及结果归档。

你可以根据自己的风格再改得更「主角视角」一点，比如：

我独立搭了一个基于 Pytest 的 API 自动化小框架，
写了自己的 APIClient 封装 + fixture 体系，还加了标签和 HTML 报告，
后面可以直接在这个基础上扩展成项目级自动化平台。
