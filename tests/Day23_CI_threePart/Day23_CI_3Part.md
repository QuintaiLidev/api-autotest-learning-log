Day23 核心目标
把“项目能跑”升级成“项目可重复构建、可持续维护”：
依赖分层 + CI 三段式（lint / unit / network）+ 文档化启动方式
你完成了哪些关键动作


依赖拆分




把运行时依赖（requests/pyyaml）从测试工具里剥离出来


dev/test/lint 统一走 requirements-dev.txt




CI 设计成三层




lint：ruff check .


unit：默认跑，不碰真外网（稳定、快）


network：条件触发（巡检/手动），避免外网波动把 push 搞黄




可见性增强




README 加 CI badge


reports 作为 artifact 留证据链（回归可追溯）


本关掉过的坑（你已经踩平了）


网络层不默认跑：否则外网抖一下，CI 直接红，体验很差


依赖文件编码/换行：之前 pip install -r requirements-dev.txt 出现过 GBK 解码问题，你现在这版内容是干净的（建议保持 UTF-8）


Day23 通关奖励（对你“面试叙事”很有用）
你现在能讲清楚一套工程化思路：

“我把测试分成 lint/unit/network 三层。push/PR 默认只跑稳定的 unit + lint，network 作为巡检或手动验证，避免外部依赖导致 CI 不稳定，同时保留报告 artifacts 方便追溯。”

这句就是你项目的“战斗宣言”。
