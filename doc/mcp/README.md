# XSchem MCP Integration Docs

This folder documents terminal-first MCP integration for XSchem across Gemini CLI, Cursor, and GitHub Copilot.

## Documents

- `ARCHITECTURE.md`: system components, data flows, and boundaries.
- `TOOL_SCHEMAS.md`: MCP tool contracts + error taxonomy.
- `SECURITY.md`: threat model and runtime guardrails.
- `TESTING.md`: unit/integration/golden/failure testing strategy.
- `OPERATIONS.md`: install/run/troubleshooting guide.
- `CONTRIBUTING.md`: how to add new tools and wrappers safely.
- `schemas/tools.json`: machine-readable JSON schema bundle.

## Source Touchpoints

- XSchem wrappers: `src/xschem.tcl` (`mcp_*` procs)
- Bridge runtime: `tools/mcp_bridge/`

