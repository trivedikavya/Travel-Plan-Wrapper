"""
Researcher Agent.
Supports the Travel Planner by validating travel details, verifying logistics, and finding sources.
"""
from typing import Optional, List
from autogen_agentchat.agents import AssistantAgent
from config.settings import TERMINATION_WORD
from models.gemini_model import model_client, create_gemini_model_client
from utils.tools import create_travel_specific_search_tool

RESEARCHER_SYSTEM_MESSAGE = f"""You are a meticulous Travel Researcher agent powered by Google Gemini.
Your role is to support the Travel Planner by verifying facts, validating logistical details, and ensuring quality.

Guidelines for research support:
1. Review the Travel Planner's proposed itinerary and recommendations.
2. If travel search tools are available, verify transit feasibility, opening days, seasonal considerations, and local tips.
3. Validate important claims and ensure recommendations are practical and grounded.
4. Avoid repeating what the Travel Planner has already stated; focus on adding missing nuances, practical tips, or verified warnings.
5. If the Travel Planner has provided a clear itinerary, review it, add 2-3 essential tips, and conclude your response with '{TERMINATION_WORD}' to finish the session. If the Planner has not yet provided the itinerary, ask them to generate the complete plan first."""


def create_researcher_agent(
    client=None,
    tools: Optional[List] = None,
) -> AssistantAgent:
    """
    Create a new instance of the Researcher agent.

    Args:
        client: AutoGen model client. If None, uses default Gemini model_client.
        tools: Optional tools for research. If None, initializes travel search tool if available.

    Returns:
        AssistantAgent: Configured Researcher agent.
    """
    effective_client = client or model_client or create_gemini_model_client()
    if tools is None:
        try:
            tools = [create_travel_specific_search_tool()]
        except Exception:
            tools = []

    return AssistantAgent(
        name="Researcher",
        description="A researcher agent that supports the Travel Planner by validating information and checking travel details.",
        model_client=effective_client,
        tools=tools,
        reflect_on_tool_use=True,
        max_tool_iterations=2,
        system_message=RESEARCHER_SYSTEM_MESSAGE,
    )


# Default module-level instance for direct import
try:
    research_tools = [create_travel_specific_search_tool()]
except Exception:
    research_tools = []

try:
    research_agent = create_researcher_agent(client=model_client, tools=research_tools)
except Exception:
    research_agent = None