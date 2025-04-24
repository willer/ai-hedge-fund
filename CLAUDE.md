# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands
- Install dependencies: `poetry install`
- Run hedge fund: `poetry run python src/main.py --ticker <TICKER_SYMBOLS>`
- Run backtester: `poetry run python src/backtester.py --ticker <TICKER_SYMBOLS>`
- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Lint code: `poetry run flake8 .`
- Run tests: `poetry run pytest`
- Run single test: `poetry run pytest path/to/test_file.py::test_function`

## Code Style Guidelines
- Use Python type hints for function parameters and return values
- Follow Black formatting with line length of 420 characters
- Use meaningful function and variable names
- Handle errors with specific exception types and detailed error messages
- Use docstrings for all public functions and classes
- Follow import order: standard library, third-party, local application
- JSON parsing should handle exceptions as seen in `parse_hedge_fund_response`
- For agent implementations, use existing patterns in the `agents` directory
- Return None with helpful error messages instead of raising exceptions
- Use f-strings for string formatting
- Organize related functionality into modules
- Maintain consistent naming conventions: snake_case for functions/variables, PascalCase for classes
