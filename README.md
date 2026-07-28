# Licensing Frontend

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

This repository contains the citizen facing frontend of the licensing application

## Set up

This repository uses `uv` to manage packages and dependencies. Run `uv sync` to install all necessary packages and dependencies needed
to test and run this project.
If a python virtual environment has not been activated for you; run `source .venv/bin/activate`.

This project also uses `pre-commit` run `pre-commit install` to create the correct pre-commit git hooks.

## Testing

This repository uses `playwright` to test the UI.
The server must running for the tests to run, to do this run `make start` in a separate terminal.
Then, to run the UI tests, run `make test-ui`.
