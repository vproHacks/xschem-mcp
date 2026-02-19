# XSchem MCP Tool Contracts

This document defines the first stable MCP tool contract for XSchem + Gemini integration.

## Response Envelope

All XSchem wrappers (`mcp_*` in `src/xschem.tcl`) return a JSON string:

```json
{
  "status": "ok|error",
  "code": "ok|<error_code>",
  "message": "<human_message>",
  "timestamp": "unix_epoch_seconds",
  "data": { "...": "..." }
}
```

Bridge-side MCP tool responses follow MCP `tools/call` shape:

- `content[0].type = "text"`
- `content[0].text = serialized wrapper response`
- `isError = true` when wrapper `status != "ok"` or bridge execution fails

## Tool List

- `xschem.start_process`
- `xschem.stop_process`
- `xschem.process_status`
- `xschem.get_context`
- `xschem.list_symbols`
- `xschem.insert_symbol`
- `xschem.create_symbol`
- `xschem.set_instance_property`
- `xschem.generate_netlist`
- `xschem.run_simulation`
- `xschem.read_simulation_results`
- `xschem.annotate_operating_point`

## Error Taxonomy

### Bridge Errors

- `bridge.connection_error`: TCP connection failure, timeout, socket reset.
- `bridge.invalid_response`: non-JSON wrapper response.
- `bridge.permission_denied`: non-allowlisted tool or missing confirmation.
- `bridge.tool_mapping_error`: tool exists but no mapper/wrapper configured.
- `bridge.process_start_error`: failed to spawn or ready-check XSchem process.

### Wrapper Errors

- `context_error`
- `list_symbols_error`
- `place_symbol_error`
- `create_symbol_error`
- `set_instance_property_error`
- `generate_netlist_error`
- `run_simulation_error`
- `read_simulation_results_error`
- `annotate_operating_point_error`

## Compatibility Rules

- New tools must be additive; avoid breaking input schema for existing tools.
- Existing wrapper names should not change once published.
- `data` fields can be extended with new keys, but existing keys should be preserved.

