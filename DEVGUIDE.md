# HOW's to

## Start the application

> NOTES: The application requires Python version 3.10 or higher

Build and activate the Python virtual environment using the pyproject.toml file.
Then, run the following command from the project's root directory to start the Flask application

```shell
python gistapi/gistapi.py
```

The Flask application will be available in debug mode at http://localhost:9876.


## Build Docker image

Executes the [build-image.sh](./build/build-image.sh) script


## Tests

Tests runs as intermediate stage inside the Docker image to prevent currupted builds.

However, you can also run it locally

```shell
# activate virtual env
pytest -v
```

> use pytest marker to un/select functional tests i.e. slower tests
> e.g. `pytest -m 'not ftest'` runs unitests only


## Code quality

You have to activate the virtual environment to run all code quality checkers

### Formatter

```shell
black .
```

### Linter

```shell
ruff .
```

> NOTES: `ruff . --ignore=E402,F403` excludes trivial import failures
