"""
Unit test suite for AutoGen Travel Planner.
Validates configuration, Gemini client, Tavily tool, agents, team, and safe result parsing.
"""
import pytest
from unittest.mock import MagicMock, patch

from config.settings import validate_config, GEMINI_MODEL, MAX_TURN
from models.gemini_model import create_gemini_model_client, DEFAULT_GEMINI_BASE_URL
from utils.tools import create_travel_specific_search_tool
from agents.planner import create_planner_agent
from agents.researcher import create_researcher_agent
from teams.travel_team import create_travel_team
from main import parse_structured_data, format_travel_content, format_search_result, get_user_request


# 1. Configuration tests
def test_configuration_loading():
    """Verify configuration settings and defaults."""
    assert GEMINI_MODEL is not None
    assert "gemini" in GEMINI_MODEL.lower()
    assert MAX_TURN > 0


# 2. Missing keys validation tests
def test_missing_keys_produce_errors():
    """Verify that missing Gemini or Tavily keys produce clear validation errors."""
    with patch("config.settings.GEMINI_API_KEY", None), patch("config.settings.TAVILY_API_KEY", None):
        errors = validate_config(require_keys=False)
        assert len(errors) == 2
        assert any("GEMINI_API_KEY" in err for err in errors)
        assert any("TAVILY_API_KEY" in err for err in errors)

        with pytest.raises(ValueError) as excinfo:
            validate_config(require_keys=True)
        assert "GEMINI_API_KEY" in str(excinfo.value)
        assert "TAVILY_API_KEY" in str(excinfo.value)


# 3. Gemini model client initialization tests
def test_gemini_model_client_initialization():
    """Verify Gemini model client is configured with expected parameters."""
    client = create_gemini_model_client(
        model="gemini-2.5-flash",
        api_key="test-gemini-key",
    )
    assert client is not None
    # Verify capabilities and model info
    info = client.model_info
    assert info.get("function_calling") is True
    assert info.get("vision") is True


def test_gemini_model_client_missing_key():
    """Verify creating Gemini client without key raises descriptive ValueError."""
    with patch("models.gemini_model.GEMINI_API_KEY", None):
        with pytest.raises(ValueError) as excinfo:
            create_gemini_model_client(api_key="")
        assert "GEMINI_API_KEY is missing" in str(excinfo.value)


# 4. Tavily search tool configuration tests
def test_tavily_search_tool_configuration():
    """Verify Tavily search tool is initialized and wrapped properly."""
    tool = create_travel_specific_search_tool(
        api_key="test-tavily-key",
        max_results=3,
    )
    assert tool is not None
    assert tool.name == "travel_search"
    assert "travel-related" in tool.description.lower() or "travel" in tool.description.lower()


def test_tavily_tool_missing_key():
    """Verify creating Tavily tool without key raises descriptive ValueError."""
    with patch("utils.tools.TAVILY_API_KEY", None):
        with pytest.raises(ValueError) as excinfo:
            create_travel_specific_search_tool(api_key="")
        assert "TAVILY_API_KEY is missing" in str(excinfo.value)


# 5. Agent construction tests
def test_agents_construction():
    """Verify both Travel Planner and Researcher agents can be constructed."""
    mock_client = MagicMock()
    mock_client.model_info = {"family": "gemini", "function_calling": True}

    def mock_travel_search(query: str) -> str:
        """Search for travel information."""
        return f"Mock results for {query}"

    # Planner agent
    planner = create_planner_agent(client=mock_client, tools=[mock_travel_search])
    assert planner.name == "Travel_Planner"
    assert "travel planner" in planner.description.lower()
    assert len(planner._tools) == 1

    # Researcher agent
    researcher = create_researcher_agent(client=mock_client, tools=[mock_travel_search])
    assert researcher.name == "Researcher"
    assert "researcher" in researcher.description.lower()


# 6. Team construction test
def test_team_construction():
    """Verify Round-Robin travel team can be constructed with participants."""
    mock_planner = MagicMock()
    mock_planner.name = "Travel_Planner"

    mock_researcher = MagicMock()
    mock_researcher.name = "Researcher"

    team = create_travel_team(planner=mock_planner, researcher=mock_researcher, max_turns=5)
    assert team is not None
    assert len(team._participants) == 2
    assert team.name == "Travel_Planning_Team"


# 7. Safe parsing of search output tests (preventing eval() vulnerabilities)
def test_safe_parsing_structured_data():
    """Verify safe parsing correctly handles JSON, Python dicts, and rejects dangerous code."""
    # JSON dict
    json_str = '{"query": "Paris hotels", "answer": "Hotel Le Marais", "results": []}'
    parsed = parse_structured_data(json_str)
    assert isinstance(parsed, dict)
    assert parsed["query"] == "Paris hotels"

    # Python literal dict (single quotes)
    py_dict_str = "{'query': 'Tokyo attractions', 'answer': 'Sensō-ji Temple', 'results': []}"
    parsed_py = parse_structured_data(py_dict_str)
    assert isinstance(parsed_py, dict)
    assert parsed_py["query"] == "Tokyo attractions"

    # Direct dict
    direct_dict = {"query": "Rome restaurants"}
    assert parse_structured_data(direct_dict) == direct_dict

    # Dangerous payload: must NOT execute and must return None
    dangerous_payload = "__import__('os').system('echo pwned')"
    result = parse_structured_data(dangerous_payload)
    assert result is None


def test_format_travel_content_output():
    """Verify content formatting displays clean text without crashing."""
    sample_data = {
        "query": "best cafes in Paris",
        "answer": "Café de Flore and Les Deux Magots",
        "results": [
            {"title": "Café de Flore", "url": "https://cafedeflore.fr", "content": "Famous café in Saint-Germain."}
        ],
    }
    formatted = format_search_result(sample_data)
    assert "Search Query: best cafes in Paris" in formatted
    assert "Café de Flore" in formatted
    assert "https://cafedeflore.fr" in formatted

    # Normal text should pass through unchanged
    plain_text = "Here is your 5-day itinerary for Paris."
    assert format_travel_content(plain_text) == plain_text


# 8. User request input test
def test_user_request_cli_args():
    """Verify user request extraction from CLI arguments."""
    with patch("sys.argv", ["main.py", "Plan", "a", "3-day", "trip", "to", "Amsterdam"]):
        request = get_user_request()
        assert request == "Plan a 3-day trip to Amsterdam"

    with patch("sys.argv", ["main.py", "--query", "Visit Kyoto for 4 days"]):
        request = get_user_request()
        assert request == "Visit Kyoto for 4 days"