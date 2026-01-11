Day20 详细笔记（你通关的内容）
1）CI 的触发点（on）

你现在等价于做了这件事：

push / pull_request：自动跑（保证每次提交都验）

workflow_dispatch：手动跑（你想测外网时点一下）

schedule：定时跑（每天/每周巡检外网）

2）CI 的两层 jobs（分层执行）

job: unit

跑：pytest -m "not network" -q（或 not network and not integration，看你 marker 定义）

目标：快、稳定、必须绿

job: network

跑：pytest -m network -q（或 -m "network or integration"）

目标：真外网回归，不作为每次 push 的硬门槛（避免网络波动把你卡死）
你截图里 network 0s，说明你已经把“外网层不默认跑”这条铁律写进去了。

3）Artifacts（产物沉淀）

你已经把报告作为 artifact 上传（截图里 Artifacts: 1）

价值：CI 失败时不用复现，直接下载报告定位；成功也能留痕当“通关录像”。

4）命令清单（以后就按这个节奏）

本地快速回归：pytest -q

本地只跑离线：pytest -m "not network" -q

只跑 mock：pytest -m mock -q

只跑外网：pytest -m network -q

提交流水线：git add . && git commit -m "Day20 CI split" && git push