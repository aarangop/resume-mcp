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

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# By default, skip real API tests to avoid costs
if [ "$1" == "--all" ]; then
  echo -e "${GREEN}Running ALL tests including real API tests...${NC}"
  uv run pytest tests/ -v --cov=. --cov-report=term
else
  echo -e "${GREEN}Running tests (excluding real API calls)...${NC}"
  uv run pytest tests/ -v --cov=. --cov-report=term -k "not real_api"
fi

echo ""
echo -e "${YELLOW}To run tests including real API calls (which may incur costs):${NC}"
echo "  1. Make sure ANTHROPIC_API_KEY environment variable is set"
echo "  2. Run ./run_tests.sh --all OR ./run_real_api_tests.sh"

# Return the exit code of the test run
exit $?
