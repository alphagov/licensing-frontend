# Licensing Frontend

Licensing allows citizens and businesses to apply for licences (and similar) from local and competent authorities.

There is a legal requirement that authorities offer an online mechanism to apply for certain licences and permissions.

Licensing exists for authorities which can't or don't want to offer their own licensing application.

This repository contains the citizen facing frontend of the licensing application

# Set up

## Submodules

This repository use a Git Submodule to reuse common code from `licensing-common`.

In the root of the project run `git submodule update --init --recursive` to fetch update to code.

### Updating the Submodule
To update the submodule, run `git submodule update --remote` or using the command `git pull --recurse-submodules`

Further info found [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

Alternatively: To set this as `git pull` default edit your `.gitconfig` file to include 

```
[pull]
    submoduleRecurse = true
```


## Mise

This repository uses [mise](https://mise.jdx.dev/) to manage tool versions and environment variables.

After installing mise, you should set up your shell to automatically activate mise following [these instructions](https://mise.jdx.dev/installing-mise.html#shell-specific-installation-activation), then run `mise install` and `mise trust`.

## UV

This repository uses `uv` to manage packages and dependencies. Run `make prepare` to install all necessary packages and dependencies needed
to test and run this project.

The python virtual environment should be automatically activated by mise. If it hasn't, run `source .venv/bin/activate`.

## Pre-Commit

This project uses `pre-commit`. Run `pre-commit install` to setup the correct pre-commit git hooks.

# Testing

Run `make test-ui`. This ensures dependencies are installed, starts a docker container with the app running inside,
and runs the tests against this app.
