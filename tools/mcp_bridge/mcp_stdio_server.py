from __future__ import annotations

import json
import logging
import sys
from io import BufferedReader, BufferedWriter
from typing import Any

from .tool_registry import ToolRegistry


LOG = logging.getLogger(__name__)


class StdioMcpServer:
    """
    MCP JSON-RPC over stdio server (Content-Length framed).
    Supported methods:
      - initialize
      - tools/list
      - tools/call
      - ping
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self._stdio_mode: str | None = None

    @staticmethod
    def _read_message(stdin: BufferedReader) -> tuple[dict[str, Any] | None, str | None]:
        first_line = stdin.readline()
        if not first_line:
            return None, None
        # Compatibility path: some clients send newline-delimited JSON-RPC.
        stripped = first_line.strip()
        if stripped.startswith(b"{"):
            return json.loads(stripped.decode("utf-8")), "line"

        content_length = None
        line = first_line
        while True:
            if not line:
                raise ValueError("unexpected EOF while reading headers")
            if line in (b"\r\n", b"\n"):
                break
            key, _, value = line.decode("utf-8", errors="replace").partition(":")
            if key.lower().strip() == "content-length":
                content_length = int(value.strip())
            line = stdin.readline()
        if content_length is None:
            raise ValueError("missing Content-Length header (and not JSON line mode)")
        body = stdin.read(content_length)
        if len(body) != content_length:
            raise ValueError("unexpected EOF while reading message body")
        return json.loads(body.decode("utf-8")), "framed"

    def _write_message(self, stdout: BufferedWriter, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        if self._stdio_mode == "line":
            stdout.write(body + b"\n")
        else:
            header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
            stdout.write(header)
            stdout.write(body)
        stdout.flush()

    def serve_forever(self) -> None:
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
        while True:
            try:
                request, mode = self._read_message(stdin)
                if request is None:
                    return
                if self._stdio_mode is None and mode is not None:
                    self._stdio_mode = mode
                    LOG.info("detected stdio mode", extra={"extra": {"mode": self._stdio_mode}})
                LOG.info(
                    "mcp request",
                    extra={"extra": {"method": request.get("method", ""), "id": request.get("id")}},
                )
                response = self._handle_request(request)
                if response is not None:
                    self._write_message(stdout, response)
            except Exception as exc:  # pylint: disable=broad-except
                LOG.exception("fatal read/dispatch error")
                error_payload = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(exc)}}
                self._write_message(stdout, error_payload)

    def _handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        is_notification = req_id is None
        if is_notification and (method in {"notifications/initialized", "$/cancelRequest"} or method.startswith("notifications/")):
            return None
        try:
            if method == "initialize":
                client_protocol = params.get("protocolVersion", "2024-11-05")
                result = {
                    # Mirror the client protocol when provided to maximize compatibility.
                    "protocolVersion": client_protocol,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                    "serverInfo": {"name": "xschem-mcp-bridge", "version": "0.1.0"},
                }
            elif method == "ping":
                result = {}
            elif method == "resources/list":
                result = {"resources": []}
            elif method == "prompts/list":
                result = {"prompts": []}
            elif method == "tools/list":
                result = {"tools": self.registry.list_tools()}
            elif method == "tools/call":
                name = params["name"]
                arguments = params.get("arguments", {})
                result = self.registry.call_tool(name, arguments)
            else:
                raise ValueError(f"Unknown method: {method}")
            if is_notification:
                return None
            payload = {"jsonrpc": "2.0", "id": req_id, "result": result}
            LOG.info("mcp response", extra={"extra": {"method": method, "id": req_id}})
            return payload
        except Exception as exc:  # pylint: disable=broad-except
            LOG.exception("request failed")
            if is_notification:
                return None
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32001, "message": str(exc)}}

