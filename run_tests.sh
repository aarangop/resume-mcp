#!/usr/bin/env bash
# Run integration tests for the resume-mcp project

# Ensure the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Virtual environment not activated. Please activate it first."
  echo "Example: source .venv/bin/activate"
  exit 1
fi

# Install test dependencies if needed
uv pip install -e ".[test]"

# Run the tests with coverage
uv run pytest tests/ -v --cov=. --cov-report=term

# Return the exit code of the test run
exit $?
