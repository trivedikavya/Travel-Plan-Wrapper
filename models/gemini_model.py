"""
Google Gemini model client integration for AutoGen agents.
Connects to Google AI Studio using the official Gemini endpoint.
"""
from typing import Optional
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from autogen_ext.models.openai import OpenAIChatCompletionClient

DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def create_gemini_model_client(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_GEMINI_BASE_URL,
) -> OpenAIChatCompletionClient:
    """
    Create an AutoGen ChatCompletionClient configured for Google Gemini via Google AI Studio.

    Args:
        model: Gemini model identifier (e.g. 'gemini-2.5-flash'). Defaults to GEMINI_MODEL setting.
        api_key: Gemini API key. Defaults to GEMINI_API_KEY setting.
        base_url: Google AI Studio OpenAI-compatible endpoint.

    Returns:
        OpenAIChatCompletionClient configured for Gemini.
    """
    effective_model = model or GEMINI_MODEL or "gemini-2.5-flash"
    effective_key = api_key or GEMINI_API_KEY

    if not effective_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment."
        )

    return OpenAIChatCompletionClient(
        model=effective_model,
        api_key=effective_key,
        base_url=base_url,
        max_retries=5,
        timeout=60.0,
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": "gemini",
            "structured_output": True,
        },
    )


# Default model client instance for AutoGen agents
# If GEMINI_API_KEY is not yet set in environment, defer instantiation until called
try:
    if GEMINI_API_KEY:
        model_client = create_gemini_model_client()
    else:
        model_client = None
except Exception:
    model_client = None
