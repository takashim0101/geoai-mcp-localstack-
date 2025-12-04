# agent.py

import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_classic.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool as LangChainTool
from langchain_core.agents import AgentAction, AgentFinish
from langchain_classic.agents.output_parsers import ReActSingleInputOutputParser
from langchain_classic.agents import create_react_agent
from gis_mcp.mcp import gis_mcp

# --- 1. Robust Parser for Llama 3 ---
class Llama3RobustOutputParser(ReActSingleInputOutputParser):
    def parse(self, text: str):
        # Replace "Input:" with "Action Input:"
        text = re.sub(r'^Input:', 'Action Input:', text, flags=re.MULTILINE)
        text = text.replace("```json", "").replace("```", "")

        # Handle cases where Action and Final Answer are mixed
        if "Action:" in text and "Final Answer:" in text:
            if text.find("Action:") < text.find("Final Answer:"):
                text = text.split("Final Answer:")[0].strip()

        # Emergency escape for empty or symbol-only responses
        if text.strip() in ["`", "``", "```", ""]:
            return AgentFinish(
                return_values={"output": "The tool executed successfully, but the AI stopped generating text due to output length. Check the logs for details."},
                log=text
            )

        # Correct for unclosed JSON
        if "Action Input:" in text:
            lines = text.strip().splitlines()
            if lines and not lines[-1].strip().endswith("}"):
                text += "}"

        try:
            return super().parse(text)
        except Exception as e:
            return AgentFinish(return_values={"output": f"Raw Output: {text}"}, log=text)

# --- 2. Tool Wrapper (with Output Summarization) ---
def wrap_tool(tool):
    def wrapper(*args, **kwargs):
        # --- Organize Input Arguments ---
        if args:
            candidate = args[0]
            if isinstance(candidate, str):
                try:
                    candidate = candidate.strip()
                    # Reject Python tuples like (10, 20)
                    if candidate.startswith("(") and ")" in candidate:
                         return "Error: Invalid JSON. Do not use tuples. Use format: {\"geometry\": \"POINT(10 20)\", ...}"
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        kwargs.update(parsed)
                except json.JSONDecodeError:
                    pass
            elif isinstance(candidate, dict):
                kwargs.update(candidate)

        if "tool_input" in kwargs and isinstance(kwargs["tool_input"], dict):
            kwargs.update(kwargs.pop("tool_input"))

        # --- Execute Tool ---
        try:
            if tool.name == "buffer":
                geometry = kwargs.get("geometry")
                distance = kwargs.get("distance")
                # Simple guard for when the user writes "point" instead of "POINT(10 20)"
                if geometry and "POINT" not in str(geometry).upper() and "POLYGON" not in str(geometry).upper():
                     return f"Error: Invalid geometry format '{geometry}'. You MUST use WKT format like 'POINT(10 20)'."

                if geometry is None or distance == None:
                    return f"Error: 'buffer' tool requires 'geometry' and 'distance'. Received: {kwargs}"
                result = tool.fn(geometry, distance)
            else:
                result = tool.fn(**kwargs)
        except Exception as e:
            return f"Tool Execution Error: {e}"

        # --- Output Summarization ---
        result_str = str(result)
        MAX_LENGTH = 300
        
        if len(result_str) > MAX_LENGTH:
            if isinstance(result, dict) and 'geometry' in result:
                short_geom = str(result['geometry'])[:50] + "... (truncated)"
                result_copy = result.copy()
                result_copy['geometry'] = short_geom
                return str(result_copy)
            return result_str[:MAX_LENGTH] + f"... [Output truncated. Total length: {len(result_str)} chars]"
        
        return result

    return LangChainTool(name=tool.name, func=wrapper, description=tool.description)

def main():
    print("--- Setting up the GIS AI Agent (v5 - WKT Format Enforced) ---")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "lmstudio")

    if LLM_PROVIDER == "lmstudio":
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="local-model",
            temperature=0,
            stop=["Observation:", "\nObservation:"]
        )
        print("LLM configured: LM Studio (Llama 3)")
    else:
        llm = ChatOllama(model="llama3", temperature=0, stop=["Observation:", "\nObservation:"])

    fastmcp_tools = list(gis_mcp._tool_manager._tools.values())
    gis_tools = [wrap_tool(tool) for tool in fastmcp_tools]
    print(f"Loaded {len(gis_tools)} tools.")

    # IMPORTANT: Re-added specific WKT examples to the prompt.
    system_template = """You are a GIS Agent. 
    You will be given a task. You must use tools to solve it.

    TOOLS:
    {tools}

    TOOL NAMES:
    {tool_names}

    IMPORTANT RULES:
    1. ONLY generate "Thought", "Action", and "Action Input". 
    2. **STOP** immediately after writing "Action Input".
    3. 'Action Input' must be valid JSON.
    4. **CRITICAL**: Geometries MUST be in WKT format.
       - CORRECT: "POINT(10 20)"
       - WRONG: "point", "(10, 20)", "{{\"x\": 10, \"y\": 20}}"

    FORMAT:

    Question: the input question
    Thought: I need to use a tool.
    Action: the tool name (one of [{tool_names}])
    Action Input: {{'key': 'value'}}
    Observation: (Wait for this!)
    ... 
    Final Answer: (Only write this after you have an Observation)

    --- EXAMPLE (Follow this exactly) ---
    Question: Buffer the point (10, 20) by 100 meters.
    Thought: I need to buffer the point. I will format the point as WKT.
    Action: buffer
    Action Input: {{"geometry": "POINT(10 20)", "distance": 100}}
    Observation: POLYGON((110 20, ...))
    Final Answer: The buffered polygon is POLYGON((110 20, ...))
    -------------------------------------

    Begin!
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}"),
        ]
    )

    agent = create_react_agent(llm, gis_tools, prompt, output_parser=Llama3RobustOutputParser())

    agent_executor = AgentExecutor(
        agent=agent,
        tools=gis_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    print("\n--- Agent is ready. Type 'exit' to quit. ---")

    while True:
        user_input = input("Ask your GIS question: ")
        if user_input.lower() == "exit":
            break

        try:
            # Add a reminder to the user input as well
            hinted_input = f"{user_input}\n(Remember: Use WKT format like 'POINT(x y)' for geometry)"
            result = agent_executor.invoke({"input": hinted_input})
            print("\n--- Final Answer ---")
            print(result.get("output"))
            print("--------------------\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()