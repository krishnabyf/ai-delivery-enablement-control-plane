.PHONY: install run test lint check docker-up docker-down

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

run:
	.venv/bin/uvicorn app.main:app --reload

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

check: lint test

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
