![CI](https://github.com/QuintaiLidev/api-autotest-learning-log/actions/workflows/ci.yml/badge.svg)

# API Autotest Learning Log

Learning project for API automation using **Python + pytest + requests**.  
Focus: **engineering-style** API test framework building (fixtures, markers layering, service layer, assertions, retry policy, logging, CI).

## Tech Stack
- Python 3.12
- pytest + pytest-html
- requests
- ruff
- YAML config
- PostgreSQL (Week03 DB assertions)

## Project Structure
```text
.
├─ .github/workflows/ci.yml
├─ autofw/
│  ├─ api_client.py                  # re-export compatibility layer
│  ├─ services/
│  │  └─ demo_echo_service.py        # toy Service layer (EchoService)
│  └─ utils/
│     ├─ api_client.py               # APIClient (timeout/retry/backoff/logging/redaction)
│     ├─ assertions.py               # assert_status_code / assert_dict_contains / assert_json_value ...
│     ├─ config_loader.py            # load config.yml
│     ├─ logging_helper.py           # unified logger (console + logs/autofw.log)
│     └─ db.py                       # minimal Postgres helper (Week03)
├─ config/
│  └─ config.yml                     # envs/dev/staging: base_url/timeout/retries/backoff...
├─ docs/
│  └─ milestones/
│     ├─ week01.md                   # Week01 notes (gate entry / scripts)
│     └─ week02.md                   # Week02 notes (debug playbook etc.)
├─ scripts/
│  └─ run.ps1                        # one-click runner (unit/network/all, custom markers)
├─ tests/
│  ├─ conftest.py                    # fixtures: client/network_client/echo_service, disable proxies
│  ├─ day01_get_demo/
│  ├─ day02_param_fixture/
│  ├─ day03_token_header/
│  ├─ day04_client_refactor/
│  ├─ day06_env_config/
│  ├─ day07_data_driven/
│  ├─ day08_post_data_driven/
│  ├─ day09_unified_data_driven/
│  ├─ day10_advanced_assertions/
│  ├─ day11_service_layer/
│  ├─ day12_service_dd/
│  ├─ day13_service_yaml/
│  ├─ day14_assertions_plus/
│  ├─ day15_mocking/
│  ├─ day16_retry_transport/
│  ├─ day17_retries/
│  ├─ day18_retry_policy/
│  ├─ day19_client_upgrade/
│  └─ week03_sql_assertions/
├─ Makefile
├─ requirements.txt                  # runtime deps
├─ requirements-dev.txt              # dev deps (pytest/ruff/html/psycopg2-binary...)
├─ pytest.ini                        # markers / addopts / testpaths
├─ reports/                          # html reports (local + CI artifacts)
└─ logs/                             # logs/autofw.log

Setup

python -m venv venv
# Windows
venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

Quick Commands (Windows)

Lint:

ruff check .

Run all tests (default):

pytest -q

Run by layers (recommended):

# stable local layer (no real network)
.\scripts\run.ps1 -Mode unit

# real network layer (network / integration)
.\scripts\run.ps1 -Mode network

# lint + unit + network
.\scripts\run.ps1 -Mode all

# custom marker expression + custom report file
.\scripts\run.ps1 -Marker "mock" -Report "mock.html"

Markers Layering
	•	mock: fully offline (no network)
	•	unit: everything not (network or integration or db)
	•	db: database integration tests (Postgres)
	•	network / integration: real external network calls (may be flaky)

Example:

pytest -m "not (network or integration or db)" -q
pytest -m "db" -q
pytest -m "network or integration" -q

Run DB tests locally (Windows)

1) Ensure PostgreSQL is running

Confirm you can connect:

psql -U postgres -h localhost -p 5432 -d postgres

2) Create a test database/user (one-time)

In psql:

CREATE USER autofw WITH PASSWORD 'autofw';
CREATE DATABASE autofw OWNER autofw;
GRANT ALL PRIVILEGES ON DATABASE autofw TO autofw;

3) Set environment variables (PowerShell)

PG helper reads:
	•	PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

Option A: current terminal only (recommended)

$env:PGHOST="127.0.0.1"
$env:PGPORT="5432"
$env:PGDATABASE="autofw"
$env:PGUSER="autofw"
$env:PGPASSWORD="autofw"
$env:PGCONNECT_TIMEOUT="3"

Option B: permanent (optional)

setx PGHOST "127.0.0.1"
setx PGPORT "5432"
setx PGDATABASE "autofw"
setx PGUSER "autofw"
setx PGPASSWORD "autofw"
setx PGCONNECT_TIMEOUT "3"

After setx, open a new terminal so variables take effect.

4) Run DB tests

pytest -m "db" -q

With HTML report:

pytest -m "db" -q --html=reports/db.html --self-contained-html

CI (GitHub Actions)

Workflow: .github/workflows/ci.yml

Jobs:
	•	lint: ruff check .
	•	unit: pytest -m "not (network or integration or db)" + HTML report artifact
	•	network: runs only on schedule or workflow_dispatch(run_network=true) + HTML report artifact
(and can start a Postgres service container if DB job is included in that layer)

Artifacts:
	•	reports-unit
	•	reports-network

```md
### Run performance tests (Locust)

Group A:
```powershell
.\scripts\run.ps1 -Mode perf -PerfGroup A

Group B:

.\scripts\run.ps1 -Mode perf -PerfGroup B

Artifacts:
	•	reports/locust.html
	•	reports/locust_B.html
	•	reports/locust*.csv

Note:
	•	Do not open the CSV files while Locust is running, or Windows may lock the files.

---

