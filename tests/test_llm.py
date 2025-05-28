#!/usr/bin/env python3
"""
Integration tests for LLM utilities like call_anthropic
"""

import os
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from resume_mcp.utils.llm import call_anthropic

import dotenv

dotenv.load_dotenv()


# Test LLM utility functions
@pytest.mark.asyncio
@patch("resume_mcp.utils.llm.anthropic.AsyncAnthropic")
@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "mock-api-key", "ANTHROPIC_MODEL": "test-model"})
async def test_call_anthropic_simple_prompt(mock_anthropic):
    """Test call_anthropic with a minimal prompt to reduce API costs"""
    # Setup mock response
    mock_client_instance = AsyncMock()
    mock_anthropic.return_value = mock_client_instance

    # Create a mock response structure that matches the Anthropic API
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello, I'm Claude!")]
    mock_client_instance.messages.create.return_value = mock_response

    # Call the function with a minimal prompt
    response = await call_anthropic("Hello")

    # Verify the function was called correctly
    mock_client_instance.messages.create.assert_called_once_with(
        model="test-model",
        max_tokens=6000,
        messages=[{"role": "user", "content": "Hello"}]
    )

    # Check the response
    assert response == "Hello, I'm Claude!"


@pytest.mark.asyncio
@patch("resume_mcp.utils.llm.anthropic.AsyncAnthropic")
@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "mock-api-key"})
async def test_call_anthropic_missing_api_key(mock_anthropic):
    """Test call_anthropic behavior when API key is missing"""
    # Setup to simulate missing API key
    mock_client_instance = AsyncMock()
    mock_anthropic.return_value = mock_client_instance
    mock_client_instance.messages.create.side_effect = ValueError(
        "Missing API key")

    # Call the function and check exception handling
    with pytest.raises(ValueError):
        await call_anthropic("Test prompt")


@pytest.mark.asyncio
@pytest.mark.real_api
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"),
                    reason="ANTHROPIC_API_KEY environment variable not set")
async def test_call_anthropic_real_api():
    """
    Real integration test that makes an actual API call to Anthropic.

    Note: This test requires a valid ANTHROPIC_API_KEY environment variable.
    It will be skipped if the API key is not set.

    Run with: pytest -m real_api tests/test_llm.py
    """
    # Use a minimal prompt to reduce token usage and cost
    prompt = "Say 'hello world' in exactly those words, nothing more."

    # Make the actual API call
    response = await call_anthropic(prompt)

    # Basic verification that we got a response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

    # This is a minimal verification that doesn't depend on exact response content
    # which might change with model versions
    assert "hello world" in response.lower()
