format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	python manage.py migrate

prepare-tests: prepare
	playwright install

start: prepare
	python manage.py runserver

test-ui: prepare-tests
	pytest citizen_frontend/tests/ui