# Contributing to XSchem MCP Tooling

## Add a New XSchem MCP Tool

## Step 1: Add/extend wrapper in XSchem Tcl

Edit `src/xschem.tcl`:

- add `mcp_<action>` wrapper
- validate arguments
- return normalized JSON (`status`, `code`, `message`, `data`)

## Step 2: Add schema

Edit `tools/mcp_bridge/schemas.py`:

- add `ToolSpec`
- define `input_schema`

Optionally mirror schema in `doc/mcp/schemas/tools.json`.

## Step 3: Update policy

Edit `tools/mcp_bridge/policy.py`:

- add allowlist entry in `TOOL_POLICY`
- mark destructive operations
- add custom validation if required

## Step 4: Add mapping

Edit `tools/mcp_bridge/tool_registry.py`:

- map tool args to wrapper positional arguments in `_map_args`

## Step 5: Add tests

- unit test wrapper mapping and policy behavior in `tools/mcp_bridge/tests/`
- add integration scenarios to `doc/mcp/TESTING.md`

## Step 6: Update docs

- update `doc/mcp/API_REFERENCE.md`
- update `doc/mcp/TOOL_SCHEMAS.md`
- update security/operations docs if behavior changes

## Coding Guidelines

- Keep wrappers deterministic and side-effect boundaries clear.
- Do not expose raw arbitrary Tcl execution to MCP callers.
- Prefer additive schema changes to preserve backward compatibility.

