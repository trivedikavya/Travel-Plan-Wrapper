"""
Travel Planning Team definition.
Coordinates the Travel Planner and Researcher agents in a Round-Robin multi-agent collaboration.
"""
from typing import Optional
from autogen_agentchat.teams import RoundRobinGroupChat
from agents.planner import planner_agent, create_planner_agent
from agents.researcher import research_agent, create_researcher_agent
from config.settings import MAX_TURN
from utils.utils import get_termination_condition


def create_travel_team(
    planner=None,
    researcher=None,
    max_turns: int = MAX_TURN,
) -> RoundRobinGroupChat:
    """
    Create a new instance of the collaborative Round-Robin travel planning team.

    Args:
        planner: Travel Planner agent instance. If None, creates a new one.
        researcher: Researcher agent instance. If None, creates a new one.
        max_turns: Maximum conversation turns between agents.

    Returns:
        RoundRobinGroupChat: Configured multi-agent team.
    """
    effective_planner = planner or planner_agent or create_planner_agent()
    effective_researcher = researcher or research_agent or create_researcher_agent()

    return RoundRobinGroupChat(
        participants=[effective_planner, effective_researcher],
        name="Travel_Planning_Team",
        description=(
            "A collaborative team that helps users plan trips by researching destinations, "
            "creating itineraries, and providing verified travel tips."
        ),
        termination_condition=get_termination_condition(),
        max_turns=max_turns,
    )


# Default module-level instance for direct import
try:
    team = create_travel_team()
except Exception:
    team = None