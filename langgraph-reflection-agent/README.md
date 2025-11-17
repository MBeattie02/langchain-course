# 🚀 LangGraph Tweet Optimization Pipeline

This project implements a reflect–generate loop using LangGraph and LangChain to iteratively improve Twitter posts. The system generates a tweet, critiques it, then refines it—repeating until a quality threshold is reached.

---

## 📌 Features

- LangGraph state machine with two nodes:
  - generate — Produces an improved tweet version using an LLM.
  - reflect — Critiques the tweet and returns actionable recommendations.
- Automatic iterative refinement using conditional edges.
- Uses OpenAI-compatible models via ChatOpenAI.
- Mermaid + ASCII graph rendering of the workflow.
- Simple CLI-style invocation using graph.invoke().

---

## 🧠 Architecture

The system is built around a MessageGraph state containing the message history:

```bash
class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

### Workflow

1. Generate Node  
   Uses generate_chain to produce a tweet based on the conversation so far.

2. Reflect Node  
   Uses reflect_chain to critique the tweet and provide improvement suggestions.

3. Loop  
   The graph alternates between generate → reflect → generate until len(state["messages"]) > 6, then it exits.

---

## 📁 Project Structure

```bash
.
├── chains.py                  # Contains generate_chain and reflect_chain
├── main.py (this file)       # LangGraph pipeline implementation
├── .env                       # Environment variables for API keys
└── README.md
```

---

## ▶️ Running the Script

1. Install dependencies:

```bash
pip install langchain langchain-openai langgraph python-dotenv
```

2. Create a .env file:

```bash
OPENAI_API_KEY=your_api_key_here
```

3. Run the script:

```bash
python main.py
```

You should see:

- Printed mermaid graph
- ASCII graph rendering
- The optimized tweet output

---

## 🧩 Example Input

```bash
{
    "messages": [
        HumanMessage(content="Make this tweet better: ...")
    ]
}
```

The pipeline then produces multiple refined versions automatically.
