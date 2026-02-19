from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonSchema = dict[str, Any]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: JsonSchema


TOOL_SPECS: dict[str, ToolSpec] = {
    "xschem.start_process": ToolSpec(
        name="xschem.start_process",
        description=(
            "Start a local XSchem process with a specific TCP port by running "
            "`xschem --tcp_port <port>`. If a process is already listening on that port, "
            "returns status='already_running'."
        ),
        input_schema={
            "type": "object",
            "required": ["tcp_port"],
            "properties": {
                "tcp_port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535,
                    "description": "TCP port for XSchem remote control.",
                },
                "command": {
                    "type": "string",
                    "default": "xschem",
                    "description": "Executable name/path for XSchem.",
                },
                "extra_args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Extra CLI args passed to XSchem.",
                },
                "cwd": {
                    "type": "string",
                    "default": "",
                    "description": "Optional working directory for the XSchem process.",
                },
                "display": {
                    "type": "string",
                    "default": "",
                    "description": "Optional X11 DISPLAY override (for example ':0'). Leave empty to inherit bridge environment.",
                },
                "startup_timeout_seconds": {
                    "type": "number",
                    "default": 8.0,
                    "description": "How long to wait for the TCP port to become ready.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.stop_process": ToolSpec(
        name="xschem.stop_process",
        description=(
            "Stop an XSchem process previously started by xschem.start_process. "
            "Returns status='not_managed' if the bridge did not start that process."
        ),
        input_schema={
            "type": "object",
            "required": ["tcp_port"],
            "properties": {
                "tcp_port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535,
                },
                "force": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use SIGKILL if true; otherwise graceful terminate first.",
                },
                "confirm": {
                    "type": "boolean",
                    "default": False,
                    "description": "Required when destructive confirmations are enabled in bridge config.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.process_status": ToolSpec(
        name="xschem.process_status",
        description=(
            "Get status for bridge-managed XSchem processes. "
            "If tcp_port is provided, returns status for that port; otherwise returns all managed processes."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "tcp_port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535,
                }
            },
            "additionalProperties": False,
        },
    ),
    "xschem.get_context": ToolSpec(
        name="xschem.get_context",
        description="Get current XSchem context (open file, selection, netlist settings).",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.list_symbols": ToolSpec(
        name="xschem.list_symbols",
        description="List loaded symbols.",
        input_schema={
            "type": "object",
            "properties": {"include_derived": {"type": "boolean", "default": False}},
            "additionalProperties": False,
        },
    ),
    "xschem.search_symbols": ToolSpec(
        name="xschem.search_symbols",
        description=(
            "Search available symbols across all XSchem library paths. "
            "Returns the symbol filename (e.g. 'res.sym'), its library, and absolute path. "
            "Pass the filename directly to insert_symbol as symbol_name. "
            "Use glob patterns: 'res*' for resistors, 'nmos*' for NMOS, '*source*' for sources, '*' for all."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "default": "*",
                    "description": "Glob pattern to match symbol names (without .sym extension). Examples: 'res*', 'nmos*', '*source*', '*'.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.insert_symbol": ToolSpec(
        name="xschem.insert_symbol",
        description=(
            "Insert a symbol instance at explicit coordinates. "
            "symbol_name must be a library-relative name (e.g. 'res.sym', 'capa.sym', 'vsource.sym'), "
            "NOT a path with directory prefix. Use xschem.search_symbols to discover valid names."
        ),
        input_schema={
            "type": "object",
            "required": ["symbol_name", "x", "y"],
            "properties": {
                "symbol_name": {"type": "string", "description": "Library-relative symbol name, e.g. 'res.sym'. Use search_symbols to find valid names."},
                "x": {"type": "number"},
                "y": {"type": "number"},
                "rot": {"type": "integer", "default": 0},
                "flip": {"type": "integer", "default": 0},
                "inst_props": {"type": "string", "default": ""},
                "batch_continues": {"type": "boolean", "default": False},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.wire": ToolSpec(
        name="xschem.wire",
        description=(
            "Draw a wire (electrical connection) between two points. "
            "Wires connect component pins. Use coordinates that align with pin endpoints. "
            "For L-shaped routes, call this tool twice (horizontal segment + vertical segment). "
            "Pins on standard symbols are spaced 20 units apart; pin endpoints are shown in xschem.get_context."
        ),
        input_schema={
            "type": "object",
            "required": ["x1", "y1", "x2", "y2"],
            "properties": {
                "x1": {"type": "number", "description": "Start X coordinate"},
                "y1": {"type": "number", "description": "Start Y coordinate"},
                "x2": {"type": "number", "description": "End X coordinate"},
                "y2": {"type": "number", "description": "End Y coordinate"},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.create_symbol": ToolSpec(
        name="xschem.create_symbol",
        description="Create a new .sym file from pin lists.",
        input_schema={
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "in": {"type": "array", "items": {"type": "string"}, "default": []},
                "out": {"type": "array", "items": {"type": "string"}, "default": []},
                "inout": {"type": "array", "items": {"type": "string"}, "default": []},
                "overwrite": {"type": "boolean", "default": False},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.set_instance_property": ToolSpec(
        name="xschem.set_instance_property",
        description="Set an instance property token=value.",
        input_schema={
            "type": "object",
            "required": ["instance", "token", "value"],
            "properties": {
                "instance": {"type": "string"},
                "token": {"type": "string"},
                "value": {"type": "string"},
                "fast": {"type": "boolean", "default": False},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.generate_netlist": ToolSpec(
        name="xschem.generate_netlist",
        description=(
            "Generate a SPICE netlist from the current schematic. "
            "Creates the simulation directory if needed. "
            "Returns the netlist file path, size, and any ERC messages. "
            "You MUST call save_schematic before this tool."
        ),
        input_schema={
            "type": "object",
            "properties": {"filename": {"type": "string", "default": ""}},
            "additionalProperties": False,
        },
    ),
    "xschem.run_simulation": ToolSpec(
        name="xschem.run_simulation",
        description=(
            "Run ngspice simulation in batch mode on the current netlist. "
            "You MUST call save_schematic then generate_netlist BEFORE this. "
            "Returns simulator stdout/stderr output, exit code, and paths to the .raw and .log files. "
            "If the simulation fails, the output contains ngspice error messages explaining why."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.read_simulation_results": ToolSpec(
        name="xschem.read_simulation_results",
        description="Load raw simulation results into XSchem.",
        input_schema={
            "type": "object",
            "properties": {
                "raw_file": {"type": "string", "default": ""},
                "sim_type": {"type": "string", "default": ""},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.save_schematic": ToolSpec(
        name="xschem.save_schematic",
        description=(
            "Save the current schematic. If filename is omitted, saves to the current file path "
            "(fails if the schematic is unnamed). If filename is provided, saves as that path "
            "(like 'Save As'). You MUST save before generating a netlist or running a simulation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "default": "",
                    "description": "Path to save to. Leave empty to save to current file. Use absolute path or relative to XSchem working dir.",
                },
                "type": {
                    "type": "string",
                    "enum": ["schematic", "symbol"],
                    "default": "schematic",
                    "description": "File type: 'schematic' (.sch) or 'symbol' (.sym).",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.delete": ToolSpec(
        name="xschem.delete",
        description=(
            "Delete wires, instances, or all objects from the schematic. "
            "Modes: 'instance' (by name, e.g. 'R1'), 'wire' (by index), "
            "'area' (everything in a bounding box), 'all' (clear entire schematic)."
        ),
        input_schema={
            "type": "object",
            "required": ["target"],
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["instance", "wire", "area", "all"],
                    "description": "What to delete: 'instance', 'wire', 'area', or 'all'.",
                },
                "name": {
                    "type": "string",
                    "description": "Instance name (required when target='instance'). E.g. 'R1', 'V1'.",
                },
                "index": {
                    "type": "integer",
                    "description": "Wire index (required when target='wire').",
                },
                "x1": {"type": "number", "description": "Area left X (required when target='area')."},
                "y1": {"type": "number", "description": "Area top Y (required when target='area')."},
                "x2": {"type": "number", "description": "Area right X (required when target='area')."},
                "y2": {"type": "number", "description": "Area bottom Y (required when target='area')."},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.reload_schematic": ToolSpec(
        name="xschem.reload_schematic",
        description=(
            "Reload the current .sch file from disk into XSchem, discarding in-memory state. "
            "Use after editing the .sch file directly (via text tools) to have XSchem pick up changes. "
            "Workflow: read_schematic -> edit the file -> reload_schematic."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.read_schematic": ToolSpec(
        name="xschem.read_schematic",
        description=(
            "Read the current .sch file contents as text. "
            "Returns the raw .sch file so you can inspect or edit it. "
            "Format: C lines are components, N lines are wires, B lines are rectangles/graphs. "
            "After editing the file, call reload_schematic to apply changes."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.add_graph": ToolSpec(
        name="xschem.add_graph",
        description=(
            "Add a waveform graph to the schematic that displays simulation results. "
            "Requires a completed simulation (.raw file). "
            "Specify which signals to plot (e.g. 'v(out)', 'i(V1)'). "
            "The graph is embedded in the schematic as a rectangle."
        ),
        input_schema={
            "type": "object",
            "required": ["x1", "y1", "x2", "y2", "signals"],
            "properties": {
                "x1": {"type": "number", "description": "Graph left X coordinate."},
                "y1": {"type": "number", "description": "Graph top Y coordinate."},
                "x2": {"type": "number", "description": "Graph right X coordinate."},
                "y2": {"type": "number", "description": "Graph bottom Y coordinate."},
                "signals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Signal names to plot. E.g. ['v(out)', 'v(in)'] for voltages, ['i(V1)'] for currents.",
                },
                "raw_file": {
                    "type": "string",
                    "default": "",
                    "description": "Path to .raw file. Defaults to last simulation output.",
                },
                "sim_type": {
                    "type": "string",
                    "default": "",
                    "description": "Simulation type filter (e.g. 'tran', 'ac', 'dc'). Leave empty for auto.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.annotate_operating_point": ToolSpec(
        name="xschem.annotate_operating_point",
        description="Back-annotate operating point values from raw file.",
        input_schema={
            "type": "object",
            "properties": {"filename": {"type": "string", "default": ""}},
            "additionalProperties": False,
        },
    ),
    "xschem.get_instance_pins": ToolSpec(
        name="xschem.get_instance_pins",
        description=(
            "Get all pins for an instance with their absolute coordinates, net connections, and directions. "
            "Use this BEFORE wiring to know exact pin positions. "
            "Returns pin name, x, y, connected net, and direction (in/out/inout) for each pin."
        ),
        input_schema={
            "type": "object",
            "required": ["instance_name"],
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Instance name, e.g. 'M1', 'R1', 'V1'. Use xschem.get_context to see available instances.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.check_connectivity": ToolSpec(
        name="xschem.check_connectivity",
        description=(
            "Validate schematic connectivity. Reports unconnected pins (pins with no wire attached "
            "or auto-generated net names), ERC messages, and warnings. "
            "Call this after placing components and wires to verify the circuit before simulation."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.get_netlist_preview": ToolSpec(
        name="xschem.get_netlist_preview",
        description=(
            "Generate and return the SPICE netlist as text so you can verify wiring correctness. "
            "Shows the actual netlist that will be used for simulation, plus any ERC messages. "
            "Use this to catch wiring errors before running a simulation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "max_lines": {
                    "type": "integer",
                    "default": 500,
                    "minimum": 1,
                    "description": "Maximum lines to return. Large netlists are truncated.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.get_pin_coordinates": ToolSpec(
        name="xschem.get_pin_coordinates",
        description=(
            "Get the absolute coordinates for a specific pin on a specific instance. "
            "Returns x, y, the net currently connected to the pin, and pin direction. "
            "Use this to find the exact endpoint for a wire."
        ),
        input_schema={
            "type": "object",
            "required": ["instance_name", "pin_name"],
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Instance name, e.g. 'M1', 'R1'.",
                },
                "pin_name": {
                    "type": "string",
                    "description": "Pin name, e.g. 'G', 'D', 'S', 'p', 'n', 'plus', 'minus'.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.wire_to_pin": ToolSpec(
        name="xschem.wire_to_pin",
        description=(
            "Draw a wire from (x, y) to a named pin on an instance. "
            "Automatically looks up the pin's absolute coordinates -- no need to guess. "
            "For L-shaped routes, call this tool twice with an intermediate point. "
            "PREFERRED over xschem.wire when connecting to a known instance pin."
        ),
        input_schema={
            "type": "object",
            "required": ["instance_name", "pin_name", "x", "y"],
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Target instance name, e.g. 'M1'.",
                },
                "pin_name": {
                    "type": "string",
                    "description": "Target pin name on the instance, e.g. 'G', 'D'.",
                },
                "x": {"type": "number", "description": "Source X coordinate (wire start)."},
                "y": {"type": "number", "description": "Source Y coordinate (wire start)."},
            },
            "additionalProperties": False,
        },
    ),
    "xschem.get_wire_net_assignment": ToolSpec(
        name="xschem.get_wire_net_assignment",
        description=(
            "Show which net each wire in the schematic is assigned to by the netlister. "
            "Lists every wire with its index, coordinates, and resolved net label. "
            "Wires without explicit labels show '(unlabeled)'. "
            "Use this to verify that wires carry the expected net names after placing connections."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "xschem.debug_pin_wire_connection": ToolSpec(
        name="xschem.debug_pin_wire_connection",
        description=(
            "Diagnose why a specific pin on an instance is not connecting to a wire. "
            "Checks all wires for proximity to the pin: reports wires that touch the pin, "
            "wires that are NEAR but don't quite reach (coordinate mismatch), and gives a "
            "human-readable diagnosis with a suggested fix. "
            "Call this when check_connectivity reports unconnected pins to understand the root cause."
        ),
        input_schema={
            "type": "object",
            "required": ["instance_name", "pin_name"],
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Instance name, e.g. 'M1', 'R1'.",
                },
                "pin_name": {
                    "type": "string",
                    "description": "Pin name, e.g. 'G', 'D', 'S', 'p', 'n'.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.force_pin_net": ToolSpec(
        name="xschem.force_pin_net",
        description=(
            "Explicitly assign a net name to a pin by placing a lab_pin.sym label at the pin's coordinates. "
            "This bypasses wire-based net detection: even if no wire reaches the pin, "
            "the netlister will see the label and assign the named net. "
            "Use as a fallback when wiring is too difficult or unreliable, or to override auto-generated net names. "
            "After calling this, regenerate the netlist to see the effect."
        ),
        input_schema={
            "type": "object",
            "required": ["instance_name", "pin_name", "net_name"],
            "properties": {
                "instance_name": {
                    "type": "string",
                    "description": "Instance name, e.g. 'M1', 'R1'.",
                },
                "pin_name": {
                    "type": "string",
                    "description": "Pin name on the instance, e.g. 'G', 'D'.",
                },
                "net_name": {
                    "type": "string",
                    "description": "Net name to assign, e.g. 'VDD', 'GND', 'out', 'gate_drive'.",
                },
            },
            "additionalProperties": False,
        },
    ),
    "xschem.get_netlist_trace": ToolSpec(
        name="xschem.get_netlist_trace",
        description=(
            "Show how the netlister resolved every net in the schematic. "
            "Returns: (1) per-instance pin-to-net mapping with flags for disconnected/auto-named nets, "
            "(2) per-wire net assignment, (3) a snippet of the generated netlist, and (4) ERC messages. "
            "Disconnected pins are flagged with *** DISCONNECTED *** or *** AUTO-NET ***. "
            "Use this for a comprehensive view of netlist resolution before simulation."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
}

