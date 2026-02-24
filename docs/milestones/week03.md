目标：引入 DB assertions layer

方案：PG helper + fixture + schema + cleanup

分层：unit/not db，db=独立层

用例：create/update persisted

风险：本机无 docker，CI 用 postgres service