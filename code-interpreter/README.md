# 🐍 Code Interpreter Agent

A multi-agent system built with LangChain v1 that demonstrates hierarchical agent architecture. This project showcases how to create specialized agents for different tasks (Python code execution and CSV data analysis) and orchestrate them through a router agent.

## 🎯 Overview

This project implements a **three-tier agent architecture**:

1. **Python Code Execution Agent** - Executes Python code dynamically
2. **CSV Data Analysis Agent** - Analyzes CSV files using pandas
3. **Grand Router Agent** - Intelligently routes questions to the appropriate specialized agent

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Grand Router Agent              │
│  (Routes to appropriate sub-agent)  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│ Python Code │  │ CSV Data   │
│   Agent     │  │   Agent    │
└──────┬──────┘  └─────┬──────┘
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│ execute_    │  │ execute_   │
│ python_code │  │ python_code│
│   tool      │  │   tool     │
└─────────────┘  └────────────┘
```

## 🔑 Key Concepts

### Agent Hierarchy

This demonstrates a **hierarchical agent pattern**:

- **Level 1**: Grand agent (router)
- **Level 2**: Specialized agents (Python, CSV)
- **Level 3**: Tools (code execution)

## 🚀 Getting Started

### Installation

1. **Install dependencies**:

   ```bash
   uv sync
   ```

2. **Set up environment variables**:

   Create a `.env` file:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Prepare CSV file** (optional):

   Place `episode_info.csv` in the project directory for CSV queries.

4. **Run the application**:

   ```bash
   python main.py
   ```

## 📦 Dependencies

- **langchain** (>=1.0.0) - Core LangChain framework
- **langchain-openai** (>=1.0.0) - OpenAI integration
- **python-dotenv** (>=1.0.0) - Environment variable management
- **pandas** (>=2.0.0) - Data analysis
- **qrcode** (>=7.0.0) - QR code generation

## 🎓 Learning Objectives

This project demonstrates:

1. **Multi-Agent Systems**: How to orchestrate multiple specialized agents
2. **Tool Creation**: Using `@tool` decorator to create custom tools
3. **Agent Routing**: Implementing intelligent routing between agents
4. **Code Execution**: Safely executing dynamic Python code
5. **LangChain v1 Patterns**: Modern LangChain best practices

## 🧪 Example Queries

### CSV Analysis

```
"Which season has the most episodes?"
"What's the average episode count per season?"
"Show me all episodes from season 1"
```

### Python Code Execution

```
"Generate 15 QR codes pointing to www.example.com"
"Calculate the factorial of 10"
"Create a list of prime numbers up to 100"
```

## 🔧 Customization

### Adding New Tools

```python
@tool
def my_custom_tool(input: str) -> str:
    """Description of what the tool does."""
    # Your implementation
    return result
```

### Creating New Specialized Agents

```python
new_agent = create_agent(
    model=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
    tools=[my_custom_tool],
    system_prompt="Instructions for the agent",
)
```

### Extending the Router

Add your new agent tool to the grand agent's tools list:

```python
grand_agent = create_agent(
    model=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
    tools=[python_agent_tool, csv_agent_tool, my_new_agent_tool],
    system_prompt="Updated routing instructions",
)
```
