"""Unit tests for configuration loader."""

import os
import unittest
from antigravity_reader.config import Config


class TestConfig(unittest.TestCase):
    def test_default_config(self):
        cfg = Config.load()
        self.assertEqual(cfg.host, "0.0.0.0")
        self.assertEqual(cfg.port, 5050)
        self.assertTrue(cfg.brain_dir.endswith(".gemini/antigravity-ide/brain"))
        self.assertFalse(cfg.open_browser)

    def test_custom_arguments_override(self):
        cfg = Config.load(host="127.0.0.1", port=9090, brain_dir="/tmp/test_brain", open_browser=True)
        self.assertEqual(cfg.host, "127.0.0.1")
        self.assertEqual(cfg.port, 9090)
        self.assertEqual(cfg.brain_dir, "/tmp/test_brain")
        self.assertTrue(cfg.open_browser)

    def test_env_var_override(self):
        os.environ["ANTIGRAVITY_PORT"] = "8081"
        os.environ["ANTIGRAVITY_HOST"] = "192.168.1.10"
        try:
            cfg = Config.load()
            self.assertEqual(cfg.port, 8081)
            self.assertEqual(cfg.host, "192.168.1.10")
        finally:
            del os.environ["ANTIGRAVITY_PORT"]
            del os.environ["ANTIGRAVITY_HOST"]


if __name__ == "__main__":
    unittest.main()
