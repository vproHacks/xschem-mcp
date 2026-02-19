# Operations Guide

## Prerequisites

- XSchem built and runnable.
- Python 3.9+.
- Local Gemini CLI installed and available in PATH (`gemini`).
- VS Code with GitHub Copilot enabled (for Copilot MCP workflow).

## System-wide installation (for agent usage across the system)

To use the XSchem MCP server in any project (Cursor, Copilot, or Gemini) without keeping config inside this repo:

1. **Choose a stable install location**  
   Clone or copy this repo to a fixed path, e.g. `~/xschem-mcp` or `/opt/xschem-mcp`. The MCP config will point at this path.

2. **Cursor (user-level, all workspaces)**  
   Create or edit `~/.cursor/mcp.json` and add the `xschem` server with **absolute paths** to the launcher and optional audit log:

   ```json
   {
     "mcpServers": {
       "xschem": {
         "command": "python3",
         "args": [
           "/path/to/xschem-mcp/tools/mcp_bridge/launcher.py",
           "--xschem-host", "127.0.0.1",
           "--xschem-port", "2021",
           "--audit-log", "/tmp/xschem-mcp-audit.jsonl",
           "--allow-destructive-without-confirm"
         ]
       }
     }
   }
   ```  
   Replace `/path/to/xschem-mcp` with your actual install path (e.g. `$HOME/xschem-mcp` or `/opt/xschem-mcp`).

3. **Start XSchem when needed**  
   Either run `xschem --tcp_port 2021` yourself, or use the MCP tool `xschem.start_process` with `{"tcp_port": 2021}` so the bridge can start XSchem.

4. **No pip install**  
   The bridge uses only Python 3.9+ standard library; no extra packages are required.

After this, Cursor will load the XSchem MCP server in every workspace. Restart Cursor or run **MCP: List Servers** to confirm `xschem` appears.

## Start Sequence (Gemini terminal workflow)

## 1) Start XSchem remote endpoint

```bash
xschem --tcp_port 2021
```

Alternative from MCP:

- call `xschem.start_process` with `{"tcp_port": 2021}` to spawn XSchem from the bridge
- call `xschem.process_status` to inspect managed process state
- call `xschem.stop_process` to stop a bridge-managed XSchem process

## 2) Configure MCP client

### Gemini CLI (project-scoped)

```bash
gemini mcp add -s project xschem python3 -m tools.mcp_bridge.main --xschem-port 2021 --negotiate-port --audit-log /tmp/xschem-mcp-audit.jsonl
```

### Cursor

Use the project file `.cursor/mcp.json` (already included in this repository).

### GitHub Copilot in VS Code

Use the project file `.vscode/mcp.json` (already included in this repository).  
This file uses VS Code's `servers` format and starts `tools/mcp_bridge/launcher.py` over stdio.

## 3) Verify MCP connectivity

### Gemini CLI

```bash
gemini mcp list
gemini
```

### Copilot (VS Code)

- Open Command Palette and run `MCP: List Servers`
- Confirm `xschem` appears and is started
- If prompted, approve MCP trust for the workspace server
- Open Copilot Chat (Agent mode) and run a tool-using prompt, e.g. "Use xschem.get_context"

## Useful Flags

- `--xschem-timeout`: per-command timeout (seconds).
- `--xschem-retries`: retry count on socket failures.
- `--allow-destructive-without-confirm`: disable default confirmation gate.
- `--audit-log`: write JSONL logs to file.

## Troubleshooting

## Bridge cannot connect to XSchem

- verify XSchem is running
- verify `--tcp_port` matches bridge port
- check local firewall rules on loopback

## Wrapper response parse errors

- verify `src/xschem.tcl` includes `mcp_*` wrappers
- manually test via netcat:

```bash
echo 'mcp_get_context' | nc localhost 2021
```

## Gemini MCP failures

- confirm CLI is installed:

```bash
gemini --help
```

- re-register server with explicit scope:

```bash
gemini mcp remove -s project xschem
gemini mcp add -s project xschem python3 -m tools.mcp_bridge.main --xschem-port 2021 --negotiate-port
```

## Copilot MCP failures

- check `.vscode/mcp.json` exists and contains an `xschem` server entry
- run `MCP: List Servers` and inspect server output for startup errors
- run `MCP: Reset Cached Tools` if tool list looks stale
- verify XSchem is running with `--tcp_port 2021`

## Observability

- standard logs go to stderr in JSON lines.
- optional persistent audit logs via `--audit-log`.
- each tool call includes tool name and wrapper status/code.

