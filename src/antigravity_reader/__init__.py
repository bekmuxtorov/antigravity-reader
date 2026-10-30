"""
Antigravity Reader.

A standalone, zero-dependency, real-time reader platform for Google Antigravity AI
conversations, agent traces, and artifact reports.
"""

__title__ = "antigravity-reader"
__version__ = "1.0.0"
__author__ = "Asadbek Muxtorov"
__license__ = "MIT"

from .config import Config
from .parser import (
    parse_transcript_file,
    get_conversation_turns,
    list_conversations,
)
from .server import AntigravityReaderHandler, run_server

__all__ = [
    "__version__",
    "Config",
    "parse_transcript_file",
    "get_conversation_turns",
    "list_conversations",
    "AntigravityReaderHandler",
    "run_server",
]
