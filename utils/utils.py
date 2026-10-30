"""
Helper utility functions for the AutoGen Travel Planner application.
"""
import json
from typing import Any
from autogen_agentchat.conditions import TextMentionTermination
from config.settings import TERMINATION_WORD


def save_state(agent: Any, filename: str) -> None:
    """Save the state of an agent or team to a JSON file."""
    state = agent.save_state()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_state(agent: Any, filename: str) -> None:
    """Load the state of an agent or team from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        state = json.load(f)
    agent.load_state(state)


def get_termination_condition() -> TextMentionTermination:
    """
    Create a termination condition that halts the chat when the termination word is mentioned.
    """
    return TextMentionTermination(TERMINATION_WORD)
