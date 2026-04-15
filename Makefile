PYTHON ?= python
SRC_DIRS := app scripts migrate.py

.PHONY: help install install-dev format lint ci run list-dialogs list-topics-src list-topics-dst build-mapping clean

help:
	@echo "Доступные команды:"
	@echo ""
	@echo "  make install          — установить проект (pip install -e .)"
	@echo "  make install-dev      — установить проект + дев-зависимости (линтеры)"
	@echo ""
	@echo "  make format           — отформатировать код: black + isort"
	@echo "  make lint             — прогнать все линтеры (black/isort/flake8/pylint/mypy)"
	@echo "  make ci               — то же, что делает CI (check-only)"
	@echo ""
	@echo "  make run              — запустить миграцию (migrate.py)"
	@echo "  make list-dialogs     — вывести список чатов с id"
	@echo "  make list-topics-src  — вывести темы исходного чата"
	@echo "  make list-topics-dst  — вывести темы целевого чата"
	@echo "  make build-mapping    — сгенерировать topic_mapping.json"
	@echo ""
	@echo "  make clean            — удалить кэши (__pycache__, .mypy_cache и т.п.)"

install:
	$(PYTHON) -m pip install -e .

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt

format:
	$(PYTHON) -m black $(SRC_DIRS)
	$(PYTHON) -m isort $(SRC_DIRS)

lint: ci

ci:
	$(PYTHON) -m black --check $(SRC_DIRS)
	$(PYTHON) -m isort --check-only $(SRC_DIRS)
	$(PYTHON) -m flake8 $(SRC_DIRS)
	$(PYTHON) -m pylint $(SRC_DIRS)
	$(PYTHON) -m mypy $(SRC_DIRS)

run:
	$(PYTHON) migrate.py

list-dialogs:
	$(PYTHON) scripts/list_dialogs.py

list-topics-src:
	$(PYTHON) scripts/list_topics.py src

list-topics-dst:
	$(PYTHON) scripts/list_topics.py dst

build-mapping:
	$(PYTHON) scripts/build_mapping.py

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -not -path "./venv/*" -exec rm -rf {} +
