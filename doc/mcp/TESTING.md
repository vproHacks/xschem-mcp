# XSchem MCP Testing Strategy

## Scope

The test strategy covers:

- bridge policy enforcement
- tool-to-wrapper mapping
- transport behavior (TCP + stdio JSON-RPC)
- XSchem integration flows (netlist/sim/results)
- regression safety for destructive edits

## Layers

## 1. Unit tests (fast, offline)

Location: `tools/mcp_bridge/tests/`

- `test_policy.py`
  - allowlist enforcement
  - path traversal rejection
- `test_registry.py`
  - tool list shape
  - wrapper mapping
  - confirmation gate behavior

Run:

```bash
python3 -m unittest discover -s tools/mcp_bridge/tests -p "test_*.py"
```

## 2. Integration tests (XSchem required)

Proposed flow:

1. Start XSchem with `--tcp_port 2021`.
2. Register bridge in Gemini (`gemini mcp add ...`).
3. From Gemini, execute tool calls in order:
   - `xschem.get_context`
   - `xschem.insert_symbol`
   - `xschem.generate_netlist`
   - `xschem.run_simulation`
   - `xschem.read_simulation_results`

Assertions:

- wrappers return `status=ok`
- output file exists where expected
- simulation execution id is non-negative

## 3. Golden tests

Maintain canonical sample schematics and expected outputs:

- generated `.sym` files for known pin lists
- netlists for known input schematics
- normalized wrapper response snapshots

## 4. Failure mode tests

- bridge cannot reach XSchem TCP socket
- invalid symbol path/name
- simulator command missing from `simrc`
- malformed wrapper JSON response
- destructive tool call without `confirm=true`

## 5. Manual Gemini workflow checks

- Gemini can discover `xschem.*` tools via `/mcp`.
- Tool calls change the currently open XSchem instance.
- Bridge restart/reconnect is handled cleanly.
- Tool confirmation prompts behave as expected.

