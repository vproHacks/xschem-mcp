#!/usr/bin/env python3
"""Path-stable launcher for XSchem MCP bridge.

Use this file as the MCP server command target so Gemini can launch
the bridge regardless of current working directory.
"""

from __future__ import annotations

import pathlib
import sys


def _bootstrap_path() -> None:
    # Ensure repo root is importable even when launched outside the project.
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


def main() -> None:
    _bootstrap_path()
    from tools.mcp_bridge.main import main as bridge_main

    bridge_main()


if __name__ == "__main__":
    main()

