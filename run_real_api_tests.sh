#!/bin/bash
# Run LLM integration tests that call the real Anthropic API
# Note: This requires a valid ANTHROPIC_API_KEY environment variable to be set

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Error: ANTHROPIC_API_KEY environment variable is not set."
  echo "Please set it before running this script:"
  echo "export ANTHROPIC_API_KEY='your-api-key'"
  exit 1
fi

echo "Running real API integration tests..."
echo "WARNING: These tests make actual API calls that may incur costs!"
echo "Using a minimal prompt to minimize token usage."
echo ""
python -m pytest -v -m real_api tests/test_llm.py
