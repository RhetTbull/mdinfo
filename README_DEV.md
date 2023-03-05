# Notes for Developers

These are notes to remind me how to do things on this project.

## Installation

mdinfo uses [poetry](https://python-poetry.org/) for dependency management.

Install poetry:

    `pip install poetry`

To install the dependencies, run:

    `poetry install`

## Building

mdinfo uses [doit](https://pydoit.org/) for building.

To build the project, run:

    `doit`

## Testing

mdinfo uses [pytest](https://docs.pytest.org/en/stable/) for testing.
The test suite can be run with the following command:

    `poetry run pytest`
    
or

    `doit test`

## README update

The README.md is updated automatically using [cogapp](https://nedbatchelder.com/code/cog/).
The README.md will be updated when running `doit`.