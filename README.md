# Licensing Frontend

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

This repository contains the citizen facing frontend of the licensing application

# Set up

This repository uses `uv` to manage packages and dependencies. Run `uv sync` to install all necessary packages and dependencies needed
to test and run this project.
If a python virtual environment has not been activated for you; run `source .venv/bin/activate`.

This project also uses `pre-commit` run `pre-commit install` to create the correct pre-commit git hooks.

## Direnv

Get direnv to load required environment variables automatically by setting up the [direnv hook](https://direnv.net/docs/hook.html) to run when your shell starts up.
Create a `.envrc` file in the root of this project, and copy the contents of `dev.envrc` into this file.
Allow direnv to load environment variables from this directory with `direnv allow .`

# Testing

Run `make test-ui`. This ensures dependencies are installed, starts a docker container with the app running inside,
and runs the tests against this app.
