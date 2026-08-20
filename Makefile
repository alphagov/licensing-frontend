format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	python manage.py migrate
	playwright install

start:
	docker compose up -d

watch:
	docker compose up --watch

test-ui: start
	pytest citizen_frontend/tests/ui

kill:
	docker compose down

remove-image:
	docker image rm licensing-frontend-citizen_frontend

test-ui-ci:
	uv sync
	python -m playwright install --with-deps
	mise exec -- docker compose up -d
	mise exec -- pytest citizen_frontend/tests/ui