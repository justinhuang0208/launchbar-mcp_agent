# Standard library imports
import asyncio
from contextlib import AsyncExitStack
import inspect
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Third-party imports
try:
    import yaml
    from agno.agent.agent import Agent
    from agno.run.agent import RunOutput
    from agno.models.openai.like import OpenAILike
    from agno.tools.mcp import MCPTools
    from agno.tools.shell import ShellTools
    from agno.utils.pprint import pprint_run_response
except ImportError as e:
    print(f"\nError: Required package not found: {e}")
    print("Please ensure all required packages are installed\n")
    sys.exit(1)

# Local application imports

BASE_DIR = Path(__file__).resolve().parent


def resolve_path(path: str) -> Path:
    file_path = Path(path)
    if file_path.is_absolute():
        return file_path
    return BASE_DIR / file_path


load_dotenv(dotenv_path=resolve_path(".env"))


# A very simple logger
def init_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="\x1b[90m[%(levelname)s]\x1b[0m %(message)s",
    )
    return logging.getLogger()


def load_mcp_config(request: str = "", path: str = "mcp_config.json") -> dict:
    with resolve_path(path).open(encoding="utf-8") as f:
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
    with resolve_path(path).open(encoding="utf-8") as f:
        return f.read()


def load_llm_config(path: str = "llm_config.yaml") -> dict[str, str | float]:
    try:
        with resolve_path(path).open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config if config is not None else {}
    except Exception as e:
        print(f"Error occurred while reading the configuration file: {e}")
        return {}


async def run(request: str) -> int:
    """Run agent with Agno MCP tools."""
    # load MCP config and prepare tool commands
    mcp_config = load_mcp_config(request)
    commands = []
    allowed_commands = []
    extra_env = {}

    for cfg in mcp_config.values():
        cmd = cfg.get("command", "")
        args = cfg.get("args", [])
        full = cmd + (" " + " ".join(args) if args else "")
        commands.append(full)
        if cmd:
            allowed_commands.append(cmd)
        # 收集工具專屬環境變數
        extra_env.update(cfg.get("env", {}))

    # 合併系統環境、ALLOW_COMMANDS 與工具專屬 env
    unique_allowed = sorted(set(allowed_commands))
    env = {
        **os.environ,
        **({"ALLOW_COMMANDS": ",".join(unique_allowed)} if unique_allowed else {}),
        **extra_env
    }

    # run with multiple MCP servers
    async with AsyncExitStack() as stack:
        mcp_tools = []
        for command in commands:
            tool = await stack.enter_async_context(MCPTools(command=command, env=env))
            mcp_tools.append(tool)

        llm_config = load_llm_config()
        # get environment variable name for API key
        key_name = llm_config.get("LLM_KEY_NAME", "")
        llm = OpenAILike(
            id=str(llm_config.get("model")),
            temperature=float(llm_config.get("temperature", 1)),
            base_url=str(llm_config.get("base_url")),
            api_key=os.environ.get(str(key_name)),
        )

        system_prompt = load_system_prompt()

        # initialize Agno agent
        agent_kwargs = dict(
            model=llm,
            tools=[*mcp_tools, ShellTools()],
            instructions=system_prompt + " Today is: " + str(datetime.today()) + "",
            markdown=True,
        )
        if "show_tool_calls" in inspect.signature(Agent.__init__).parameters:
            agent_kwargs["show_tool_calls"] = True
        agent = Agent(**agent_kwargs)

        # run agent and only print the raw response content
        response_obj: RunOutput = await agent.arun(request, stream=False)
        # pprint_run_response(response_obj, markdown=True)
        print(response_obj.content)
        return 0


def main() -> None:
    if len(sys.argv) > 1:
        request = sys.argv[1]
    else:
        print("Error: No request provided as a command-line argument.")
        sys.exit(1)
    exit_code = asyncio.run(run(request))
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
