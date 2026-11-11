PY ?= python

.PHONY: install lint test

install:
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check src tests

test:
	$(PY) -m pytest -q --cov=weightcourt --cov-report=term
