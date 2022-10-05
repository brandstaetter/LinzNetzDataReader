# Formatting / Linting

## Formatting

All the code is formatted via the tools `black` and `isort`.

It's possible to configure IDEs to automatically format the Python files on every save.
See the [IDE Integration](./ide_integration.md) for more information.
But the formatting is also checkt with tools like `pre-commit` and in the CI pipeline.

### `black`

`black` is an opinionated formatter. It will reformat everything to its own preference.
It is configured in [pyproject.toml](../pyproject.toml), although the options for `black` are very limited.

Besides the integration into IDEs, it's also possible to run it standalone:

```shell
black .
```

### `isort`

`isort` is a tool to automatically sort all used imports in Python files.
It groups the imports into a standard library imports block, a third party imports block, and a first party import block.
Each block is sorted in lexicographical order.

It is configured in [pyproject.toml](../pyproject.toml).

Besides the integration into IDEs, it's also possible to run it standalone:

```shell
isort .
```

## Linting

There are multiple linters enabled.

### `flake8`

`flake8` is configured in [setup.cfg](../setup.cfg).

In some cases it's necessary to circumvent `flake8`:

```python
from library import unused_object  # noqa: F401
```

### `pylint`

`pylint` is configured in [.pylintrc](../.pylintrc).

In some cases it's necessary to circumvent `pylint`:

```python
# pylint: disable=missing-docstring
# disable certain errors in the complete file

# or only disable a single line
object.with_dynamic_method(42)  # pylint: disable=no-member
```

## `pre-commit`

`pre-commit` is a framework for running various linters locally on every commit.
It creates a Git hook, that installs and runs all formatting tools and linters, and point out mistakes before a commit 
It points out annoying formatting/linter errors before the CI pipeline or a code review does.

You just need to activate it for each project where you want to use it.

```shell
# activate it in the current project
pre-commit install
```

This will run all specified linters specified in `.pre-commit-config.yaml`, and block the commit in case there is an error.
Certain linters might also modify files (e.g. reformat code), so you might need to add the changes again to Git and make the commit again.

It's also possible to `pytest` and `mypy` via the `dev` Docker image.

```shell
docker-compose build pre-commit
docker-compose run pre-commit
```
