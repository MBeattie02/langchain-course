from typing import Any
import io
import sys
import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage

load_dotenv()


@tool
def execute_python_code(code: str) -> str:
    """Execute Python code and return the output.
    
    Use this tool to run Python code. The code will be executed in a Python REPL.
    You have access to the qrcode package. If you get an error, debug your code and try again.
    
    IMPORTANT: Always print your results! For pandas operations, use print() to display DataFrames.
    Example: print(df.head()) or print(df.groupby('column').size())
    
    Args:
        code: The Python code to execute as a string.
        
    Returns:
        The output of the code execution (stdout).
    """
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        # Execute the code
        exec(code, globals())
        output = buffer.getvalue()
        return output.strip() if output.strip() else "Code executed successfully with no output."
    except Exception as e:
        return f"Error executing code: {str(e)}"
    finally:
        sys.stdout = old_stdout


@tool
def query_csv_data(question: str) -> str:
    """Answer questions about the episode_info.csv file using pandas.
    
    This tool loads the CSV file and uses pandas to answer questions about the data.
    It can perform calculations, aggregations, and data analysis.
    
    Args:
        question: The question to answer about the CSV data.
        
    Returns:
        The answer to the question based on the CSV data.
    """
    try:
        # Load the CSV file
        df = pd.read_csv("episode_info.csv")
        
        # Use pandas to answer the question
        # This is a simplified approach - for complex queries, the agent will use Python code execution
        if "season" in question.lower() and ("most" in question.lower() or "max" in question.lower()):
            # Check for both capitalized and lowercase column names
            season_col = "Season" if "Season" in df.columns else ("season" if "season" in df.columns else None)
            if season_col:
                season_counts = df.groupby(season_col).size()
                max_season = season_counts.idxmax()
                max_count = season_counts.max()
                return f"Season {max_season} has the most episodes with {max_count} episodes."
        
        # Return basic info for other questions
        return f"The CSV file has {len(df)} rows and {len(df.columns)} columns. Columns: {', '.join(df.columns)}. For complex queries, use the Python code execution tool with pandas."
    except FileNotFoundError:
        return "Error: episode_info.csv file not found."
    except Exception as e:
        return f"Error processing CSV: {str(e)}"


def main():
    print("Start...")

    # Python code execution agent
    python_system_prompt = """You are an agent designed to write and execute python code to answer questions.
    You have access to a python REPL, which you can use to execute python code.
    You have qrcode package installed.
    If you get an error, debug your code and try again.
    
    IMPORTANT: Always use print() to display results. The tool only captures printed output.
    Example: print(result) or print(df.head())
    
    Only use the output of your code to answer the question. 
    You might know the answer without running any code, but you should still run the code to get the answer.
    If it does not seem like you can write code to answer the question, just return "I don't know" as the answer."""

    python_agent = create_agent(
        model=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=[execute_python_code],
        system_prompt=python_system_prompt,
    )

    # CSV query agent - uses Python code execution for pandas operations
    csv_system_prompt = """You are an agent designed to answer questions about CSV data.
    You have access to a Python code execution tool. Use it to load and analyze the episode_info.csv file with pandas.
    
    CRITICAL INSTRUCTIONS:
    1. Always import pandas as pd and load the CSV: df = pd.read_csv('episode_info.csv')
    2. ALWAYS use print() to display results - the tool only captures printed output
    3. For DataFrames, use print(df.head()), print(df.groupby(...)), etc.
    4. For aggregations, use print() to show the result: print(df.groupby('Season').size())
    5. Never just write df.head() - always write print(df.head())
    
    Example for "which season has the most episodes?":
    import pandas as pd
    df = pd.read_csv('episode_info.csv')
    season_counts = df.groupby('Season').size()
    print(season_counts)
    max_season = season_counts.idxmax()
    max_count = season_counts.max()
    print(f"Season {max_season} has the most episodes with {max_count} episodes")
    
    Then perform the necessary pandas operations to answer the question and ALWAYS print the results."""

    csv_agent = create_agent(
        model=ChatOpenAI(temperature=0, model="gpt-4"),
        tools=[execute_python_code],
        system_prompt=csv_system_prompt,
    )

    # Router/Grand Agent that can use both agents
    @tool
    def python_agent_tool(question: str) -> str:
        """Useful when you need to transform natural language to python and execute the python code,
        returning the results of the code execution.
        DOES NOT ACCEPT CODE AS INPUT - only natural language questions."""
        result = python_agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        # Extract the final answer from the agent response
        if "messages" in result and len(result["messages"]) > 0:
            # Find the last AIMessage with content (skip ToolMessages)
            for message in reversed(result["messages"]):
                # Skip ToolMessages - we want the AI's final response
                if isinstance(message, ToolMessage) or (isinstance(message, dict) and message.get("type") == "tool"):
                    continue
                # Handle message objects
                if hasattr(message, "content"):
                    content = str(message.content) if message.content else ""
                    # Return first non-empty AIMessage content
                    if content:
                        return content
                # Handle dictionaries
                elif isinstance(message, dict):
                    content = message.get("content", "")
                    if content:
                        return str(content)
        # Fallback: return string representation of result
        return str(result)

    @tool
    def csv_agent_tool(question: str) -> str:
        """Useful when you need to answer questions over episode_info.csv file.
        Takes as input the entire question and returns the answer after running pandas calculations."""
        result = csv_agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        # Extract the final answer from the agent response
        if "messages" in result and len(result["messages"]) > 0:
            # Find the last AIMessage with content (skip ToolMessages)
            for message in reversed(result["messages"]):
                # Skip ToolMessages - we want the AI's final response
                if isinstance(message, ToolMessage) or (isinstance(message, dict) and message.get("type") == "tool"):
                    continue
                # Handle message objects
                if hasattr(message, "content"):
                    content = str(message.content) if message.content else ""
                    # Return first non-empty AIMessage content
                    if content:
                        return content
                # Handle dictionaries
                elif isinstance(message, dict):
                    content = message.get("content", "")
                    if content:
                        return str(content)
        # Fallback: return string representation of result
        return str(result)

    # Grand agent that routes to appropriate sub-agents
    grand_agent = create_agent(
        model=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=[python_agent_tool, csv_agent_tool],
        system_prompt="You are a helpful assistant that can answer questions using Python code execution or CSV data analysis. Choose the appropriate tool based on the question.",
    )

    # Test queries
    print("\n=== Query 1: CSV Question ===")
    result1 = grand_agent.invoke({
        "messages": [{"role": "user", "content": "which season has the most episodes?"}]
    })
    # Extract and print the final answer (skip ToolMessages)
    if "messages" in result1 and len(result1["messages"]) > 0:
        for msg in reversed(result1["messages"]):
            if isinstance(msg, ToolMessage) or (isinstance(msg, dict) and msg.get("type") == "tool"):
                continue
            if hasattr(msg, "content") and msg.content:
                print(msg.content)
                break
            elif isinstance(msg, dict) and msg.get("content"):
                print(msg.get("content"))
                break
        else:
            print(result1)
    else:
        print(result1)

    print("\n=== Query 2: Python Code Execution ===")
    result2 = grand_agent.invoke({
        "messages": [{"role": "user", "content": "Generate and save in current working directory 15 qrcodes that point to `www.udemy.com/course/langchain`"}]
    })
    # Extract and print the final answer (skip ToolMessages)
    if "messages" in result2 and len(result2["messages"]) > 0:
        for msg in reversed(result2["messages"]):
            if isinstance(msg, ToolMessage) or (isinstance(msg, dict) and msg.get("type") == "tool"):
                continue
            if hasattr(msg, "content") and msg.content:
                print(msg.content)
                break
            elif isinstance(msg, dict) and msg.get("content"):
                print(msg.get("content"))
                break
        else:
            print(result2)
    else:
        print(result2)


if __name__ == "__main__":
    main()
