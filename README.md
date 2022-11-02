[![Docker App Image CI](https://github.com/brandstaetter/LinzNetzDataReader/actions/workflows/docker-app-image.yml/badge.svg)](https://github.com/brandstaetter/LinzNetzDataReader/actions/workflows/docker-app-image.yml)

## Local Setup

###	Requirements

We need a couple of tools (`pre-commit` and `poetry`) installed globally.
For that we advice using `pipx` (Python Application Manager).
`pipx` installs each tool in it's own virtual environment and exposes the tool by manipulating the `PATH`.

```shell
# install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# install requirements
pipx install poetry
pipx install pre-commit
```

### Virtual environment and dependencies

We use `poetry` to manage the virtual environment and also the dependencies.

```shell
# create virtual environment and install dependencies
poetry install
# activate the virtual environment
poetry shell
```

See the usage details in the [poetry](./docs/poetry.md) documentation.

### pre-commit

`pre-commit` is a framework for running various linters locally on every commit.
It points out annoying formatting/linter errors before the CI pipeline or a code review does.

```shell
# activate it in project
pre-commit install
```

This will run all specified linters in `.pre-commit-config.yaml`, and block the commit in case there is an error. Certain linters might also modify files (e.g. reformat code), so you might need to add the changes again to Git and make the commit again.

See the usage details in the [Formatting / Linting](./docs/formatting-linting.md) documentation.

### IDE integration

See the [IDE Integration](./docs/ide_integration.md) documentation.

## Run

### Run server

```shell
# start the server
uvicorn data_analyzer.main:app --port 8080
# or simply run main.py
```

### Run tests and static code analysis

```shell
# run tests
pytest
# run mypy
mypy 
```

See more usage details and configuration in the [Testing](./docs/testing.md) documentation.

### Run Docker container

```shell
# run and build the application
docker-compose build app
docker-compose run app

# run tests
docker-compose build dev
docker-compose run dev

# run pre-commit in Docker
docker-compose build pre-commit
docker-compose run pre-commit
```

### Run the database

Create a .env file in the root of the project containing the following:
```
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataanalyzer
```
and run
```
docker-compose run -d postgres
```
