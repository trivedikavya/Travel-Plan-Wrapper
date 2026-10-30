# AutoGen Travel Planner (Google Gemini & Tavily Search)

An intelligent multi-agent travel planning system built with **Microsoft AutoGen v0.4**, powered by **Google Gemini** (via Google AI Studio) and real-time web search powered by **Tavily**.

---

## Features

- ** Multi-Agent Collaboration**: Two specialized agents (`Travel_Planner` and `Researcher`) collaborate in a structured Round-Robin group chat.
- ** Powered by Google Gemini**: Built on modern, cost-efficient Gemini models (`gemini-2.5-flash` by default) using the official Google AI Studio API.
- ** Real-Time Travel Search**: Live web search integration via Tavily Search returns current hotel rates, attractions, restaurant tips, and opening hours.
- ** Secure & Safe Parsing**: Zero `eval()` vulnerabilities; utilizes safe JSON and literal evaluation to parse search data.
- ** Interactive & CLI Support**: Run interactive prompts or supply custom travel requests directly from the command line.
- ** Configurable & Extensible**: Environment-driven settings with automated variable validation.

---

##  Architecture

```
                          User Request
                               │
                               ▼
                   ┌────────────────────────┐
                   │  RoundRobinGroupChat   │
                   └───────────┬────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     ┌───────────────────┐           ┌───────────────────┐
     │   Travel Planner  │◄─────────►│     Researcher    │
     │      (Gemini)     │           │      (Gemini)     │
     └─────────┬─────────┘           └─────────┬─────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │   Tavily Search Tool   │
                   │ (Real-Time Web Search) │
                   └────────────────────────┘
```

1. **Travel Planner Agent (`agents/planner.py`)**:
   - Analyzes traveler needs (destination, duration, budget, preferences).
   - Queries Tavily for live accommodations, dining, sightseeing, and transit.
   - Generates structured day-by-day itineraries with source links and estimated costs.

2. **Researcher Agent (`agents/researcher.py`)**:
   - Reviews and verifies proposed recommendations.
   - Checks transit logistics, operating hours, and seasonal constraints.
   - Emits the termination word (`stop`) once the plan is thorough and finalized.

3. **Gemini Model Integration (`models/gemini_model.py`)**:
   - Manages communication with Google AI Studio using AutoGen's `OpenAIChatCompletionClient` over Google's official OpenAI-compatible endpoint.

---

##  Project Structure

```
TRAVEL_PLANNER/
├── agents/
│   ├── planner.py            # Travel Planner agent definition
│   └── researcher.py         # Researcher agent definition
├── config/
│   └── settings.py           # Configuration loader & startup validator
├── models/
│   └── gemini_model.py       # Google Gemini model client configuration
├── teams/
│   └── travel_team.py        # RoundRobinGroupChat team setup
├── utils/
│   ├── tools.py              # Tavily search tool adapter
│   └── utils.py              # Termination conditions & state helpers
├── tests/
│   └── agents_test.py        # Automated test suite
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (protects .env and venv)
├── main.py                   # Application entry point
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

##  Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 (64-bit recommended)
- **Google AI Studio API Key**: Free API key for Gemini
- **Tavily API Key**: Free API key for real-time web search
- **Operating System**: Windows, macOS, or Linux

---

##  Obtaining API Keys

### 1. Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **"Get API key"** and create a new API key.
4. Copy your key (starts with `AIzaSy...`).

### 2. Tavily Search API Key
1. Sign up for a free account at [Tavily](https://tavily.com/).
2. Navigate to your dashboard and copy your API key (starts with `tvly-...`).

---

##  Setup & Installation (Windows)

Open PowerShell in the project directory:

### Step 1: Open Project Directory
```powershell
cd C:\Users\hp\OneDrive\Desktop\TRAVEL_PLANNER-main
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```
*(If you see an execution policy error on Windows, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to create your `.env` file:
```powershell
Copy-Item .env.example .env
```
Open `.env` and fill in your API keys:
```dotenv
# Google Gemini API key from Google AI Studio
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Supported Gemini model identifier (default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Tavily Search API key
TAVILY_API_KEY=your_actual_tavily_api_key_here

# Workflow settings
MAX_TURN=7
MAX_TURN_10=10
TERMINATION_WORD=stop
```

> **Security Note:** `.env` is ignored in `.gitignore`. Never commit or hardcode your API keys.

---

##  Running the Application

### Option A: Interactive Mode
Run without arguments to be prompted for your query (or press Enter to use the default 5-day Paris trip):
```powershell
python main.py
```

### Option B: Custom CLI Query
Pass your travel request directly on the command line:
```powershell
python main.py "Plan a 3-day budget trip to Mumbai for 2 people with a budget of Rs 15,000"
```

```powershell
python main.py "Find affordable hotels and must-visit attractions in Ahmedabad with visiting hours"
```

```powershell
python main.py "Plan a 7-day family trip to Tokyo and Kyoto with train tips"
```

---

##  Running Automated Tests

Run the test suite using `pytest`:
```powershell
python -m pytest tests/ -v
```

All 11 unit tests verify:
- Environment variable loading and defaults
- Helpful errors when API keys are missing
- Gemini model client initialization
- Tavily tool configuration and parameter passing
- Agent and Round-Robin team construction
- Safe parsing of search data (preventing arbitrary code execution)
- Command-line argument parsing

---

##  API Rate Limits & Free-Tier Considerations

- **Google AI Studio (Gemini 2.5 Flash)**:
  - Free tier includes generous RPM (requests per minute) and RPD (requests per day) limits.
  - Recommended model is `gemini-2.5-flash` for high speed, reasoning, and tool use.
  - If rate limits occur (HTTP 429), the application displays a friendly message. Simply wait a moment or switch to another supported Gemini model via `GEMINI_MODEL`.
- **Tavily Search**:
  - The free tier provides 1,000 search credits per month.
  - Each search query issued by the agents consumes search credits.

---

##  Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `UnicodeEncodeError: 'charmap' codec can't encode character...` | Windows PowerShell encoding default | Handled automatically in `main.py` via UTF-8 reconfiguration. You can also run `$env:PYTHONIOENCODING='utf-8'` in PowerShell. |
| `GEMINI_API_KEY is missing` | `.env` file does not exist or key is blank | Ensure `.env` exists in the project root with a valid `GEMINI_API_KEY`. |
| `TAVILY_API_KEY is missing` | Key missing in `.env` | Add `TAVILY_API_KEY` to your `.env` file. |
| `404 NOT_FOUND models/...` | Using a retired Gemini model | Ensure `GEMINI_MODEL=gemini-2.5-flash` in `.env`. |
| `ModuleNotFoundError: No module named '...'` | Virtual environment not active or dependencies missing | Run `.\venv\Scripts\activate` and `pip install -r requirements.txt`. |
