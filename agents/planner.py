"""
Travel Planner Agent.
Creates comprehensive, structured travel itineraries using real-time Tavily search and Gemini.
"""
from typing import Optional, List
from autogen_agentchat.agents import AssistantAgent
from models.gemini_model import model_client, create_gemini_model_client
from utils.tools import create_travel_specific_search_tool

PLANNER_SYSTEM_MESSAGE = """You are a professional Travel Planner agent powered by Google Gemini.
Your mission is to help travelers by creating comprehensive, realistic, and well-structured travel itineraries.

Guidelines for creating travel plans:
1. Understand the traveler's destination, duration, budget, and preferences from the request.
2. Use the travel search tool to research current information about attractions, hotels, dining, and transit.
3. Produce a structured day-by-day itinerary with:
   - Morning, Afternoon, and Evening activities
   - Recommended accommodations and neighborhood suggestions
   - Distinct restaurant recommendations for meals
   - Practical transportation advice (metro, trains, walking, rideshare)
4. Clearly distinguish verified information from estimates (e.g. approximate costs vs fixed ticket prices).
5. Include source URLs or references for recommendations when available from search results.
6. Do not invent live hotel availability, fake booking confirmations, or unverified opening hours.
7. Always provide actionable, specific recommendations rather than raw search dumps.

Once the itinerary is detailed and structured, present it clearly and collaborate with the Researcher to verify details."""


def create_planner_agent(
    client=None,
    tools: Optional[List] = None,
) -> AssistantAgent:
    """
    Create a new instance of the Travel Planner agent.

    Args:
        client: AutoGen model client. If None, uses default Gemini model_client.
        tools: List of tools available to the agent. If None, initializes travel search tool.

    Returns:
        AssistantAgent: Configured Travel Planner agent.
    """
    effective_client = client or model_client or create_gemini_model_client()
    if tools is None:
        try:
            tools = [create_travel_specific_search_tool()]
        except Exception:
            tools = []

    return AssistantAgent(
        name="Travel_Planner",
        description="A travel planner agent that helps users plan their trips using real-time travel information.",
        model_client=effective_client,
        tools=tools,
        reflect_on_tool_use=True,
        max_tool_iterations=2,
        system_message=PLANNER_SYSTEM_MESSAGE,
    )


# Default module-level instances for direct import
try:
    travel_search_tool = create_travel_specific_search_tool()
    planner_agent = create_planner_agent(client=model_client, tools=[travel_search_tool])
except Exception:
    travel_search_tool = None
    planner_agent = None