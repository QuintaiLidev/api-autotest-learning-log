![CI](https://github.com/QuintaiLidev/api-autotest-learning-log/actions/workflows/ci.yml/badge.svg)

# Server-side API Automation & Quality Gate Project

A server-side API automation engineering project built with **Python + pytest + requests**, focused on:
- layered test execution
- reusable request/client abstraction
- database assertions
- CI quality gates
- minimal performance validation
- business-flow level testing

This project is not just a collection of API test scripts.  
It is a **mini automation framework** designed to support local execution, CI execution, layered validation, report generation, and business-flow expression.

---

## What this project solves

Compared with simple request-based API scripts, this project addresses:

- inconsistent local execution commands
- missing test layering between stable / db / real-network cases
- duplicated request logic across test files
- lack of server-side state validation beyond API response checks
- weak failure diagnosis and report traceability
- lack of a minimal performance baseline

---

## Highlights

- **pytest layered execution**: `unit / db / network / integration / mock`
- **Unified APIClient**: URL joining, timeout, retry/backoff, default headers, logging, header redaction
- **YAML-based configuration**
- **Shared fixture management** via `conftest.py`
- **GitHub Actions quality gates**
- **PostgreSQL SQL assertions**
- **Locust minimal performance loop**
- **Business-flow testing** with `UserService`

---

## Project Structure

```text
.
├─ .github/workflows/ci.yml          # CI quality gates
├─ autofw/                           # framework code
│  ├─ api_client.py                  # re-export layer
│  ├─ services/
│  │  ├─ demo_echo_service.py
│  │  └─ user_service.py             # business actions: login/create/query/update
│  └─ utils/
│     ├─ api_client.py
│     ├─ assertions.py
│     ├─ config_loader.py
│     ├─ data_loader.py
│     ├─ db.py
│     ├─ logger_helper.py
│     └─ response_builder.py
├─ config/
│  └─ config.yml                     # env configuration
├─ data/
│  └─ *.yml                          # data-driven test data
├─ docs/
│  ├─ career_goals.md
│  ├─ debug_playbook.md
│  ├─ perf_report_locust.md
│  └─ milestones/
│     ├─ week01.md
│     ├─ week02.md
│     ├─ week03.md
│     ├─ week04.md
│     └─ month01_review.md
├─ perf/
│  └─ locustfile.py                  # minimal performance scenarios
├─ scripts/
│  └─ run.ps1                        # local unified entry
├─ tests/
│  ├─ conftest.py
│  ├─ business_flow/
│  │  └─ test_user_flow.py           # business flow: login -> create -> query -> update -> db assert
│  ├─ week03_sql_assertions/
│  │  └─ test_users_db_assertion.py
│  └─ day01~day23/...                # staged learning / evolution path
├─ Makefile
├─ pytest.ini
├─ requirements.txt
├─ requirements-dev.txt
└─ README.md


⸻

Tech Stack
	•	Python 3.12
	•	pytest / pytest-html
	•	requests
	•	PostgreSQL
	•	GitHub Actions
	•	Locust
	•	Ruff
	•	YAML

⸻

Quick Start

Setup

python -m venv venv
# Windows
venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

Lint

ruff check .

Run default tests

pytest -q


⸻

Run by layers

Stable local layer

.\scripts\run.ps1 -Mode unit

Real network layer

.\scripts\run.ps1 -Mode network

Run all

.\scripts\run.ps1 -Mode all

Custom marker

.\scripts\run.ps1 -Marker "mock" -Report "mock.html"


⸻

Run performance tests

Group A

.\scripts\run.ps1 -Mode perf -PerfGroup A

Group B

.\scripts\run.ps1 -Mode perf -PerfGroup B

Artifacts:
	•	reports/locust.html
	•	reports/locust_B.html
	•	reports/locust*.csv

Do not open CSV files while Locust is running, or Windows may lock them.

⸻

Layering Strategy
	•	mock: fully offline
	•	unit: everything not (network or integration or db)
	•	db: database assertion tests
	•	network / integration: real external calls, may be unstable

Examples:

pytest -m "not (network or integration or db)" -q
pytest -m "db" -q
pytest -m "network or integration" -q


⸻

Run DB tests locally (Windows)

1. Ensure PostgreSQL is running

psql -U postgres -h localhost -p 5432 -d postgres

2. Create test database and user

CREATE USER autofw WITH PASSWORD 'autofw';
CREATE DATABASE autofw OWNER autofw;
GRANT ALL PRIVILEGES ON DATABASE autofw TO autofw;

3. Set environment variables

$env:PGHOST="127.0.0.1"
$env:PGPORT="5432"
$env:PGDATABASE="autofw"
$env:PGUSER="autofw"
$env:PGPASSWORD="autofw"
$env:PGCONNECT_TIMEOUT="3"

4. Run DB tests

pytest -m "db" -q


⸻

CI (GitHub Actions)

Workflow: .github/workflows/ci.yml

Auto jobs
	•	lint
	•	unit
	•	db

Conditional job
	•	network runs only on:
	•	schedule
	•	manual workflow dispatch

Outputs
	•	HTML test reports
	•	CI artifacts for traceability

⸻

Business Flow Capability

The project is no longer limited to single-endpoint checks.
It now supports a minimal business flow:

login -> create_user -> get_user -> update_user_status -> db assert

This flow is implemented through:
	•	autofw/services/user_service.py
	•	tests/business_flow/test_user_flow.py

This makes the project closer to real server-side testing scenarios.

⸻

Milestones

This repository also records the evolution path of the framework:
	•	Week01: one-click execution entry / gate entry
	•	Week02: failure diagnosis loop / debug playbook
	•	Week03: PostgreSQL SQL assertion layer
	•	Week04: Locust minimal performance loop
	•	Month01 Review: first-stage project review

⸻

Project Definition

This is not just a learning log or a collection of scattered scripts.

It is an API automation engineering project that gradually evolved into a mini framework with:
	•	unified entry
	•	layered execution
	•	reusable capability modules
	•	database assertions
	•	performance baseline
	•	business-flow expression
	•	CI quality gates

Its value is not only validating API correctness, but also demonstrating the path from execution-oriented testing to automation engineering and test development.

---
