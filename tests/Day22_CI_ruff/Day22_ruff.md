Day22 详细笔记（可直接贴到你的学习日志）
1）Day22 目标

把项目从“能跑”升级到“有质量门禁”：

引入 ruff 做静态检查（lint）

保持单测全绿

CI 分层不被破坏（network 依旧按条件触发）

2）你做了什么

✅ 运行 ruff check . 定位问题

✅ 修复 B904：except 里的 raise 路径更清晰（避免异常来源混淆）

✅ 修复 E402：把 import 调整到模块顶部（pytestmark 这种写法要注意顺序）

✅ commit：Day22_ruff_check

✅ 再次跑：lint + unit 全绿

3）你学到的“工程化要点”

lint 是早期拦截器：很多风格/异常处理问题，越晚修越贵

CI 分层要稳：不让“外网不稳定”影响主线回归（unit/lint 是主线，network 是巡检/手动）

4）本日结论

Day22 通关：你已经拥有“团队级别的基本质量门禁能力”。


常用命令（存档）
ruff check .
ruff check . --fix
pytest -q
pytest -m "not network" -q
pytest -m network -q
git status
git add .
git commit -m "Day22_ruff_check"