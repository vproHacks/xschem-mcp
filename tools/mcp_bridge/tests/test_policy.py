import unittest

from tools.mcp_bridge.policy import enforce_allowed_tool, validate_arguments


class PolicyTests(unittest.TestCase):
    def test_allowlisted_tool_passes(self) -> None:
        enforce_allowed_tool("xschem.get_context")

    def test_unknown_tool_fails(self) -> None:
        with self.assertRaises(PermissionError):
            enforce_allowed_tool("xschem.unknown")

    def test_path_traversal_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_arguments("xschem.generate_netlist", {"filename": "../bad.spice"})

    def test_absolute_symbol_path_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_arguments(
                "xschem.insert_symbol",
                {"symbol_name": "/tmp/nmos.sym", "x": 0, "y": 0},
            )


if __name__ == "__main__":
    unittest.main()

