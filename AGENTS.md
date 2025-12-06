# For AI Agents

This document provides a summary of the project for AI agents and assistants.

## Project Name
mappingtools

## Project Description
A Python library with utility functions for manipulating and transforming data structures with Mapping-like characteristics. It can invert dictionaries, convert objects to dictionaries, create nested defaultdicts, and more.

## Technologies Used
- Python
- hatchling (for building)
- pytest (for testing)
- ruff (for linting)

## File Structure
The core logic is located in `src/mappingtools`. This directory is organized into three main namespaces:
- `collectors`: Classes for collecting and categorizing data.
- `operators`: Functions that perform operations on mappings.
- `transformers`: Functions that reshape objects.

Tests for the project are located in the `tests` directory.

## Key Commands

To lint the project:
```shell
ruff check src
ruff check tests
```

To run the test suite:
```shell
python -m pytest tests --cov=src --cov-branch --doctest-modules --cov-report=term
```
