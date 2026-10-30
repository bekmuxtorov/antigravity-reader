"""Unit tests for server endpoints and handler logic."""

import unittest
from antigravity_reader.config import Config
from antigravity_reader.parser import export_turns_to_markdown


class TestServerLogic(unittest.TestCase):
    def test_health_config_association(self):
        cfg = Config.load(port=5055, host="127.0.0.1")
        self.assertEqual(cfg.port, 5055)
        self.assertEqual(cfg.host, "127.0.0.1")

    def test_empty_turns_export(self):
        res = export_turns_to_markdown("empty-session", [])
        self.assertIn("empty-session", res)
        self.assertIn("**Jami burilishlar (turns)**: 0", res)


if __name__ == "__main__":
    unittest.main()
