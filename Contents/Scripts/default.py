#!/Users/justin/opt/anaconda3/envs/myenv/bin/python

import sys
import os
import subprocess

os.environ["PATH"] = "/usr/local/bin:" + os.environ.get("PATH", "")

argument = sys.argv[1] if len(sys.argv) > 1 else ""

try:
    result = subprocess.run(
        [
            "/Users/justin/opt/anaconda3/envs/myenv/bin/python",
            "/Users/justin/Library/Application Support/LaunchBar/Actions/mcp_agent.lbaction/Contents/Scripts/main.py",
            argument,
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    print(result.stdout, end="")

except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
