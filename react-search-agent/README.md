React Search Agent

Basic LangChain agent that uses OpenAI for reasoning and Tavily Search as a web search tool. The agent returns a structured response (answer plus sources) defined via Pydantic models in `schemas.py`.

Features

- OpenAI LLM via `langchain-openai` (`ChatOpenAI`)
- Web search via `langchain-tavily` (`TavilySearch`)
- Structured outputs using Pydantic (`AgentResponse`, `Source`)
- Environment-based configuration loaded with `python-dotenv`

Setup

1. Create a `.env` file in this directory with your keys:

```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

2. Install dependencies :

- Using uv :
  - From this folder: `uv sync`

Behavior

- The current example in `main.py` asks the agent to search for AI engineer roles and prints the structured result. Modify the user message in `main.py` to change the query.

Key Files

- `main.py`: constructs the agent and runs a sample query
- `schemas.py`: Pydantic models for structured outputs (`AgentResponse`, `Source`)
- `pyproject.toml`: dependencies and project metadata
