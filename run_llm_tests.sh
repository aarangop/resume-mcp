#!/bin/bash
# Run LLM integration tests

# By default, skip real API tests to avoid costs
if [ "$1" == "--all" ]; then
    echo "Running ALL LLM integration tests, including real API calls..."
    python -m pytest tests/test_llm.py -v
else
    echo "Running LLM integration tests (skipping real API calls)..."
    python -m pytest tests/test_llm.py -v -k "not real_api"
fi

echo ""
echo "To run tests including real API calls (which may incur costs):"
echo "  1. Make sure ANTHROPIC_API_KEY environment variable is set"
echo "  2. Run ./run_llm_tests.sh --all OR ./run_real_api_tests.sh"
