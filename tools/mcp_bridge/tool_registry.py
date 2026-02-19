from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .policy import TOOL_POLICY, enforce_allowed_tool, enforce_confirmation, validate_arguments
from .process_manager import XSchemProcessManager
from .schemas import TOOL_SPECS
from .xschem_client import XSchemClient


LOG = logging.getLogger(__name__)


@dataclass
class RegistryConfig:
    require_confirmation_for_destructive_tools: bool = True


class ToolRegistry:
    def __init__(self, xschem: XSchemClient, config: RegistryConfig | None = None):
        self.xschem = xschem
        self.config = config or RegistryConfig()
        self.processes = XSchemProcessManager(host=xschem.config.host)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
            }
            for spec in TOOL_SPECS.values()
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        enforce_allowed_tool(name)
        validate_arguments(name, arguments)
        enforce_confirmation(name, arguments, self.config.require_confirmation_for_destructive_tools)

        policy = TOOL_POLICY[name]
        if not policy.wrapper:
            return self._call_local_tool(name, arguments)
        wrapper_args = self._map_args(name, arguments)
        response = self.xschem.run_wrapper(policy.wrapper, *wrapper_args)
        is_error = response.get("status") != "ok"
        LOG.info(
            "tool call complete",
            extra={
                "extra": {
                    "tool": name,
                    "is_error": is_error,
                    "status": response.get("status", ""),
                    "code": response.get("code", ""),
                }
            },
        )
        return {"content": [{"type": "text", "text": str(response)}], "isError": is_error}

    def _call_local_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "xschem.start_process":
            response = self.processes.start_process(
                tcp_port=arguments["tcp_port"],
                command=arguments.get("command", "xschem"),
                extra_args=arguments.get("extra_args", []),
                cwd=arguments.get("cwd", ""),
                display=arguments.get("display", ""),
                startup_timeout_seconds=float(arguments.get("startup_timeout_seconds", 8.0)),
            )
            # Keep XSchem RPC port aligned with the spawned process.
            self.xschem.config.port = int(arguments["tcp_port"])
            return {"content": [{"type": "text", "text": str(response)}], "isError": False}
        if name == "xschem.stop_process":
            response = self.processes.stop_process(
                tcp_port=arguments["tcp_port"],
                force=bool(arguments.get("force", False)),
            )
            is_error = response.get("status") == "not_managed"
            return {"content": [{"type": "text", "text": str(response)}], "isError": is_error}
        if name == "xschem.process_status":
            response = self.processes.process_status(tcp_port=arguments.get("tcp_port"))
            return {"content": [{"type": "text", "text": str(response)}], "isError": False}
        raise RuntimeError(f"No local tool handler configured for: {name}")

    @staticmethod
    def _map_args(name: str, args: dict[str, Any]) -> list[Any]:
        if name == "xschem.get_context":
            return []
        if name == "xschem.search_symbols":
            return [args.get("pattern", "*")]
        if name == "xschem.list_symbols":
            return [1 if args.get("include_derived", False) else 0]
        if name == "xschem.wire":
            return [args["x1"], args["y1"], args["x2"], args["y2"]]
        if name == "xschem.insert_symbol":
            return [
                args["symbol_name"],
                args["x"],
                args["y"],
                args.get("rot", 0),
                args.get("flip", 0),
                args.get("inst_props", ""),
                1 if args.get("batch_continues", False) else 0,
            ]
        if name == "xschem.create_symbol":
            return [
                args["name"],
                args.get("in", []),
                args.get("out", []),
                args.get("inout", []),
                1 if args.get("overwrite", False) else 0,
            ]
        if name == "xschem.set_instance_property":
            return [
                args["instance"],
                args["token"],
                args["value"],
                1 if args.get("fast", False) else 0,
            ]
        if name == "xschem.generate_netlist":
            return [args.get("filename", "")]
        if name == "xschem.run_simulation":
            return []
        if name == "xschem.read_simulation_results":
            return [args.get("raw_file", ""), args.get("sim_type", "")]
        if name == "xschem.save_schematic":
            return [args.get("filename", ""), args.get("type", "schematic")]
        if name == "xschem.delete":
            target = args["target"]
            if target == "instance":
                return [target, args.get("name", "")]
            if target == "wire":
                return [target, args.get("index", 0)]
            if target == "area":
                return [target, args["x1"], args["y1"], args["x2"], args["y2"]]
            return [target]
        if name == "xschem.reload_schematic":
            return []
        if name == "xschem.read_schematic":
            return []
        if name == "xschem.add_graph":
            return [
                args["x1"], args["y1"], args["x2"], args["y2"],
                args["signals"],
                args.get("raw_file", ""),
                args.get("sim_type", ""),
            ]
        if name == "xschem.annotate_operating_point":
            return [args.get("filename", "")]
        if name == "xschem.get_instance_pins":
            return [args["instance_name"]]
        if name == "xschem.check_connectivity":
            return []
        if name == "xschem.get_netlist_preview":
            return [args.get("max_lines", 500)]
        if name == "xschem.get_pin_coordinates":
            return [args["instance_name"], args["pin_name"]]
        if name == "xschem.wire_to_pin":
            return [args["instance_name"], args["pin_name"], args["x"], args["y"]]
        if name == "xschem.get_wire_net_assignment":
            return []
        if name == "xschem.debug_pin_wire_connection":
            return [args["instance_name"], args["pin_name"]]
        if name == "xschem.force_pin_net":
            return [args["instance_name"], args["pin_name"], args["net_name"]]
        if name == "xschem.get_netlist_trace":
            return []
        raise ValueError(f"Unknown tool mapping: {name}")

