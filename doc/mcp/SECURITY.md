# XSchem MCP Security Model

## Threat Model

Primary risks for LLM-driven EDA automation:

- Arbitrary command execution through Tcl injection.
- Unintended destructive edits to schematics/symbols.
- Path traversal while creating/reading symbols/netlists/raw files.
- Unsafe prompt content causing data exfiltration through Gemini CLI.
- Missing auditability for automated operations.

## Guardrails Implemented

## 1. Tool allowlist

The bridge only exposes allowlisted tools from `tools/mcp_bridge/policy.py`.  
Unknown tools are rejected with `PermissionError`.

## 2. Wrapper-only execution

The bridge does **not** send arbitrary Tcl from MCP callers.  
It maps tools to fixed wrapper functions (`mcp_*`) in `src/xschem.tcl`.

## 3. Input validation

Bridge validation enforces:

- size limits for string/list arguments
- path traversal checks for path-like parameters
- symbol path restrictions (disallow absolute symbol paths)

## 4. Confirmation policy

Destructive tools require `confirm=true` by default:

- `xschem.stop_process`
- `xschem.insert_symbol`
- `xschem.create_symbol`
- `xschem.set_instance_property`

Can be disabled with `--allow-destructive-without-confirm` for trusted workflows.

## 5. Structured audit logs

Bridge supports JSONL logs via:

```bash
python3 -m tools.mcp_bridge.main --audit-log /tmp/xschem-mcp-audit.jsonl
```

Each call includes tool name and wrapper status/code.

## 6. Recommended operational controls

- Run bridge on local loopback only.
- Keep XSchem TCP listener local and non-public.
- Use dedicated user account/workspace for automation jobs.
- Review destructive tool usage from audit logs.
- Treat Gemini responses as untrusted suggestions; validate before execution.

## Future Hardening

- Add request signing or local auth token between Gemini client and bridge.
- Add per-tool path allowlists (project-only, netlist-only).
- Add secret redaction in logs.
- Add explicit multi-step approvals for bulk edits.

