format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	playwright install

start:
	mise exec -- docker compose up -d
	nohup mise exec -- docker compose watch > /dev/null 2>&1 &

watch:
	mise exec -- docker compose up --watch

test-ui: start prepare
	DOCUMENTDB_HOST=127.0.0.1 pytest citizen_frontend/tests/ui

kill:
	pkill -f "docker compose watch"
	docker compose down && \
	cd licensing_common && docker compose down

remove-image:
	docker image rm licensing-frontend-citizen_frontend

test-ui-ci:
	uv sync
	python -m playwright install --with-deps
	docker compose up -d
	pytest citizen_frontend/tests/ui

test-common:
	cd licensing_common && \
	make prepare-tests && \
	pytest


test-api: prepare
	pytest citizen_frontend/tests/api --ignore citizen_frontend/tests/api/end_to_end

test-services: prepare
	pytest citizen_frontend/tests/services