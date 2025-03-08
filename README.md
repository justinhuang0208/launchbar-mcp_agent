# MCP Agent

This is a Launchbar action integrated with Langchain and MCP to automatically complete tasks based on your prompt.

## Configuration

Before using the application, ensure that you add a `.env` file to configure your LLM API key. Additionally, include an `mcp_config.json` file to set up your MCP.

The `mcp_config.json` should format like this:

```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "/your/folder/path1",
      "/your/folder/path2"
    ]
  },
  "fetch": {
    "command": "uvx",
    "args": [
      "mcp-server-fetch"
    ]
  }
}
```
The `suggestions.js` file is designed to activate autocomplete when you type "@", providing suggestions for the MCP server names. Furthermore, this function dynamically loads only the MCP server associated with the tool name you've specified. You have the flexibility to modify the keyword section within `suggestions.js` to align with the MCP server you have installed or to alter its name if you want.
