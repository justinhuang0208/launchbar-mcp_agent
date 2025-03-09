# Standard library imports
import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv

# Third-party imports
try:
    import yaml
    from langchain.schema import HumanMessage
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
except ImportError as e:
    print(f"\nError: Required package not found: {e}")
    print("Please ensure all required packages are installed\n")
    sys.exit(1)

# Local application imports
from langchain_mcp_tools import convert_mcp_to_langchain_tools

load_dotenv()


# A very simple logger
def init_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="\x1b[90m[%(levelname)s]\x1b[0m %(message)s",
    )
    return logging.getLogger()


def load_mcp_config(request: str = "", path: str = "mcp_config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        config = json.load(f)

    matched_commands = re.findall(r"@([^\s]+)", request)
    if not matched_commands:
        return {}

    unique_commands = []
    [
        unique_commands.append(cmd)
        for cmd in matched_commands
        if cmd not in unique_commands
    ]

    filtered_config = {}
    for cmd in unique_commands:
        if cmd in config:
            filtered_config[cmd] = config[cmd]

    return filtered_config


def load_system_prompt(path: str = "system_prompt.txt") -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_llm_config(path: str = "llm_config.yaml") -> dict[str, str | float]:
    try:
        with open(path, encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config if config is not None else {}
    except Exception as e:
        print(f"Error occurred while reading the configuration file: {e}")
        return {}


async def run(request: str) -> None:
    """Initializes MCP tools and returns tools and cleanup function."""
    try:
        mcp_config = load_mcp_config(request)
        mcp_tools, cleanup = await convert_mcp_to_langchain_tools(
            mcp_config, init_logger()
        )

        llm_config = load_llm_config()
        llm = ChatOpenAI(
            temperature=float(llm_config.get("temperature", 0.8)),
            base_url=str(llm_config.get("base_url")),
            api_key=os.environ.get(llm_config.get("LLM_KEY_NAME")),
            model=str(llm_config.get("model")),
            verbose=True,
        )

        system_prompt = load_system_prompt()

        agent = create_react_agent(
            llm, mcp_tools, prompt=system_prompt + "Today is:" + str(datetime.today())
        )

        messages = [HumanMessage(content=request)]

        result = await agent.ainvoke({"messages": messages})

        response = result["messages"][-1].content

        print(response)

    finally:
        if cleanup is not None:
            await cleanup()


def main() -> None:
    if len(sys.argv) > 1:
        request = sys.argv[1]
    asyncio.run(run(request))


if __name__ == "__main__":
    main()
