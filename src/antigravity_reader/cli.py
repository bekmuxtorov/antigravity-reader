"""
Command-line interface for Antigravity Reader.
"""

import argparse
import sys

from . import __version__
from .config import Config
from .server import run_server


def build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="antigravity-reader",
        description="Antigravity Reader — Standalone Web App for reading Google Antigravity AI outputs.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=None,
        help="Port to bind server on (default: 5050, or ANTIGRAVITY_PORT env)",
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default=None,
        help="Host address to bind on (default: 0.0.0.0, or ANTIGRAVITY_HOST env)",
    )
    parser.add_argument(
        "-b",
        "--brain-dir",
        type=str,
        default=None,
        help="Path to Antigravity brain directory (default: ~/.gemini/antigravity-ide/brain)",
    )
    parser.add_argument(
        "--public-dir",
        type=str,
        default=None,
        help="Custom path to static assets directory (public/)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        default=False,
        help="Automatically open web browser upon server launch",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )
    return parser


def main(argv=None):
    """Entry point for CLI command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    config = Config.load(
        host=args.host,
        port=args.port,
        brain_dir=args.brain_dir,
        public_dir=args.public_dir,
        open_browser=args.open,
    )

    run_server(config)


if __name__ == "__main__":
    main()
