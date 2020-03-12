<!--
# SPDX-FileCopyrightText: (c) 2019-2025 Siemens
# SPDX-License-Identifier: MIT
-->

# SW360 Base Library for Python

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/sw360/sw360python/blob/master/License.md)
[![Python Version](https://img.shields.io/badge/python-3.8%2C3.9%2C3.10%2C3.11-yellow?logo=python)](https://www.python.org/doc/versions/)
[![PyPI](https://shields.io/pypi/v/sw360)](https://pypi.org/project/sw360/)
[![Static checks](https://github.com/sw360/sw360python/actions/workflows/static-checks.yml/badge.svg)](https://github.com/sw360/sw360python/actions/workflows/static-checks.yml)
[![Unit tests](https://github.com/sw360/sw360python/actions/workflows/unit-test.yml/badge.svg)](https://github.com/sw360/sw360python/actions/workflows/unit-test.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/tngraf/6ab639b6f9d1f6161d3db52d348d2997/raw/666fa870981726e1fa3469b6aa668c20fdd9d1b2/sw360python-cobertura-coverage.json&color=green)](https://github.com/sw360/sw360python/actions/workflows/unit-test.yml)
[![REUSE status](https://api.reuse.software/badge/git.fsfe.org/reuse/api)](https://api.reuse.software/info/git.fsfe.org/reuse/api)

This Python project implements the REST API of [SW360](https://www.eclipse.org/sw360/)
and allows an easy way to interact with SW360.

## Documentation

Have a look at the documentation: https://sw360.github.io/sw360python/

The [`SW360`](https://sw360.github.io/sw360python/index.html#sw360.SW360) class
provides the main interface.

In [`sw360_objects.py`](./sw360/sw360_objects.py), there's also a preview of a
high-level API, but note this is read-only and incomplete for now.

## Usage

### Installation

This project is available as [Python package on PyPi.org](https://pypi.org/project/sw360/).  
Install sw360 and required dependencies:

```shell
  pip install sw360 requests
  ```

### Using the API

* Get a REST API token from your SW360 server
* Export required environment variables (optionally but recommended):

  ```shell
  export SW360ProductionToken=<your_api_token>
  ```

* Start using the API:

  ```python
  import sw360
  client = sw360.SW360(sw360_url, sw360_api_token)
  ```

### Contribute

* All contributions in form of bug reports, feature requests or merge requests!
* Use proper [docstrings](https://realpython.com/documenting-python-code/) to document  
  functions and classes
* Extend the testsuite **poetry run pytest** with the new functions/classes
* The **documentation website** can automatically be generated by the [Sphinx autodoc extension](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)

### Build

#### Building the Documentation

The documentation of the project is built using Sphinx:

```python
poetry run sphinx-build ./docs-source/ ./docs/
```

#### Building Python package

For building the library, you need [Poetry](https://python-poetry.org/).  
The build is then triggered using

```shell
poetry build
```

This creates the source and wheel files in ```dist/``` subdirectory -- which can then be  
uploaded or installed locally using ```pip```.

## Test

Start the complete test suite or a specific test case (and generate coverage report):

```shell
poetry run pytest
```

or

```shell
poetry run coverage run -m pytest
poetry run coverage report -m --omit "*/site-packages/*.py"
poetry run coverage html --omit "*/site-packages/*.py"
```

## Demo

The script ``check_project.py`` shows how to use the library to retrieve some information  
of a given project on SW360. This requires colorama>=0.4.1.

## License

Copyright 2019-2025 Siemens

The project is licensed under the MIT license.
SPDX-License-Identifier: MIT

## SBOM

For an up-to-date CycloneDX SBOM, please have a look at the
[SBOM](https://github.com/sw360/sw360python/tree/master/SBOM) folder.
