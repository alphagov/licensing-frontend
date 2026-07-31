format:
	uv run ruff check --fix && uv run ruff format

prepare:
	uv sync
	python manage.py migrate

prepare-tests: prepare
	playwright install

start: prepare
	nohup python manage.py runserver 0.0.0.0:8000 &

test-ui: prepare-tests
	make start
	echo "Waiting for Django to start..."
	while ! nc -z localhost 8000; do sleep 0.5; done
	pytest citizen_frontend/tests/ui

kill:
	lsof -ti :8000 | xargs kill