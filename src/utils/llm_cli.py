"""CLI-based LLM wrapper for using subscription-based CLI tools instead of API calls.

Supports:
- claude -p "prompt" (Claude CLI)
- gemini -p "prompt" (Gemini CLI)
- codex exec "prompt" (OpenAI Codex CLI)
"""

import subprocess
import json
import re
from pydantic import BaseModel


# AIDEV-NOTE: Maps model providers to their CLI commands and argument formats
CLI_PROVIDERS = {
    "anthropic": {"cmd": "claude", "args": ["-p"], "name": "Claude"},
    "google": {"cmd": "gemini", "args": ["-y", "-p"], "name": "Gemini"},
    "openai": {"cmd": "codex", "args": ["exec"], "name": "Codex"},
    # Fallback - use claude for unknown providers
    "default": {"cmd": "claude", "args": ["-p"], "name": "Claude"},
}


def get_cli_config(model_provider: str) -> dict:
    """Get CLI configuration for the given provider."""
    provider_lower = model_provider.lower()

    # Map provider names to CLI configs
    if "anthropic" in provider_lower or "claude" in provider_lower:
        return CLI_PROVIDERS["anthropic"]
    elif "google" in provider_lower or "gemini" in provider_lower:
        return CLI_PROVIDERS["google"]
    elif "openai" in provider_lower or "gpt" in provider_lower or "codex" in provider_lower:
        return CLI_PROVIDERS["openai"]
    else:
        return CLI_PROVIDERS["default"]


def call_llm_cli(
    prompt: str,
    pydantic_model: type[BaseModel],
    model_provider: str = "anthropic",
    timeout: int = 300,
) -> BaseModel:
    """
    Call an LLM via CLI tools instead of API.

    Args:
        prompt: The prompt to send (will be augmented with JSON instructions)
        pydantic_model: Pydantic model class for structured output
        model_provider: Provider name to determine which CLI to use
        timeout: Timeout in seconds (default 5 minutes)

    Returns:
        Instance of the pydantic_model populated with LLM response
    """
    cli_config = get_cli_config(model_provider)

    # Build the augmented prompt requesting JSON output
    json_schema = pydantic_model.model_json_schema()
    augmented_prompt = f"""{prompt}

IMPORTANT: You must respond with valid JSON that matches this schema:
{json.dumps(json_schema, indent=2)}

Respond ONLY with the JSON object, no markdown code blocks, no explanation."""

    # Build command
    cmd = [cli_config["cmd"]] + cli_config["args"] + [augmented_prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise Exception(f"CLI command failed: {result.stderr}")

        response_text = result.stdout.strip()

        # Try to parse the response as JSON
        parsed = extract_json_from_cli_response(response_text)
        if parsed:
            return pydantic_model(**parsed)

        # If extraction failed, raise an error
        raise Exception(f"Could not extract valid JSON from CLI response: {response_text[:500]}")

    except subprocess.TimeoutExpired:
        raise Exception(f"CLI command timed out after {timeout} seconds")
    except FileNotFoundError:
        raise Exception(f"CLI tool '{cli_config['cmd']}' not found. Please ensure it's installed and in PATH.")


def extract_json_from_cli_response(content: str) -> dict | None:
    """
    Extract JSON from CLI response, handling various formats.

    Tries multiple strategies:
    1. Direct JSON parse
    2. Extract from markdown code blocks
    3. Find JSON object pattern in text
    """
    content = content.strip()

    # Strategy 1: Direct parse (response is pure JSON)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code blocks
    # Try ```json first
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try ``` without language specifier
    code_match = re.search(r'```\s*([\s\S]*?)\s*```', content)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find JSON object pattern (first { to last })
    brace_start = content.find('{')
    brace_end = content.rfind('}')
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return json.loads(content[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    return None


def is_cli_available(provider: str = "anthropic") -> bool:
    """Check if the CLI tool for the given provider is available."""
    cli_config = get_cli_config(provider)
    try:
        result = subprocess.run(
            ["which", cli_config["cmd"]],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False
