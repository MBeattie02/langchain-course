# Function Calling Demo

This module shows a minimal LangChain setup that calls predefined functions through an agent-like workflow.

## Quick Start

1. Create a virtual environment and install dependencies:
   ```bash
   uv sync
   ```
2. Run the example script:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Entry point that loads the tool definitions and runs the chain.
- `callbacks.py`: Optional callback handlers used during execution.
- `pyproject.toml`: Project metadata and dependency list managed by `uv`.
