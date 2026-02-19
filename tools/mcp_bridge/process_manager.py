from __future__ import annotations

import logging
import os
import socket
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Any


LOG = logging.getLogger(__name__)


@dataclass
class ManagedProcess:
    tcp_port: int
    command: list[str]
    popen: subprocess.Popen[Any]
    started_at: float = field(default_factory=time.time)


class XSchemProcessManager:
    """Manage local XSchem processes started by the MCP bridge."""

    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self._lock = threading.Lock()
        self._managed_by_port: dict[int, ManagedProcess] = {}

    def _is_port_open(self, tcp_port: int, timeout_seconds: float = 0.3) -> bool:
        try:
            with socket.create_connection((self.host, tcp_port), timeout=timeout_seconds):
                return True
        except OSError:
            return False

    def _wait_for_port(self, tcp_port: int, timeout_seconds: float, process: subprocess.Popen[Any]) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if process.poll() is not None:
                return False
            if self._is_port_open(tcp_port):
                return True
            time.sleep(0.15)
        return self._is_port_open(tcp_port)

    def _prune_dead(self) -> None:
        dead_ports: list[int] = []
        for port, managed in self._managed_by_port.items():
            if managed.popen.poll() is not None:
                dead_ports.append(port)
        for port in dead_ports:
            self._managed_by_port.pop(port, None)

    def start_process(
        self,
        tcp_port: int,
        command: str = "xschem",
        extra_args: list[str] | None = None,
        cwd: str = "",
        display: str = "",
        startup_timeout_seconds: float = 8.0,
    ) -> dict[str, Any]:
        extra_args = extra_args or []
        cmd = [command, "--tcp_port", str(tcp_port), *extra_args]
        effective_display = display or os.environ.get("DISPLAY", "")

        with self._lock:
            self._prune_dead()

            if self._is_port_open(tcp_port):
                managed = self._managed_by_port.get(tcp_port)
                return {
                    "status": "already_running",
                    "managed_by_bridge": managed is not None,
                    "tcp_port": tcp_port,
                    "pid": managed.popen.pid if managed else None,
                    "command": managed.command if managed else cmd,
                    "display": effective_display,
                }

            env = os.environ.copy()
            if effective_display:
                env["DISPLAY"] = effective_display

            popen = subprocess.Popen(  # noqa: S603
                cmd,
                cwd=cwd or None,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )

            if not self._wait_for_port(tcp_port, startup_timeout_seconds, popen):
                try:
                    popen.terminate()
                    popen.wait(timeout=1.5)
                except Exception:  # pylint: disable=broad-except
                    try:
                        popen.kill()
                    except Exception:  # pylint: disable=broad-except
                        pass
                raise RuntimeError(
                    f"xschem process failed to become ready on tcp_port={tcp_port} "
                    f"(command={cmd!r}, startup_timeout_seconds={startup_timeout_seconds})"
                )

            managed = ManagedProcess(tcp_port=tcp_port, command=cmd, popen=popen)
            self._managed_by_port[tcp_port] = managed
            LOG.info(
                "started xschem process",
                extra={"extra": {"tcp_port": tcp_port, "pid": popen.pid, "command": cmd}},
            )
            return {
                "status": "started",
                "managed_by_bridge": True,
                "tcp_port": tcp_port,
                "pid": popen.pid,
                "command": cmd,
                "display": effective_display,
            }

    def stop_process(self, tcp_port: int, force: bool = False) -> dict[str, Any]:
        with self._lock:
            self._prune_dead()
            managed = self._managed_by_port.get(tcp_port)
            if managed is None:
                return {
                    "status": "not_managed",
                    "managed_by_bridge": False,
                    "tcp_port": tcp_port,
                    "port_open": self._is_port_open(tcp_port),
                }

            proc = managed.popen
            if proc.poll() is not None:
                self._managed_by_port.pop(tcp_port, None)
                return {
                    "status": "already_stopped",
                    "managed_by_bridge": True,
                    "tcp_port": tcp_port,
                    "pid": proc.pid,
                }

            if force:
                proc.kill()
            else:
                proc.terminate()
            try:
                proc.wait(timeout=2.5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.5)

            self._managed_by_port.pop(tcp_port, None)
            LOG.info(
                "stopped xschem process",
                extra={"extra": {"tcp_port": tcp_port, "pid": proc.pid, "force": force}},
            )
            return {
                "status": "stopped",
                "managed_by_bridge": True,
                "tcp_port": tcp_port,
                "pid": proc.pid,
                "force": force,
            }

    def process_status(self, tcp_port: int | None = None) -> dict[str, Any]:
        with self._lock:
            self._prune_dead()
            if tcp_port is not None:
                managed = self._managed_by_port.get(tcp_port)
                return {
                    "tcp_port": tcp_port,
                    "port_open": self._is_port_open(tcp_port),
                    "managed_by_bridge": managed is not None,
                    "pid": managed.popen.pid if managed else None,
                    "running": (managed.popen.poll() is None) if managed else False,
                    "command": managed.command if managed else [],
                }

            processes = [
                {
                    "tcp_port": managed.tcp_port,
                    "pid": managed.popen.pid,
                    "running": managed.popen.poll() is None,
                    "command": managed.command,
                    "uptime_seconds": max(0.0, time.time() - managed.started_at),
                }
                for managed in self._managed_by_port.values()
            ]
            return {"managed_processes": processes, "count": len(processes)}
