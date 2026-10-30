"""
Tavily Search Tool integration for AutoGen agents.
Provides real-time web search for destinations, accommodations, attractions, and travel advice.
"""
from typing import Optional
from config.settings import TAVILY_API_KEY
from langchain_tavily import TavilySearch
from autogen_ext.tools.langchain import LangChainToolAdapter


def create_travel_specific_search_tool(
    api_key: Optional[str] = None,
    max_results: int = 3,
) -> LangChainToolAdapter:
    """
    Create a travel-specific search tool with customized instructions.

    Args:
        api_key: Optional Tavily API key. If omitted, uses TAVILY_API_KEY from config.
        max_results: Maximum number of search results to return.

    Returns:
        LangChainToolAdapter: Wrapped Tavily search tool ready for AutoGen agents.
    """
    effective_key = api_key or TAVILY_API_KEY
    if not effective_key:
        raise ValueError(
            "TAVILY_API_KEY is missing. Please set TAVILY_API_KEY in your .env file or environment."
        )

    # Instantiate TavilySearch with travel-focused parameters
    travel_search = TavilySearch(
        tavily_api_key=effective_key,
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
        include_images=False,
        name="travel_search",
        description=(
            "Search for current travel-related information including destinations, hotels, "
            "restaurants, attractions, transportation, activities, and practical travel advice. "
            "Use this tool to find real-time, verified information for trip planning."
        ),
    )

    # Wrap for AutoGen
    return LangChainToolAdapter(travel_search)
