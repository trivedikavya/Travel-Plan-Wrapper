import ast
import asyncio
import json
import sys
from typing import Any, Dict, Optional

# Ensure Windows terminal handles UTF-8 / emojis cleanly without crashing on cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage
from config.settings import validate_config
from teams.travel_team import create_travel_team, team as default_team

DEFAULT_TRAVEL_PROMPT = "Plan a 5-day trip to Paris for two people."


def parse_structured_data(content: Any) -> Optional[Dict[str, Any]]:
    """
    Safely parse dictionary or structured JSON/Python literal data without using eval().

    Args:
        content: Any input content (dict, string, or object).

    Returns:
        Optional[Dict[str, Any]]: Parsed dictionary if valid, otherwise None.
    """
    if isinstance(content, dict):
        return content

    if not isinstance(content, str):
        return None

    stripped = content.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None

    # Try standard JSON parsing first
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Safely evaluate Python dictionary literals (e.g. single-quoted dict strings)
    try:
        parsed = ast.literal_eval(stripped)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, SyntaxError, MemoryError):
        pass

    return None


def format_search_result(data: Dict[str, Any]) -> str:
    """Format structured Tavily search results into readable text."""
    if not isinstance(data, dict):
        return str(data)

    formatted = []

    if "query" in data and data["query"]:
        formatted.append(f"🔍 Search Query: {data['query']}")

    if "answer" in data and data["answer"]:
        formatted.append(f"📋 Summary: {data['answer']}")

    results = data.get("results", [])
    if isinstance(results, list) and results:
        formatted.append("\n📍 Verified Top Recommendations:")
        for i, item in enumerate(results[:3], 1):
            if isinstance(item, dict):
                title = item.get("title", "Recommendation")
                url = item.get("url", "")
                snippet = item.get("content", "")
                if len(snippet) > 220:
                    snippet = snippet[:220].rstrip() + "..."
                link_text = f" ({url})" if url else ""
                formatted.append(f"   {i}. {title}{link_text}")
                if snippet:
                    formatted.append(f"      {snippet}")

    return "\n".join(formatted)


def format_travel_content(content: Any) -> str:
    """
    Format message content for terminal output.
    Hides internal function call plumbing and safely renders search data and text.
    """
    try:
        # Handle list-type content (AutoGen function calls and execution results)
        if isinstance(content, list):
            for item in content:
                item_str = str(item)
                if "FunctionCall(" in item_str:
                    return "🔍 Researching live travel data via Tavily..."
                if "FunctionExecutionResult(" in item_str:
                    # Attempt to extract and safely format the content inside the execution result
                    if hasattr(item, "content"):
                        parsed = parse_structured_data(item.content)
                        if parsed and "query" in parsed:
                            return format_search_result(parsed)
            return ""

        # Handle string content
        if isinstance(content, str):
            # Check if this string is a serialized dictionary from search
            parsed_dict = parse_structured_data(content)
            if parsed_dict and ("query" in parsed_dict or "results" in parsed_dict):
                return format_search_result(parsed_dict)
            return content

        # Handle direct dictionary content
        if isinstance(content, dict):
            return format_search_result(content)

        return str(content)
    except Exception:
        return str(content) if content is not None else ""


def get_user_request() -> str:
    """
    Obtain travel request from command line arguments or interactive input.
    Falls back to a sensible default if none provided.
    """
    # 1. Check command line arguments: python main.py "Plan a 3-day trip to Rome"
    args = sys.argv[1:]
    if args:
        # Filter out common flags like --query if present
        if args[0] in ("-q", "--query") and len(args) > 1:
            return " ".join(args[1:]).strip()
        return " ".join(args).strip()

    # 2. Check interactive input
    try:
        print(f"\n💡 Default example: '{DEFAULT_TRAVEL_PROMPT}'")
        user_input = input("✈️  Enter your travel planning request (or press Enter to use default): ").strip()
        if user_input:
            return user_input
    except (EOFError, KeyboardInterrupt):
        print()

    # 3. Fallback to sensible default
    return DEFAULT_TRAVEL_PROMPT


async def run_planner(user_prompt: str) -> None:
    """Execute the multi-agent travel planning session."""
    # Ensure configuration is valid before launching
    try:
        validate_config(require_keys=True)
    except ValueError as e:
        print("\n❌ Configuration Error:")
        print(str(e))
        print("\nPlease configure your .env file before running the application.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🌍 AutoGen Travel Planner (Google Gemini & Tavily Search)")
    print("=" * 60)
    print(f"🎯 Request: {user_prompt}")
    print("-" * 60)

    # Initialize team
    team = default_team or create_travel_team()

    task = TextMessage(content=user_prompt, source="User")

    try:
        async for message in team.run_stream(task=task):
            if isinstance(message, TaskResult):
                print("\n" + "=" * 60)
                print(f"✅ Planning Complete! (Stop reason: {message.stop_reason})")
                print("=" * 60)
            else:
                source = getattr(message, "source", "Agent")
                if source == "User":
                    continue

                formatted = format_travel_content(message.content)
                if formatted and formatted.strip():
                    print(f"\n💬 [{source}]:")
                    print(formatted.strip())
                    print("-" * 60)

    except Exception as e:
        print(f"\n❌ An error occurred during planning: {e}")
        print("Please check your API keys, network connection, or rate limits.")


def main():
    """Application entry point."""
    user_prompt = get_user_request()
    asyncio.run(run_planner(user_prompt))


if __name__ == "__main__":
    main()