# Testing

## Tests

Tests are run with the `pytest` framework.
`pytest` will pick up any functions with the prefix `test_` in the files with the prefix `test_` in the `tests` directory.
You run `pytest` with:

```shell
$ pytest
======================================= test session starts ========================================
platform linux -- Python 3.9.6, pytest-7.0.1, pluggy-1.0.0
rootdir: /home/user/dev/python-template, configfile: pyproject.toml, testpaths: tests
plugins: anyio-3.5.0
collected 1 item

tests/test_api.py .                                                                          [100%]

======================================== 1 passed in 0.22s =========================================
```

`pytest` is configured in the [pyproject.toml](../pyproject.toml) and in the [conftest.py](../conftest.py) file.

## Static type checking

Types are checked with `mypy`.

```console
$ mypy
Success: no issues found in 3 source files
```

`mypy` is configured in [pyproject.toml](../pyproject.toml).
It's configured to be quite strict, e.g. every function needs to be fully typed.

In some cases it's necessary to circumvent `mypy`:

```python
object.with_dynamic_method(42)  # type: ignore[attr-defined]
```

## Docker

It's also possible to `pytest` and `mypy` via the `dev` Docker image.

```console
$ docker-compose build dev
$ docker-compose run dev
```
