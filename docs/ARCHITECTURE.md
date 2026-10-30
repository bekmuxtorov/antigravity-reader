# Antigravity Reader — Architecture & Design

## Overview

Antigravity Reader is designed as an ultra-lightweight, zero-dependency local reading environment for AI conversation logs produced by Google Antigravity IDE.

```
+-----------------------------------------------------------+
|                      Browser UI                           |
|  - Vanilla HTML5 / Modern CSS                             |
|  - SSE EventSource live sync listener                     |
|  - Client-side Marked.js & Highlight.js rendering         |
+-----------------------------^-----------------------------+
                              | HTTP / SSE (:5050)
+-----------------------------v-----------------------------+
|                 AntigravityReaderHandler                  |
|  - Static File Server (/public)                           |
|  - REST Endpoints (/api/conversations, /api/conversation) |
|  - Server-Sent Events Engine (/api/stream)                |
|  - Markdown Exporter (/api/export)                        |
+-----------------------------^-----------------------------+
                              |
+-----------------------------v-----------------------------+
|                     Parser Engine                         |
|  - Watches ~/.gemini/antigravity-ide/brain/               |
|  - Parses transcript_full.jsonl & transcript.jsonl        |
|  - Pairs USER_INPUT and PLANNER_RESPONSE turns            |
+-----------------------------------------------------------+
```

## Key Principles

1. **Zero External Dependencies**:
   The backend relies solely on the Python 3.8+ Standard Library (`http.server`, `json`, `re`, `time`, `urllib`). No `pip install` is required to run the server.

2. **Real-time File Invalidation**:
   Instead of periodic heavy re-parsing, the SSE stream monitors `os.path.getmtime` of the target conversation log file. If modified, it parses new delta lines and pushes an update event directly to the browser DOM.

3. **Local & Privacy First**:
   All logs stay on the user's local machine. No telemetry or external cloud calls are executed.
