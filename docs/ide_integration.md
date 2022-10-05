# IDE Integration

## VS Code

Install the official [Microsoft Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python).

VS Code is preconfigured via [.vscode/settings.json](../.vscode/settings.json) to automatically format the file with `black` and `isort` on every file save.
It will also show you linting errors with `flake8`, type errors with `mypy` and `p

VS Code will automatically detect the virtual environment.
But it's also possible to set it manually with <kbd>Ctrl</kbd> + <kbd>P</kbd>, "Python: Select Interpreter", and choosing the path to the Python binary in the new virtual environment.
