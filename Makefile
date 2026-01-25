.PHONY: help lint unit network test ci clean

PYTHON ?= python
PIP ?= pip
PYTEST ?= pytest
RUFF ?= ruff
REPORTS_DIR ?= reports

help:
	@echo "Targets:"
	@echo "  make lint     - ruff check ."
	@echo "  make unit     - pytest (not network/integration) + html report"
	@echo "  make network  - pytest (network or integration) + html report"
	@echo "  make test     - alias of unit"
	@echo "  make ci       - lint + unit"
	@echo "  make clean    - remove reports/*.html"

lint:
	$(RUFF) check .

unit:
	mkdir -p $(REPORTS_DIR)
	$(PYTEST) -m "not (network or integration)" -q --html=$(REPORTS_DIR)/unit.html --self-contained-html

network:
	mkdir -p $(REPORTS_DIR)
	$(PYTEST) -m "network or integration" -q --html=$(REPORTS_DIR)/network.html --self-contained-html

test: unit

ci: lint unit

clean:
	rm -f $(REPORTS_DIR)/*.html
