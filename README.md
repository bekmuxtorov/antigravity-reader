<div align="center">

# 🚀 Antigravity Reader

**A premium, zero-dependency, real-time reader platform for Google Antigravity AI outputs.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Stdlib)-orange.svg?style=flat-square)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

[O'zbekcha](#-tavsif-ozbek-tilida) • [Features](#-features) • [Quick Start](#-quick-start) • [CLI Options](#-cli-options) • [Project Structure](#-project-structure) • [Architecture](#-architecture) • [License](#-license)

</div>

---

## 📖 Overview

**Antigravity Reader** is an open-source, lightweight web application built to comfortably read, search, and export Google Antigravity AI conversation transcripts, planner responses, and code outputs.

It directly interfaces with the local Antigravity brain logs (`~/.gemini/antigravity-ide/brain`), parsing `transcript_full.jsonl` files and streaming live conversation turns into a distraction-free, beautifully formatted reading UI using **Server-Sent Events (SSE)**.

---

## ✨ Features

- **⚡ Zero External Runtime Dependencies**: Built entirely on Python's standard library (`http.server`, `json`, `re`, `time`). No `pip install` required to run!
- **🔄 Real-Time Live Sync**: Watches conversation files on disk and instantly pushes new AI responses to the browser via SSE without page refreshes.
- **📚 Premium Reading Aesthetics**:
  - **Warm Book Mode** (Warm sepia palette crafted for long reading sessions).
  - **Sleek Dark Mode** (High-contrast OLED palette).
  - **Clean Light Mode** (Classic high-clarity view).
- **🔠 Typography Controls**: Dynamic font size scaling (A- / A+) and full-width layout toggling.
- **🔍 Instant Search & Navigation**: Quick-jump chips to directly jump to any conversation turn and live prompt filtering.
- **💻 Offline Syntax Highlighting**: Pre-bundled local Highlight.js & Marked.js for fast, offline-ready rendering.
- **📥 One-Click Markdown Export**: Download complete conversation histories as structured `.md` files.

---

## 🇺🇿 Tavsif (O'zbek tilida)

**Antigravity Reader** — Google Antigravity AI tomonidan yaratilgan barcha javoblar, kodlar va tahlillarni qulay, estetik va real vaqtda kuzatib o'qish uchun yaratilgan maxsus platforma.

- **Nol bog'liqlik (Zero dependency)**: Tashqi kutubxonalarsiz, sof Python 3 standart kutubxonasida ishlaydi.
- **Jonli yangilanish (Live SSE)**: Antigravity yangi javob yozayotgan paytda sahifa avtomatik yangilanadi.
- **Kitob rejimi**: Ko'zni charchatmaydigan maxsus "Book" rejimi, qorong'u va yorug' mavzular.
- **Markdown eksport**: Barcha suhbatni bir tugma bilan `.md` fayl qilib yuklab olish.

---

## 🚀 Quick Start

### Method 1: Instant Bash Launcher (Recommended)

Run the included automated launch script (auto-cleans busy ports and opens the reader):

```bash
./start.sh
```

Now open **http://localhost:5050** in your web browser.

---

### Method 2: Direct Python Execution

You can run the application directly with Python 3:

```bash
python3 server.py
```

Or pass custom flags:

```bash
python3 server.py --port 8080 --open
```

---

### Method 3: Installable CLI Tool

You can install `antigravity-reader` as a global command on your machine:

```bash
# Editable developer install
pip install -e .

# Run from anywhere in terminal
antigravity-reader --port 5050
```

---

## ⚙️ CLI Options & Configuration

```text
usage: antigravity-reader [-h] [-p PORT] [-H HOST] [-b BRAIN_DIR]
                          [--public-dir PUBLIC_DIR] [--open] [-v]

options:
  -h, --help            Show this help message and exit
  -p, --port PORT       Port to bind server on (default: 5050, or ANTIGRAVITY_PORT env)
  -H, --host HOST       Host address to bind on (default: 0.0.0.0, or ANTIGRAVITY_HOST env)
  -b, --brain-dir DIR   Path to Antigravity brain directory (default: ~/.gemini/antigravity-ide/brain)
  --public-dir DIR      Custom path to static assets directory (public/)
  --open                Automatically open web browser upon server launch
  -v, --version         Show program version and exit
```

### Environment Variables

You can configure settings via environment variables or a `.env` file (see [`.env.example`](.env.example)):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ANTIGRAVITY_PORT` | HTTP server binding port | `5050` |
| `ANTIGRAVITY_HOST` | HTTP server binding interface | `0.0.0.0` |
| `ANTIGRAVITY_BRAIN_DIR` | Absolute path to conversation logs | `~/.gemini/antigravity-ide/brain` |

---

## 🏛️ Project Structure

```text
antigravity-reader/
├── .github/                  # CI/CD and contribution workflows
│   ├── workflows/ci.yml      # Multi-version Python test runner
│   ├── ISSUE_TEMPLATE/       # GitHub issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                     # Detailed architectural guides
│   ├── ARCHITECTURE.md       # High-level component diagram & dataflow
│   └── API.md                # Full REST and SSE endpoint documentation
├── public/                   # Frontend assets (Offline-ready)
│   ├── vendor/               # Bundled Highlight.js and Marked.js
│   ├── app.js                # SSE client logic & state management
│   ├── index.html            # Semantic, modern reading layout
│   └── style.css             # Glassmorphic, multi-theme CSS system
├── scripts/
│   └── start.sh              # Portable startup script
├── src/
│   └── antigravity_reader/   # Modular Python package
│       ├── __init__.py       # Package metadata and public exports
│       ├── cli.py            # CLI argument parsing
│       ├── config.py         # Config resolver (Args -> Env -> Defaults)
│       ├── parser.py         # JSONL transcript stream parser
│       └── server.py         # Threading HTTP server & SSE handler
├── tests/                    # Unit test suite
│   ├── test_config.py        # Configuration loading tests
│   ├── test_parser.py        # JSONL parser & turn pairing tests
│   └── test_server.py        # Handler & export tests
├── .env.example              # Sample environment configuration
├── .gitignore                # Production Python/IDE gitignore
├── CHANGELOG.md              # Version release history
├── CONTRIBUTING.md           # Guidelines for contributors
├── LICENSE                   # MIT License
├── Makefile                  # Developer task automation
├── pyproject.toml            # PEP 517/621 package specification
├── README.md                 # Primary project documentation
├── requirements.txt          # Zero runtime dependencies notice
├── requirements-dev.txt      # Development & testing tools
├── server.py                 # Top-level direct execution entrypoint
└── start.sh                  # Root executable launcher
```

---

## 🧪 Testing

To run the full unit test suite:

```bash
make test
# or
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).  
Copyright (c) 2026 **Asadbek Muxtorov**.
