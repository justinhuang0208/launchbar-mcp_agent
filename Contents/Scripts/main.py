# Standard library imports
import asyncio
import logging
import json
import sys
from datetime import datetime
import os
os.environ['PATH'] = '/usr/local/bin:' + os.environ.get('PATH', '')
LLM_API_KEY = os.getenv('XAI_API_KEY')

# Third-party imports
try:
    from langchain.schema import HumanMessage
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
    import yaml
except ImportError as e:
    print(f'\nError: Required package not found: {e}')
    print('Please ensure all required packages are installed\n')
    sys.exit(1)

# Local application imports
from langchain_mcp_tools import convert_mcp_to_langchain_tools


# A very simple logger
def init_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,  # logging.DEBUG,
        format='\x1b[90m[%(levelname)s]\x1b[0m %(message)s'
    )
    return logging.getLogger()

def load_mcp_config(path: str = "mcp_config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_system_prompt(path: str = "system_prompt.txt") -> str:
    with open(path, encoding="utf-8") as f:
        return str(f)

def load_llm_config(path: str="llm_config.yaml") -> dict:
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
        mcp_config = load_mcp_config()
        mcp_tools, cleanup = await convert_mcp_to_langchain_tools(
            mcp_config,
            init_logger()
        )

        llm_config = load_llm_config()
        llm = ChatOpenAI(
            temperature=llm_config.get("temperature"),
            openai_api_base=llm_config.get("base_url"),
            openai_api_key=LLM_API_KEY,
            model=llm_config.get("model")
        )

        system_prompt = load_system_prompt()

        agent = create_react_agent(
            llm,
            mcp_tools,
            prompt = system_prompt + "Today is:" + str(datetime.today())
        )

        messages = [HumanMessage(content=request)]

        result = await agent.ainvoke({'messages': messages})

        # the last message should be an AIMessage
        response = result['messages'][-1].content

        # print('\x1b[36m')  # color to cyan
        print(response)
        # print('\x1b[0m')   # reset the color

    finally:
        if cleanup is not None:
            await cleanup()

def main() -> None:
    if len(sys.argv) > 1:
        request = sys.argv[1]
    asyncio.run(run(request))


if __name__ == '__main__':
    main()
