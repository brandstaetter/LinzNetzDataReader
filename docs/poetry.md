# poetry

[Poetry](https://python-poetry.org/) is a packaging and dependency manager.
It will track all dependencies for the project, and make sure that the libraries are compatible among themselves (by using a dependency resolver).

When using poetry locally, it will automatically create a new virtual environment.
It will also automatically install the application itself as a package inside the virtual environment.

## Development setup

To install all required dependencies locally into a new virtual environment and activate it.

```shell
# install dependencies (including dev dependencies)
poetry install
# activate virtual environment
poetry shell
```

## Add new dependencies

```shell
# add new dependencies
poetry add numpy
poetry add "pandas>=1.4.0"

# add new development dependency
poetry add --dev pytest-flake8
```

## Package the project

```shell
poetry build -f wheel
```

## Setup process for a new project

You need to change some of the configuration in [pyproject.toml](../pyproject.toml).

Alternatively you can run the initialization again:

```shell
poetry init
```
