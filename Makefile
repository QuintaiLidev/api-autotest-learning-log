# Makefile
.PHONY: help lint unit db network perf test ci clean

PYTHON ?= python
PIP ?= pip
PYTEST ?= pytest
RUFF ?= ruff
REPORTS_DIR ?= reports
LOCUST ?= locust

help:
	@echo "Targets:"
	@echo "  make lint     - ruff check ."
	@echo "  make unit     - pytest (not network/integration/db) + html report"
	@echo "  make db       - pytest db + report"
	@echo "  make network  - pytest (network or integration) + html report"
	@echo "  make perf     - locust performance test"
	@echo "  make test     - alias of unit"
	@echo "  make ci       - lint + unit"
	@echo "  make clean    - remove reports/*.html and *.csv"

lint:
	$(RUFF) check .

unit:
	mkdir -p $(REPORTS_DIR)
	$(PYTEST) -m "not (network or integration or db)" -q --html=$(REPORTS_DIR)/unit.html --self-contained-html

db:
	mkdir -p $(REPORTS_DIR)
	$(PYTEST) -m "db" -q --html=$(REPORTS_DIR)/db.html --self-contained-html

network:
	mkdir -p $(REPORTS_DIR)
	$(PYTEST) -m "(network or integration) and not db" -q --html=$(REPORTS_DIR)/network.html --self-contained-html

perf:
	mkdir -p $(REPORTS_DIR)
	$(LOCUST) -f perf/locustfile.py --headless \
		-u 10 -r 2 -t 60s \
		--host https://postman-echo.com \
		--csv $(REPORTS_DIR)/locust \
		--html $(REPORTS_DIR)/locust.html

test: unit
ci: lint unit

clean:
	rm -f $(REPORTS_DIR)/*.html $(REPORTS_DIR)/*.csv