from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any


@dataclass(frozen=True)
class ToolPolicy:
    wrapper: str | None
    destructive: bool = False


TOOL_POLICY: dict[str, ToolPolicy] = {
    "xschem.start_process": ToolPolicy(None, destructive=False),
    "xschem.stop_process": ToolPolicy(None, destructive=True),
    "xschem.process_status": ToolPolicy(None, destructive=False),
    "xschem.get_context": ToolPolicy("mcp_get_context", destructive=False),
    "xschem.search_symbols": ToolPolicy("mcp_search_symbols", destructive=False),
    "xschem.list_symbols": ToolPolicy("mcp_list_symbols", destructive=False),
    "xschem.wire": ToolPolicy("mcp_wire", destructive=True),
    "xschem.insert_symbol": ToolPolicy("mcp_place_symbol", destructive=True),
    "xschem.create_symbol": ToolPolicy("mcp_create_symbol", destructive=True),
    "xschem.set_instance_property": ToolPolicy("mcp_set_instance_property", destructive=True),
    "xschem.generate_netlist": ToolPolicy("mcp_generate_netlist", destructive=False),
    "xschem.run_simulation": ToolPolicy("mcp_run_simulation", destructive=False),
    "xschem.read_simulation_results": ToolPolicy("mcp_read_simulation_results", destructive=False),
    "xschem.save_schematic": ToolPolicy("mcp_save_schematic", destructive=True),
    "xschem.delete": ToolPolicy("mcp_delete", destructive=True),
    "xschem.reload_schematic": ToolPolicy("mcp_reload_schematic", destructive=True),
    "xschem.read_schematic": ToolPolicy("mcp_read_schematic", destructive=False),
    "xschem.add_graph": ToolPolicy("mcp_add_graph", destructive=True),
    "xschem.annotate_operating_point": ToolPolicy("mcp_annotate_operating_point", destructive=False),
    "xschem.get_instance_pins": ToolPolicy("mcp_get_instance_pins", destructive=False),
    "xschem.check_connectivity": ToolPolicy("mcp_check_connectivity", destructive=False),
    "xschem.get_netlist_preview": ToolPolicy("mcp_get_netlist_preview", destructive=False),
    "xschem.get_pin_coordinates": ToolPolicy("mcp_get_pin_coordinates", destructive=False),
    "xschem.wire_to_pin": ToolPolicy("mcp_wire_to_pin", destructive=True),
    "xschem.get_wire_net_assignment": ToolPolicy("mcp_get_wire_net_assignment", destructive=False),
    "xschem.debug_pin_wire_connection": ToolPolicy("mcp_debug_pin_wire_connection", destructive=False),
    "xschem.force_pin_net": ToolPolicy("mcp_force_pin_net", destructive=True),
    "xschem.get_netlist_trace": ToolPolicy("mcp_get_netlist_trace", destructive=False),
}


def enforce_allowed_tool(tool_name: str) -> None:
    if tool_name not in TOOL_POLICY:
        raise PermissionError(f"Tool not allowlisted: {tool_name}")


def enforce_confirmation(tool_name: str, args: dict[str, Any], confirmations_enabled: bool) -> None:
    policy = TOOL_POLICY[tool_name]
    if not confirmations_enabled or not policy.destructive:
        return
    confirmed = bool(args.get("confirm"))
    if not confirmed:
        raise PermissionError(f"Tool requires explicit confirmation: {tool_name}")


def _validate_safe_path(path_value: str) -> None:
    if "\x00" in path_value:
        raise ValueError("path contains NUL byte")
    norm = os.path.normpath(path_value)
    if norm.startswith("../") or norm == "..":
        raise ValueError("path traversal is not allowed")


def validate_arguments(tool_name: str, args: dict[str, Any]) -> None:
    # Defensive checks independent of JSON schema validation.
    for key, value in args.items():
        if isinstance(value, str):
            if len(value) > 20000:
                raise ValueError(f"argument too long: {key}")
            if key in {"filename", "raw_file", "name"}:
                _validate_safe_path(value)
        if isinstance(value, list):
            if len(value) > 1000:
                raise ValueError(f"list argument too long: {key}")
            for item in value:
                if not isinstance(item, str):
                    raise ValueError(f"list argument must contain strings: {key}")

    if tool_name == "xschem.insert_symbol":
        symbol_name = str(args.get("symbol_name", ""))
        if "/" in symbol_name and symbol_name.startswith("/"):
            # Force relative/known library-resolved symbol naming.
            raise ValueError("absolute symbol paths are not allowed")

    if tool_name in {"xschem.start_process", "xschem.stop_process", "xschem.process_status"}:
        tcp_port = args.get("tcp_port")
        if tcp_port is not None:
            if not isinstance(tcp_port, int):
                raise ValueError("tcp_port must be an integer")
            if tcp_port < 1 or tcp_port > 65535:
                raise ValueError("tcp_port must be between 1 and 65535")

    if tool_name == "xschem.start_process":
        timeout = args.get("startup_timeout_seconds")
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise ValueError("startup_timeout_seconds must be > 0")
        display = args.get("display")
        if display is not None and not isinstance(display, str):
            raise ValueError("display must be a string")

