"""
HTTP and SSE Server implementation for Antigravity Reader.
Zero external dependencies, built on Python's ThreadingHTTPServer.
"""

import json
import mimetypes
import os
import sys
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .config import Config
from .parser import (
    export_turns_to_markdown,
    get_conversation_turns,
    list_conversations,
)


class AntigravityReaderHandler(SimpleHTTPRequestHandler):
    """Custom request handler serving static frontend assets and REST/SSE endpoints."""

    # Set by run_server
    config: Config = None

    def __init__(self, *args, **kwargs):
        directory = self.config.public_dir if self.config else None
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        """Clean timestamped log format."""
        try:
            sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {fmt % args}\n")
            sys.stderr.flush()
        except Exception:
            pass

    def end_headers(self):
        """Append CORS and basic security headers."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/conversations":
            self.handle_conversations()
        elif path == "/api/conversation":
            conv_id = query.get("id", [None])[0]
            self.handle_single_conversation(conv_id)
        elif path == "/api/stream":
            conv_id = query.get("id", [None])[0]
            self.handle_sse_stream(conv_id)
        elif path == "/api/export":
            conv_id = query.get("id", [None])[0]
            self.handle_export(conv_id)
        elif path in ("/api/health", "/healthz"):
            self.handle_health()
        else:
            # Fallback root to index.html
            if path == "/":
                self.path = "/index.html"
            super().do_GET()

    def handle_health(self):
        """Health check endpoint for Docker and monitoring."""
        payload = json.dumps({
            "status": "healthy",
            "uptime_epoch": int(time.time()),
            "brain_dir": self.config.brain_dir,
            "brain_exists": os.path.exists(self.config.brain_dir),
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_conversations(self):
        """Return list of all found conversation sessions."""
        convs = list_conversations(self.config.brain_dir)
        payload = json.dumps(convs, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_single_conversation(self, conv_id: str):
        """Return turns for a specific conversation."""
        convs = list_conversations(self.config.brain_dir)
        if not conv_id and convs:
            conv_id = convs[0]["id"]

        if not conv_id:
            self.send_error(404, "Suhbat topilmadi")
            return

        turns, _ = get_conversation_turns(conv_id, self.config.brain_dir)
        meta = next(
            (c for c in convs if c["id"] == conv_id),
            {"id": conv_id, "title": "Suhbat"},
        )

        response_data = {
            "conversation": meta,
            "turns": turns,
        }
        payload = json.dumps(response_data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_export(self, conv_id: str):
        """Export conversation history as a downloadable Markdown document."""
        if not conv_id:
            convs = list_conversations(self.config.brain_dir)
            conv_id = convs[0]["id"] if convs else None

        if not conv_id:
            self.send_error(404, "Suhbat topilmadi")
            return

        turns, _ = get_conversation_turns(conv_id, self.config.brain_dir)
        markdown_text = export_turns_to_markdown(conv_id, turns)
        full_md = markdown_text.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="antigravity-{conv_id[:8]}.md"',
        )
        self.send_header("Content-Length", str(len(full_md)))
        self.end_headers()
        self.wfile.write(full_md)

    def handle_sse_stream(self, conv_id: str):
        """Real-time Server-Sent Events (SSE) feed watching transcript file changes."""
        convs = list_conversations(self.config.brain_dir)
        if not conv_id and convs:
            conv_id = convs[0]["id"]

        if not conv_id:
            self.send_error(404, "Suhbat topilmadi")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        turns, target_path = get_conversation_turns(conv_id, self.config.brain_dir)
        meta = next(
            (c for c in convs if c["id"] == conv_id),
            {"id": conv_id, "title": "Suhbat"},
        )

        initial_payload = json.dumps(
            {"type": "init", "conversation": meta, "turns": turns},
            ensure_ascii=False,
        )
        self.wfile.write(f"data: {initial_payload}\n\n".encode("utf-8"))
        self.wfile.flush()

        last_mtime = (
            os.path.getmtime(target_path)
            if target_path and os.path.exists(target_path)
            else 0
        )
        last_turn_count = len(turns)

        counter = 0
        try:
            while True:
                time.sleep(0.5)
                counter += 1

                if target_path and os.path.exists(target_path):
                    try:
                        current_mtime = os.path.getmtime(target_path)
                    except OSError:
                        current_mtime = last_mtime

                    if current_mtime != last_mtime:
                        last_mtime = current_mtime
                        updated_turns, _ = get_conversation_turns(
                            conv_id, self.config.brain_dir
                        )
                        if len(updated_turns) != last_turn_count or updated_turns != turns:
                            last_turn_count = len(updated_turns)
                            turns = updated_turns
                            upd_payload = json.dumps(
                                {
                                    "type": "update",
                                    "conversation": meta,
                                    "turns": updated_turns,
                                },
                                ensure_ascii=False,
                            )
                            self.wfile.write(f"data: {upd_payload}\n\n".encode("utf-8"))
                            self.wfile.flush()

                # Keep-alive heartbeat ping
                if counter % 20 == 0:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            pass


def run_server(config: Config):
    """Configure and start the threaded HTTP server."""
    mimetypes.init()
    mimetypes.add_type("text/javascript", ".js")
    mimetypes.add_type("text/css", ".css")

    AntigravityReaderHandler.config = config

    server_address = (config.host, config.port)
    ThreadingHTTPServer.allow_reuse_address = True

    try:
        httpd = ThreadingHTTPServer(server_address, AntigravityReaderHandler)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print("=" * 60)
            print(f"❌ Xatolik: {config.port}-port allaqachon band!")
            print("💡 Server orqa fonda ishlab turgan bo'lishi mumkin.")
            print(f"   Uni to'xtatish uchun:  fuser -k {config.port}/tcp")
            print("   Yoki boshqa port tanlang:  --port 5051")
            print("=" * 60)
            sys.exit(1)
        raise

    url = f"http://{'localhost' if config.host in ('0.0.0.0', '') else config.host}:{config.port}"

    print("=" * 64)
    print("  ✨ ANTIGRAVITY READER — AI Natijalarini O'qish Platformasi")
    print(f"  🌐 Veb sahifa:   {url}")
    print(f"  🧠 Antigravity:  {config.brain_dir}")
    print(f"  📁 Public dir:   {config.public_dir}")
    print(f"  ⚡ To'xtatish:   Ctrl + C")
    print("=" * 64)

    if config.open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer to'xtatildi.")
        httpd.server_close()
