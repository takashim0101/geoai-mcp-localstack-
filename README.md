# Local AI Dev Template (Ollama + LM Studio + MCP + VSCode)

This repository provides a fully local, privacy-safe AI development environment using:

- Ollama
- LM Studio
- MCP Servers
- VSCode + Gemini Code Assist

## How to use

### 1. Install dependencies
npm install

### 2. Start MCP server
./scripts/start_mcp.ps1

### 3. Open VSCode
The local LLM becomes available inside the editor.

### 4. Switch provider
Edit `vscode/config.json`:
LLM_PROVIDER = "ollama"
or
LLM_PROVIDER = "lmstudio"

---

## Technologies Used

This project integrates several technologies to create a local AI development environment.

-   **AI & LLM**
    -   **LangChain**: A framework for developing applications powered by language models. Used here to build the core ReAct agent.
    -   **Ollama & LM Studio**: Service platforms for running and managing local Large Language Models (LLMs) like Llama 3.
-   **Programming Languages**
    -   **Python**: The primary language for the AI agent (`agent.py`) and GIS tooling.
    -   **JavaScript (Node.js)**: Used for the simple MCP server (`mcp-servers/local-llm/server.js`) that bridges the gap to the local LLM.
-   **Geospatial**
    -   **gis-mcp**: A Python package that provides a suite of GIS tools accessible to the AI agent.
    -   **WKT (Well-Known Text)**: A standard text markup language for representing vector geometry objects.
-   **Development & Tooling**
    -   **VSCode**: The primary code editor, configured for this project.
    -   **Gemini Code Assist**: The VSCode extension used to interact with the AI and manage the MCP servers.
    -   **npm & uv/pip**: Package managers for Node.js and Python, respectively.

---

## System Architecture
This project is composed of several components that work together to provide a local, AI-powered GIS agent.

**Component Overview:**
1.  **Client (`agent.py` or VSCode)**: The user-facing application where you provide instructions.
2.  **MCP Servers**: Middleware that connects the client to the backend tools and the LLM.
    -   `gis-mcp`: A server that exposes the Python-based GIS tools.
    -   `local-llm`: A Node.js server that acts as a bridge to the LLM service.
3.  **LLM Service (Ollama or LM Studio)**: The local service that runs the actual large language model (e.g., Llama 3).

**Workflow Diagram:**
Here is the typical flow of information when you ask the agent a question:
```
   +----------+        +---------------------+        +--------------------+
   |          |        |                     |        |                    |
   |   User   |------> |  agent.py (Client)  |------> |  local-llm Server  |
   |          |        |                     |        |  (Node.js Bridge)  |
   +----------+        +----------+----------+        +---------+----------+
                                  ^                             |
                                  | (GIS Tool Call)             | (LLM Prompt)
                                  v                             v
                       +----------+----------+        +---------+----------+
                       |                     |        |                    |
                       |  gis-mcp (Tools)    | <------> |   LLM Service      |
                       |                     | (Result) | (Ollama/LM Studio)|
                       +---------------------+        +--------------------+
```

## Startup Sequence
To run the application, components must be launched in the correct order.

1.  **Start Local LLM Service**:
    -   Ensure that your chosen LLM provider (Ollama or LM Studio) is running. This service must be active in the background to handle AI requests.

2.  **Start MCP Servers**:
    -   Run the `start_mcp.ps1` script from the `/scripts` directory. This will launch the necessary `gis-mcp` and `local-llm` servers.

3.  **Run the Client**:
    -   **For the standalone agent**: Execute `python agent.py` in your terminal.
    -   **For VSCode integration**: Simply open the VSCode editor. The Gemini Code Assist extension will automatically connect to the running MCP servers.

---

## GIS AI Agent (`agent.py`)

The `agent.py` script implements a sophisticated, command-line AI agent for performing Geographic Information System (GIS) tasks. It runs entirely on your local machine, ensuring privacy and control.

### Core Features

-   **Local LLM Integration**: Connects to local Large Language Models (LLMs) like Llama 3 using either **LM Studio** or **Ollama**, configured via the `LLM_PROVIDER` environment variable.
-   **Tool-Using Agent**: Utilizes the `LangChain` framework to create a ReAct (Reason, Act) agent that can intelligently use a suite of GIS tools provided by the `gis-mcp` library.
-   **Robust Input/Output Handling**:
    -   **WKT Enforcement**: Strictly requires geometric inputs to be in Well-Known Text (WKT) format (e.g., `"POINT(10 20)"`) to ensure reliable tool execution. The prompt is engineered to guide the LLM towards this format.
    -   **Custom Output Parser**: A `Llama3RobustOutputParser` is implemented to reliably parse the LLM's output, even with common formatting inconsistencies. It cleans up the text to isolate the agent's "Thought" and "Action".
    -   **Tool Wrapper**: Each GIS tool is wrapped to provide better error handling and to truncate overly long outputs, preventing the agent from getting stuck in long, unhelpful loops.
-   **Interactive CLI**: After setup, it provides an interactive prompt where you can ask the agent GIS-related questions in natural language.

### How It Works

1.  **Initialization**: The script loads a local LLM and wraps the tools from the `gis-mcp` library, making them available to the agent.
2.  **Prompt Engineering**: A detailed system prompt instructs the LLM on how to behave, what tools are available, and the critical importance of using the JSON and WKT formats for its actions.
3.  **User Input**: The agent takes a user's question (e.g., "Buffer the point (10, 20) by 100 meters").
4.  **Reasoning Loop**: The agent enters a "Thought -> Action -> Action Input -> Observation" loop:
    -   **Thought**: The LLM thinks about which tool to use.
    -   **Action**: It decides on a tool (e.g., `buffer`).
    -   **Action Input**: It formats the arguments for the tool as a JSON object with WKT geometry.
    -   **Observation**: The script executes the tool and returns the result to the agent.
5.  **Final Answer**: The agent loops until it has enough information to answer the user's question.

This setup creates a powerful local assistant capable of solving complex, multi-step geospatial problems.

---

## Engineering Highlights & Portfolio Notes

In short, this agent is built on a standard, well-established AI technique (ReAct) but incorporates significant **custom engineering** to make a local LLM (Llama 3) operate reliably and effectively in a real-world scenario.

When presenting this project, framing it with the following points will highlight the depth of the engineering work involved.

### 1. Standard Foundation (The "What")

The core architecture follows industry best practices for building autonomous agents:

-   **ReAct Framework (Reason + Act)**: The agent uses the fundamental cycle of "Thought" -> "Action" -> "Observation" to reason about a problem and use tools to solve it.
-   **LangChain**: The standard library for orchestrating the ReAct framework and integrating components.
-   **Tool Calling**: The mechanism that allows the AI to execute Python functions (the GIS tools).

### 2. Custom Engineering (The "Value-Add")

This is where the real engineering challenge was solved. While a top-tier model like GPT-4 might not require these adjustments, they are **essential for making a smaller, local model like Llama 3 8B perform reliably**.

-   **Robust Output Parser (`Llama3RobustOutputParser`)**:
    -   **Problem**: Standard LangChain parsers are brittle. They fail if the LLM deviates even slightly from the expected format (e.g., writing `Input:` instead of `Action Input:`, forgetting a closing `}`), or adding conversational text).
    -   **Solution**: This agent implements a custom parser that uses regular expressions to **auto-correct common LLM mistakes**. It functions as a self-healing layer between the AI and the program, which is a practical and crucial piece of AI engineering.

-   **Output Summarization (Truncation Middleware)**:
    -   **Problem**: GIS data can be extremely large. Passing a massive polygon's geometry back to the LLM can exceed its context window, causing it to lose focus or crash.
    -   **Solution**: The tool wrapper acts as a safety valve. It intercepts tool outputs and **truncates any result longer than 300 characters**, preventing context overflow and ensuring system stability.

-   **WKT Format Enforcement (Few-Shot Prompting & Guardrails)**:
    -   **Problem**: The LLM might "hallucinate" its own geometry formats (e.g., `{"x": 10, "y": 20}`) instead of using the required WKT standard.
    -   **Solution**: A two-layer defense was created. The prompt provides explicit examples of the correct WKT format (**Few-Shot Prompting**), while the Python code validates the input before execution, rejecting incorrect formats (**Guardrails**).

### How to Showcase This Project

Instead of simply stating, "I built a project using LangChain," you can present it in a way that demonstrates deeper expertise:

> "While it's straightforward to build agents with powerful cloud APIs like OpenAI, I chose to construct this system using a **local LLM (Llama 3) to prioritize privacy and control costs.** Local models are often less reliable at following structured instructions, so I engineered several custom components to ensure robust operation. This included an **auto-correcting output parser** to handle formatting errors and **summarization middleware** to process large-scale GIS data without overwhelming the model's context window. This approach demonstrates how to overcome the practical challenges of deploying AI in resource-constrained or private environments."

In essence, this project is an excellent example of not just *using* tools, but **solving real-world engineering problems with code**.

---

## Key Engineering Concepts Demonstrated

This project demonstrates several key engineering concepts that are crucial for building reliable AI systems.

### 1. Advanced LLM Control

-   **Local LLM Operation**: The agent is engineered to work with a small, efficient local model (Llama 3 8B). This requires more sophisticated control techniques than simply using a large, cloud-based API.
-   **Reliable Output Generation**: To prevent the AI from generating incorrect or "hallucinated" formats, the system uses **Few-Shot Prompting** (giving the AI examples) and **Guardrails** (validating its output with code). This ensures the AI's output is consistently reliable.

### 2. Robust Python Design

-   **Custom Components**: When the standard LangChain library was not enough, a custom parser (`Llama3RobustOutputParser`) was created by extending the library's base class. This component uses regular expressions (Regex) to automatically fix the AI's output.
-   **Clean, Maintainable Code**: The `wrap_tool` function uses a decorator pattern. This adds new features—like input validation and output summarization—to existing tools without modifying their original code, which makes the system easier to maintain and extend.

### 3. System Stability and Error Handling

-   **Resilience**: The agent is designed to be resilient. It uses built-in error handling (`handle_parsing_errors=True`) and `try-except` blocks to prevent crashes, allowing it to recover from mistakes and continue running.
-   **Resource Management**: The system understands that GIS data can be very large. To prevent memory issues or crashes, tool outputs are automatically truncated to a safe length. This is a key feature for ensuring the application runs smoothly.

---

## Python GIS MCP Server Setup

*This setup is based on the official GIS MCP Getting Started guide: https://gis-mcp.com/getting-started/*

This section documents the steps to set up the `gis-mcp` server, a Python-based MCP server for geospatial operations.

### 1. Create and Activate Virtual Environment

First, create a dedicated Python virtual environment.

```shell
# Create the environment
python -m venv venv

# Activate the environment (on Windows PowerShell)
.\venv\Scripts\Activate.ps1
```
*Note: For macOS/Linux, use `source venv/bin/activate`.*

### 2. Install Python Packages

Once the environment is activated (you should see `(venv)` in your terminal prompt), install the necessary packages using `requirements.txt`. This file includes `gis-mcp`, `langchain`, `langchain-community`, and their dependencies.

```shell
# Install the uv package manager (if not already installed)
pip install uv

# (Optional) Upgrade pip
python -m pip install --upgrade pip

# Install all project dependencies from requirements.txt
uv pip install -r requirements.txt
```

### 4. Run the GIS MCP Server

After installation, you can run the server.

**Default (STDIO transport mode):**
Ideal for local development and integration with IDEs like Claude Desktop or Cursor.

```shell
gis-mcp
```

**HTTP transport mode (for network deployments):**
Set environment variables before running.

```powershell
$env:GIS_MCP_TRANSPORT="http" # For PowerShell
$env:GIS_MCP_PORT="8080"     # For PowerShell
gis-mcp
```
*Note: For Linux/macOS, use `export GIS_MCP_TRANSPORT=http` and `export GIS_MCP_PORT=8080`.*

### 5. Connect to an MCP Client

Configure your IDE or client to connect to the GIS MCP server.

**Claude Desktop (Windows) / Cursor IDE (Windows) - Example `mcp.json` configuration:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "C:\\Users\\YourUsername\\.venv\\Scripts\\gis-mcp",
      "args": []
    }
  }
}
```
*Remember to replace `YourUsername` with your actual Windows username and adjust the path if your virtual environment is not in the default user directory.*

**Claude Desktop (Linux/Mac) / Cursor IDE (Linux/Mac) - Example `mcp.json` configuration:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "/home/YourUsername/.venv/bin/gis-mcp",
      "args": []
    }
  }
}
```
*Remember to replace `YourUsername` with your actual Linux/Mac username and adjust the path if your virtual environment is not in the default user directory.*

---

## Verifying the VSCode Integration

After completing the setup in `vscode/config.json` and `vscode/settings.json`, and restarting VSCode, the `gis-mcp` server will be automatically managed by the Gemini Code Assist extension. You can verify that the integration is working correctly by giving the chat assistant a command that uses the GIS tools.

1.  Open the Gemini Code Assist chat panel in VSCode.
2.  Enter the following command:
    ```
    Create a folder named "maps" in the current working directory
    ```
3.  The assistant should respond confirming the folder creation.
4.  You can verify this by checking for a new `maps` folder in your project's root directory (`C:\Portfolio\geoai-mcp-localstack\local-ai-dev\maps`).

This confirms that you have successfully set up a local, secure GIS-enabled AI assistant within VSCode, without relying on external services like Claude.

---

## Building a Custom GIS AI Agent (LangChain Tutorial)

This section outlines how to build a custom AI agent that runs **fully locally**. The following instructions are an updated, simplified, and more robust version of common online tutorials (such as the one found on Medium), designed to work with the latest libraries and avoid common errors.

This process is separate from the VSCode integration.

*Note: Due to recent updates in the `gis-mcp` library, the process has been simplified. You no longer need to run the GIS MCP server in a separate terminal.*

### 1. Install Dependencies

Open a PowerShell terminal and activate the virtual environment:

```powershell
# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

Ensure all dependencies are installed by running:

```bash
python -m uv pip install -r requirements.txt
```
*(If you encounter `ImportError` issues later, refer to the "Reinstalling Packages" section under "Troubleshooting LangChain Imports" below.)*

### 2. Create and Run the Agent

The `agent.py` script has been created to set up and run your custom agent. The updated script now:
1.  Connects to a local LLM (e.g., LM Studio).
2.  **Directly imports the GIS tools** from the installed `gis-mcp` package.
3.  Initializes a LangChain agent to use the LLM with the GIS tools.
4.  Provides an interactive command-line prompt for you to ask questions.

**Prerequisites for running the agent:**
- Your local LLM server (e.g., LM Studio, Ollama) must be running.

**To run the agent:**
In the terminal where your virtual environment is active, execute the following command:

```bash
python agent.py
```

You can then ask the agent questions like "Create a 100-meter buffer around the point (10, 20) and show me the result as WKT".

### Troubleshooting

**1. LangChain `ImportError`:**
The LangChain library is updated very frequently, which can lead to `ImportError` or `ModuleNotFoundError`. If you encounter such errors when running `agent.py`, you may need to find the new locations of the required components.

**2. Finding a File's Location:**
If you need to find where a specific component like `AgentExecutor` is located, you can search for its file (`agent_executor.py`) within your virtual environment.

On Windows PowerShell:
```powershell
Get-ChildItem -Path venv -Recurse -Filter "agent_executor.py"
```

On macOS/Linux:
```bash
find venv -name "agent_executor.py"
```

**3. Reinstalling Packages:**
If the steps above fail to locate the necessary components, the `langchain` installation may be in an inconsistent state. The most reliable solution is to uninstall and reinstall the core packages to ensure all dependencies are correctly aligned.

First, uninstall the existing packages:
```bash
python -m uv pip uninstall langchain langchain-core langchain-openai langchain-community
```

Then, reinstall them:
```bash
python -m uv pip install -r requirements.txt
```

**4. Prompt Template Errors:**
If you successfully run the agent but encounter an error during execution like "Only user and assistant roles are supported!", it means the prompt template in `agent.py` is not compatible with your specific local LLM. Many models do not support the "system" role. script.

### Recommended Models for Tool Calling (LM Studio)

If you encounter issues with your local LLM's ability to perform tool calling, or if you're looking for models specifically designed for this task, consider the following:

*   **Nexusflow/Nexus-Raven-V2-13B-GGUF:** This model is highly recommended as it was specifically trained for function/tool calling. It often outperforms larger, more general-purpose models for this task.
    *   **Reason:** Specialized for Function Calling, High Performance, Good Community Support (often comes with pre-configured prompt templates in LM Studio).
*   **Nous Research/Nous-Hermes-2-Mistral-7B-DPO-GGUF:** Another excellent choice known for its strong function calling capabilities.
*   **Meta-Llama-3-8B-Instruct-GGUF:** Llama 3 Instruct models have improved function calling abilities and are very popular.

When using these models in LM Studio, ensure that the correct "Prompt Template" is applied (often automatically detected). This is crucial for the agent to correctly interpret and execute tool calls.

**5. Context Length Error in LM Studio**

When you run `agent.py` and ask a question, you might encounter an error similar to this:

```
An error occurred during agent execution: Trying to keep the first X tokens when context the overflows. However, the model is loaded with context length of only 4096 tokens, which is not enough.
```

This error occurs because the prompt sent to the LLM (which includes your question and the descriptions of all 87 GIS tools) is larger than the model's default context window (e.g., 4096 tokens).

**Solution:**

The solution is to increase the context length in your LM Studio settings.

1.  Go to the **"My Models"** tab in LM Studio.
2.  Find your model (e.g., `nexusraven-v2-13b`) in the list.
3.  To the right of the model name, click the **gear icon (⚙️)**.
4.  In the model's parameters, find the **"Context Length"** (or `n_ctx`) setting.
5.  Change the value from `4096` to `16384` or higher.
6.  Save the settings.
7.  Go to the **"Server"** tab and **restart your server** to apply the new setting.

After restarting the server, the agent should be able to handle the large prompt and the error will be resolved.