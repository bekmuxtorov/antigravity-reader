"""Unit tests for transcript parser engine."""

import json
import os
import tempfile
import unittest
from antigravity_reader.parser import (
    export_turns_to_markdown,
    parse_timestamp,
    parse_transcript_file,
)


class TestParser(unittest.TestCase):
    def test_parse_timestamp(self):
        ts = "2026-10-30T06:15:30Z"
        res = parse_timestamp(ts)
        self.assertIn("2026-10-30", res)
        self.assertEqual(parse_timestamp(""), "")

    def test_parse_transcript_file_and_markdown_export(self):
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as f:
            temp_path = f.name
            # Write sample JSONL entries
            f.write(json.dumps({
                "type": "USER_INPUT",
                "source": "USER_EXPLICIT",
                "content": "<USER_REQUEST>\nSalom, bu test so'rovi\n</USER_REQUEST>",
                "created_at": "2026-10-30T06:00:00Z"
            }) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": "Assalomu alaykum! Bu model javobi.",
                "created_at": "2026-10-30T06:00:05Z"
            }) + "\n")

        try:
            turns = parse_transcript_file(temp_path)
            self.assertEqual(len(turns), 1)
            turn = turns[0]
            self.assertEqual(turn["id"], 1)
            self.assertEqual(turn["prompt"], "Salom, bu test so'rovi")
            self.assertIn("Assalomu alaykum", turn["response"])

            md = export_turns_to_markdown("test-session-123", turns)
            self.assertIn("# Antigravity Suhbat Hisoboti", md)
            self.assertIn("test-session-123", md)
            self.assertIn("Salom, bu test so'rovi", md)
            self.assertIn("Assalomu alaykum", md)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
