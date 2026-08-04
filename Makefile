format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	python manage.py migrate
	playwright install

start: prepare
	docker compose up -d --watch

test-ui: start
	pytest citizen_frontend/tests/ui

kill:
	docker compose down

test-ui-ci:
	uv sync
	playright install
	docker compose up -d
	pytest citizen_frontend/tests/ui