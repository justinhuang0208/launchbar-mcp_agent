#!/Users/justin/opt/anaconda3/envs/myenv/bin/python

import sys
import os
import subprocess

os.environ["PATH"] = "/usr/local/bin:" + os.environ.get("PATH", "")

argument = sys.argv[1] if len(sys.argv) > 1 else ""

try:
    result = subprocess.Popen(
        [
            "/Users/justin/opt/anaconda3/envs/myenv/bin/python",
            "/Users/justin/Library/Application Support/LaunchBar/Actions/mcp_agent.lbaction/Contents/Scripts/main.py",
            argument,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )
    for line in iter(result.stdout.readline, ""):
        print(line.strip())

except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
