import asyncio
import os
import anthropic


async def call_anthropic(prompt: str) -> str:
    """Call Anthropic API"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise Exception("Anthropic api key not found")

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = await client.messages.create(
        model=os.getenv('ANTHROPIC_MODEL', 'claude-3-7-sonnet-20250219'),
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text  # type: ignore


async def test_simple():
    """Simple async test function"""
    prompt = "Say 'Hello Andres', nothing more."
    try:
        response = await call_anthropic(prompt)
        print(f"Response: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Fix: Use asyncio.run() to execute async function
    print("Testing call_anthropic function...")
    result = asyncio.run(test_simple())
    print(f"Final result: {result}")
