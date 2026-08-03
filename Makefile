format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	python manage.py migrate
	playwright install

start: build-image
	docker compose up -d

build-image: prepare
	docker build -t citizen-frontend .


test-ui:
	make start
	pytest citizen_frontend/tests/ui

kill:
	docker compose down