from __future__ import annotations

import json
import logging
import pathlib
import socket
import threading
import time
from dataclasses import dataclass
from typing import Any


LOG = logging.getLogger(__name__)

_MCP_PROCS_TCL = pathlib.Path(__file__).with_name("mcp_procs.tcl")


@dataclass
class XSchemClientConfig:
    host: str = "127.0.0.1"
    port: int = 2021
    timeout_seconds: float = 8.0
    retries: int = 2
    retry_backoff_seconds: float = 0.4


class XSchemClient:
    """Small TCP client for XSchem Tcl command socket."""

    def __init__(self, config: XSchemClientConfig):
        self.config = config
        self._lock = threading.Lock()
        self._procs_loaded = False

    def _send_once(self, command: str, timeout_seconds: float | None = None) -> str:
        timeout = timeout_seconds or self.config.timeout_seconds
        LOG.debug("sending tcl command", extra={"extra": {"command": command, "port": self.config.port}})
        with socket.create_connection((self.config.host, self.config.port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            if not command.endswith("\n"):
                command += "\n"
            sock.sendall(command.encode("utf-8"))
            try:
                sock.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)
        return b"".join(chunks).decode("utf-8", errors="replace")

    def run_tcl(self, command: str, timeout_seconds: float | None = None) -> str:
        with self._lock:
            attempt = 0
            while True:
                attempt += 1
                try:
                    return self._send_once(command, timeout_seconds=timeout_seconds)
                except (TimeoutError, OSError, socket.error) as exc:
                    if attempt > self.config.retries + 1:
                        raise RuntimeError(f"Failed Tcl command after {attempt} attempts: {exc}") from exc
                    delay = self.config.retry_backoff_seconds * attempt
                    LOG.warning(
                        "xschem command failed; retrying",
                        extra={"extra": {"attempt": attempt, "delay_s": delay, "error": str(exc)}},
                    )
                    time.sleep(delay)

    def negotiate_port(self) -> int:
        """Ask XSchem default port to migrate this session to a free port."""
        response = self.run_tcl("setup_tcp_xschem 0")
        try:
            new_port = int(response.strip())
        except ValueError as exc:
            raise RuntimeError(f"Invalid port negotiation response: {response!r}") from exc
        self.config.port = new_port
        LOG.info("negotiated xschem port", extra={"extra": {"port": new_port}})
        return new_port

    @classmethod
    def _tcl_quote(cls, arg: Any) -> str:
        if isinstance(arg, (list, tuple)):
            inner = " ".join(cls._tcl_quote(item) for item in arg)
            return "{" + inner + "}"
        raw = str(arg)
        if raw == "":
            return "{}"
        safe = raw.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        return "{" + safe + "}"

    def _ensure_procs(self) -> None:
        if self._procs_loaded:
            return
        tcl_path = str(_MCP_PROCS_TCL.resolve())
        LOG.info("sourcing mcp procs", extra={"extra": {"path": tcl_path}})
        self.run_tcl(f"source {{{tcl_path}}}")
        self._procs_loaded = True

    def run_wrapper(self, wrapper_name: str, *args: Any, timeout_seconds: float | None = None) -> dict[str, Any]:
        self._ensure_procs()
        parts = [wrapper_name]
        parts.extend(self._tcl_quote(a) for a in args)
        response = self.run_tcl(" ".join(parts), timeout_seconds=timeout_seconds).strip()
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Wrapper did not return JSON: {response!r}") from exc
        return parsed

