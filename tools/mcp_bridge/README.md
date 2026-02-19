# XSchem MCP Bridge (Python)

This bridge exposes XSchem operations as MCP tools so Gemini CLI can call them directly from your terminal session.

## Components

- `xschem_client.py`: TCP client for XSchem remote Tcl interface.
- `tool_registry.py`: MCP tool routing and argument mapping.
- `policy.py`: Tool allowlist + confirmation gates for destructive operations.
- `mcp_stdio_server.py`: MCP stdio server (Content-Length framed JSON-RPC).
- `main.py`: CLI entrypoint.

## Startup

Start XSchem with remote TCP enabled:

```bash
xschem --tcp_port 2021
```

Run bridge (MCP server process):

```bash
python3 -m tools.mcp_bridge.main --xschem-port 2021 --negotiate-port
```

## Register with Gemini CLI

Use Gemini CLI's MCP registration command:

```bash
gemini mcp add -s project xschem python3 /home/vraj/Documents/xschem-mcp/tools/mcp_bridge/launcher.py --xschem-port 2021
```

Optional trusted mode (skip confirmations in Gemini):

```bash
gemini mcp add -s project --trust xschem python3 /home/vraj/Documents/xschem-mcp/tools/mcp_bridge/launcher.py --xschem-port 2021 --allow-destructive-without-confirm
```

Inspect registration:

```bash
gemini mcp list
```

## Exposed MCP methods (server side)

- `initialize`
- `ping`
- `tools/list`
- `tools/call`

## Notes

- Destructive tools require `confirm: true` by default.
- Wrapper commands are limited to `mcp_*` functions defined in `src/xschem.tcl`.
- Responses from XSchem wrappers must be JSON strings.

