# IoC

[//]: # ([![Stable Version]&#40;https://img.shields.io/pypi/v/bootstrap-python-package?color=blue&#41;]&#40;https://pypi.org/project/bootstrap-python-package/&#41;)
[![stability-wip](https://img.shields.io/badge/stability-wip-lightgrey.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#work-in-progress)

[![Python 3.8](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.8.yml/badge.svg?event=push)](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.8.yml)
[![Python 3.9](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.9.yml/badge.svg?event=push)](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.9.yml)
[![Python 3.10](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.10.yml/badge.svg?event=push)](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.10.yml)
[![Python 3.11](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.11.yml/badge.svg?event=push)](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.11.yml)
[![Python 3.12](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.12.yml/badge.svg?event=push)](https://github.com/febus982/bootstrap-python-package/actions/workflows/python-3.12.yml)

[![Maintainability](https://api.codeclimate.com/v1/badges/69f51e1b5cfc67c7cfc5/maintainability)](https://codeclimate.com/github/febus982/python-ioc/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/69f51e1b5cfc67c7cfc5/test_coverage)](https://codeclimate.com/github/febus982/python-ioc/test_coverage)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

This project is a framework that implements Inversion of Control and [Dependency Inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle).
Dependencies can be resolved in two different ways:

* Invoking directly the IoC Container ([Service Locator pattern](https://en.wikipedia.org/wiki/Service_locator_pattern))
* Using the [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection) helpers

## How to use the framework

### Register the dependencies

`TODO`

### Resolve the dependencies

`TODO`

## Commands for development

* `make dev-dependencies`: Install dev requirements
* `make test`: Run test suite
* `make check`: Run tests, code style and lint checks
* `make fix`: Run code style and lint automatic fixes (where possible)
* `make docs`: Render the mkdocs website locally
