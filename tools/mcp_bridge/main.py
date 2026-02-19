from __future__ import annotations

import argparse
import logging

from .logging_utils import configure_logging
from .mcp_stdio_server import StdioMcpServer
from .tool_registry import RegistryConfig, ToolRegistry
from .xschem_client import XSchemClient, XSchemClientConfig


LOG = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XSchem MCP bridge server")
    parser.add_argument("--xschem-host", default="127.0.0.1")
    parser.add_argument("--xschem-port", type=int, default=2021)
    parser.add_argument("--xschem-timeout", type=float, default=8.0)
    parser.add_argument("--xschem-retries", type=int, default=2)
    parser.add_argument("--negotiate-port", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--audit-log", default="", help="Optional JSONL audit log path.")
    parser.add_argument(
        "--allow-destructive-without-confirm",
        action="store_true",
        help="Disable explicit confirm=true gate for destructive tool calls.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level, audit_log_path=args.audit_log)

    xschem = XSchemClient(
        XSchemClientConfig(
            host=args.xschem_host,
            port=args.xschem_port,
            timeout_seconds=args.xschem_timeout,
            retries=args.xschem_retries,
        )
    )
    if args.negotiate_port:
        try:
            xschem.negotiate_port()
        except Exception as exc:  # pylint: disable=broad-except
            LOG.warning(
                "xschem port negotiation failed; continuing with configured port",
                extra={"extra": {"port": xschem.config.port, "error": str(exc)}},
            )

    registry = ToolRegistry(
        xschem=xschem,
        config=RegistryConfig(
            require_confirmation_for_destructive_tools=not args.allow_destructive_without_confirm,
        ),
    )
    LOG.info("xschem mcp bridge started", extra={"extra": {"port": xschem.config.port}})
    StdioMcpServer(registry).serve_forever()


if __name__ == "__main__":
    main()

