![CI](https://github.com/QuintaiLidev/api-autotest-learning-log/actions/workflows/ci.yml/badge.svg)

# API Autotest Learning Log

Learning project for API automation using **Python + pytest + requests**.  
Includes fixtures, parameterization, headers validation, and step-by-step day folders.

## Structure
- `tests/day01_get_demo/` – first GET test
- `tests/day02_param_fixture/` – parametrize + fixture
- `tests/day03_token_header/` – token fixture + Authorization header
- `autotest/` – shared code (api_client coming next)
- `data/`, `reports/`, `logs/`

## Run
```bash
pip install -r requirements.txt   # if you exported one
pytest


## Quick Start
```bash
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
ruff check .
pytest -q

# 只跑本地稳定层（不打真外网）
.\scripts\run.ps1 -Mode unit

# 跑真外网层（network / integration）
.\scripts\run.ps1 -Mode network

# 全部跑完（lint + unit + network）
.\scripts\run.ps1 -Mode all

# 指定 marker 表达式（你想怎么拼都行）
.\scripts\run.ps1 -Marker "mock" -Report "mock.html"