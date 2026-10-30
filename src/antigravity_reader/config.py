"""
Configuration management for Antigravity Reader.
Supports environment variables, CLI options, and sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration container."""

    host: str = "0.0.0.0"
    port: int = 5050
    brain_dir: str = ""
    public_dir: str = ""
    open_browser: bool = False

    @classmethod
    def load(
        cls,
        host: str = None,
        port: int = None,
        brain_dir: str = None,
        public_dir: str = None,
        open_browser: bool = False,
    ) -> "Config":
        """
        Load configuration resolving priority:
        1. Explicit function arguments
        2. Environment variables (ANTIGRAVITY_PORT, ANTIGRAVITY_HOST, etc.)
        3. Built-in defaults
        """
        env_host = os.getenv("ANTIGRAVITY_HOST", os.getenv("HOST", "0.0.0.0"))
        env_port_str = os.getenv("ANTIGRAVITY_PORT", os.getenv("PORT", "5050"))
        try:
            env_port = int(env_port_str)
        except ValueError:
            env_port = 5050

        env_brain = os.getenv(
            "ANTIGRAVITY_BRAIN_DIR",
            os.path.expanduser("~/.gemini/antigravity-ide/brain"),
        )

        resolved_host = host if host is not None else env_host
        resolved_port = port if port is not None else env_port
        resolved_brain = brain_dir if brain_dir is not None else env_brain

        # Locate public directory
        if public_dir:
            resolved_public = str(Path(public_dir).resolve())
        else:
            # Try 1: alongside package root (standard layout)
            candidate_roots = [
                Path(__file__).resolve().parent.parent.parent / "public",
                Path(__file__).resolve().parent / "public",
                Path.cwd() / "public",
            ]
            resolved_public = ""
            for candidate in candidate_roots:
                if candidate.exists() and candidate.is_dir():
                    resolved_public = str(candidate.resolve())
                    break

            if not resolved_public:
                resolved_public = str((Path.cwd() / "public").resolve())

        return cls(
            host=resolved_host,
            port=resolved_port,
            brain_dir=str(Path(resolved_brain).expanduser().resolve()),
            public_dir=resolved_public,
            open_browser=open_browser,
        )
