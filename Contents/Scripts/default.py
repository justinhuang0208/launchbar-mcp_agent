#!/opt/miniconda3/envs/mcp_agent/bin/python

import os
import json
import subprocess
import sys
from pathlib import Path

os.environ["PATH"] = "/usr/local/bin:" + os.environ.get("PATH", "")

PYTHON_BIN = "/opt/miniconda3/envs/mcp_agent/bin/python"
IGNORED_STDERR_PREFIXES = (
    "Secure MCP Filesystem Server running on stdio",
    "Client does not support MCP Roots, using allowed directories set from server args:",
)
IGNORED_STDOUT_PREFIXES = (
    "INFO Running shell command:",
    "[INFO] Running shell command:",
    "\x1b[90m[INFO]\x1b[0m Running shell command:",
)


def filter_prefixed_lines(text: str, ignored_prefixes: tuple[str, ...]) -> str:
    return "".join(
        line
        for line in text.splitlines(keepends=True)
        if not any(line.lstrip().startswith(prefix) for prefix in ignored_prefixes)
    )


def extract_launchbar_json(text: str) -> str | None:
    """Extract the first valid JSON object/array from mixed stdout."""
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in ("[", "{"):
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, (list, dict)):
            return json.dumps(payload, ensure_ascii=False)
    return None


def resolve_main_script() -> Path:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "main.py",
        script_dir / "Contents" / "Scripts" / "main.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def main() -> None:
    argument = sys.argv[1] if len(sys.argv) > 1 else ""
    main_script = resolve_main_script()

    if not main_script.exists():
        print(f"Error: cannot find main.py at {main_script}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [PYTHON_BIN, str(main_script), argument],
        text=True,
        capture_output=True,
    )

    if result.stdout:
        filtered_stdout = filter_prefixed_lines(
            result.stdout, IGNORED_STDOUT_PREFIXES
        )
        if filtered_stdout:
            extracted_json = extract_launchbar_json(filtered_stdout)
            print(extracted_json if extracted_json is not None else filtered_stdout, end="")
    if result.stderr:
        filtered_stderr = "\n".join(
            line
            for line in result.stderr.splitlines()
            if line and not line.startswith(IGNORED_STDERR_PREFIXES)
        )
        if filtered_stderr:
            print(filtered_stderr, file=sys.stderr, end="\n")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
