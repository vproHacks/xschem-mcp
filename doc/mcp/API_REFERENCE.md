# API Reference

This reference describes MCP calls exposed by `tools/mcp_bridge`.

## MCP Methods

## `initialize`

Returns:

- `protocolVersion`
- `capabilities.tools`
- `serverInfo`

## `ping`

Returns:

- `{}`

## `tools/list`

Returns:

- `tools[]` with `{name, description, inputSchema}`

## `tools/call`

Parameters:

- `name`: tool name
- `arguments`: JSON object matching input schema

Result:

- `content[]` where `content[0].text` contains XSchem wrapper response
- `isError`: boolean

## Tool-to-Wrapper Mapping

- `xschem.start_process` -> local bridge handler (no Tcl wrapper)
- `xschem.stop_process` -> local bridge handler (no Tcl wrapper)
- `xschem.process_status` -> local bridge handler (no Tcl wrapper)
- `xschem.get_context` -> `mcp_get_context`
- `xschem.list_symbols` -> `mcp_list_symbols`
- `xschem.insert_symbol` -> `mcp_place_symbol`
- `xschem.create_symbol` -> `mcp_create_symbol`
- `xschem.set_instance_property` -> `mcp_set_instance_property`
- `xschem.generate_netlist` -> `mcp_generate_netlist`
- `xschem.run_simulation` -> `mcp_run_simulation`
- `xschem.read_simulation_results` -> `mcp_read_simulation_results`
- `xschem.annotate_operating_point` -> `mcp_annotate_operating_point`

## Example Requests

## List tools

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

## Insert symbol

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "xschem.insert_symbol",
    "arguments": {
      "symbol_name": "nmos.sym",
      "x": 100,
      "y": 200,
      "confirm": true
    }
  }
}
```

## Start XSchem on TCP port

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "xschem.start_process",
    "arguments": {
      "tcp_port": 2021
    }
  }
}
```

