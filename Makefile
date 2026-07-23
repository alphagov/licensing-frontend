format:
	uv run ruff check --fix && uv run ruff format

start:
	python manage.py runserver

test-ui:
	pytest citizen_frontend/tests/ui