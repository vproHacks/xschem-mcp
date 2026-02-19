import unittest

from tools.mcp_bridge.tool_registry import RegistryConfig, ToolRegistry


class FakeXSchemClient:
    def __init__(self) -> None:
        self.calls = []

    def run_wrapper(self, wrapper_name, *args, timeout_seconds=None):
        self.calls.append((wrapper_name, args))
        return {"status": "ok", "code": "ok", "message": "", "data": {"wrapper": wrapper_name}}


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.xschem = FakeXSchemClient()
        self.registry = ToolRegistry(
            xschem=self.xschem,
            config=RegistryConfig(require_confirmation_for_destructive_tools=True),
        )

    def test_list_tools_non_empty(self) -> None:
        tools = self.registry.list_tools()
        self.assertGreater(len(tools), 0)

    def test_get_context_calls_expected_wrapper(self) -> None:
        self.registry.call_tool("xschem.get_context", {})
        self.assertEqual(self.xschem.calls[0][0], "mcp_get_context")

    def test_destructive_tool_requires_confirm(self) -> None:
        with self.assertRaises(PermissionError):
            self.registry.call_tool(
                "xschem.insert_symbol",
                {"symbol_name": "nmos.sym", "x": 0, "y": 0},
            )

    def test_destructive_tool_with_confirm(self) -> None:
        result = self.registry.call_tool(
            "xschem.insert_symbol",
            {"symbol_name": "nmos.sym", "x": 0, "y": 0, "confirm": True},
        )
        self.assertFalse(result["isError"])


if __name__ == "__main__":
    unittest.main()

