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

async def run(request: str) -> None:
    """Initializes MCP tools and returns tools and cleanup function."""
    try:
        mcp_configs = load_mcp_config()
        mcp_tools, cleanup = await convert_mcp_to_langchain_tools(
            mcp_configs,
            init_logger()
        )

        llm = ChatOpenAI(
            temperature=0.8,
            openai_api_base="https://api.x.ai/v1",
            openai_api_key=LLM_API_KEY,
            model="grok-2"
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
