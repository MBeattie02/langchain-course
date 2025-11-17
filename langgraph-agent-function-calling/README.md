# 🧠 ReAct Agent with LangGraph v1 + Tools (LangChain v1)

This project implements a ReAct-style AI agent using:

- LangGraph v1 (graph-based AI state machines)
- LangChain v1
- OpenAI GPT-4o-mini
- Tavily Search API
- Custom Python tool (triple)

The agent performs reasoning, decides whether it needs to call a tool, executes the tool, and continues reasoning until it produces a final answer.

## 🚀 Features

### ✔️ ReAct-style agent loop

The agent thinks → decides on a tool → executes it → loops until done.

### ✔️ Tool Support

Includes:

- TavilySearch (web search)
- Custom tool: triple(num)

### ✔️ LangGraph State Machine

Graph structure:

agent_reason → (needs tool?) → act → agent_reason → ...

## 📦 Project Structure

.
├── main.py # Builds and runs the LangGraph agent
├── nodes.py # Reasoning node + ToolNode setup
├── react.py # LLM + tools definitions
├── README.md
└── .env # API keys

## 🔧 Installation

pip install -r requirements.txt

Required libraries include:

- langchain
- langgraph
- langsmith
- langchain-openai
- langchain-tavily
- python-dotenv

## 🔑 Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
```

## ▶️ Running the Agent

python main.py

Example output:

Hello ReAct LangGraph with Function Calling  
The temperature in Tokyo is 12°C; triple it = 36°C.

## 🧩 How the LangGraph Works

1. agent_reason  
   The LLM reasons about the user query. If it decides that a tool is needed, it produces a tool call message.

2. should_continue  
   If the latest message contains tool calls, the graph transitions to act. Otherwise, it ends the workflow.

3. act  
   Executes the tool(s) requested by the model and appends the result to the message list.

4. Control returns to agent_reason, which continues reasoning with the new information.

## 🛠️ Adding New Tools

Add any Python function and decorate it with @tool, then include it in the tools list in react.py.

## 📘 Notes

- Uses the new v1 LangChain and LangGraph APIs.
- Easy to extend with more tools or different LLMs.
- Useful template for search-enabled and function-calling agents.
