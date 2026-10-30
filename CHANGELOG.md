# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-30

### Added
- **Core Engine**: Standalone Python HTTP Server with real-time SSE live-sync.
- **Log Parser**: Automatic parser for Antigravity JSONL transcripts (`transcript.jsonl` & `transcript_full.jsonl`).
- **Modern Web Interface**:
  - Live conversation stream with automatic real-time DOM updates.
  - Three visual themes: Warm Book (Sepia), Sleek Dark (OLED), Crisp Light.
  - Interactive font size scaling and reader width toggle.
  - Full-text search and conversation filtering.
  - Offline syntax highlighting via Highlight.js.
  - One-click Markdown export (`/api/export`).
- **Packaging**: Standardized Python package with CLI command `antigravity-reader`.
- **Developer Tools**: Unit test suite, Makefile, GitHub Actions CI workflow.
