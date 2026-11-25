CLIENTE ?= demo-bpo

.PHONY: install test lint demo

install:
	uv sync
	npm ci

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	npm run lint
	npm run format:check

demo:
	cd dbt && uv run dbt build --profiles-dir .
	CLIENTE=$(CLIENTE) npm run build
