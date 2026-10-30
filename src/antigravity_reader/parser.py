"""
Log parsing engine for Antigravity AI transcripts.
Parses JSON Lines (transcript.jsonl and transcript_full.jsonl) into structured turns.
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple


USER_REQUEST_REGEX = re.compile(r"<USER_REQUEST>(.*?)</USER_REQUEST>", re.DOTALL)


def parse_timestamp(created_str: str) -> str:
    """Format ISO-8601 timestamp into user-friendly local date-time string."""
    if not created_str:
        return ""
    try:
        clean_ts = created_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return created_str[:19].replace("T", " ")


def parse_transcript_file(file_path: str) -> List[Dict]:
    """
    Parses a single transcript JSONL file and pairs USER_INPUT with PLANNER_RESPONSE.
    Returns list of structured turns.
    """
    if not file_path or not os.path.exists(file_path):
        return []

    turns: List[Dict] = []
    current_user: Optional[Dict] = None

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except Exception:
                    continue

                item_type = item.get("type")
                source = item.get("source")
                content = item.get("content", "")
                created = item.get("created_at", "")
                readable_time = parse_timestamp(created)

                if item_type == "USER_INPUT" and source == "USER_EXPLICIT":
                    m = USER_REQUEST_REGEX.search(content)
                    prompt_text = m.group(1).strip() if m else content.strip()
                    current_user = {
                        "prompt": prompt_text,
                        "timestamp": readable_time,
                        "raw_created": created,
                    }

                elif item_type == "PLANNER_RESPONSE" and source == "MODEL" and content:
                    turn_id = len(turns) + 1
                    turns.append({
                        "id": turn_id,
                        "prompt": current_user["prompt"] if current_user else "Boshlang'ich so'rov",
                        "user_time": current_user.get("timestamp") if current_user else readable_time,
                        "response_time": readable_time,
                        "response": content,
                    })
    except Exception as e:
        sys.stderr.write(f"[WARN] Error reading transcript '{file_path}': {e}\n")

    return turns


def get_conversation_turns(conv_id: str, brain_dir: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Locates the transcript file for the given conversation ID within brain_dir.
    Prefers transcript_full.jsonl over transcript.jsonl.
    """
    if not conv_id or not brain_dir:
        return [], None

    conv_dir = os.path.join(brain_dir, conv_id, ".system_generated", "logs")
    full_log = os.path.join(conv_dir, "transcript_full.jsonl")
    std_log = os.path.join(conv_dir, "transcript.jsonl")

    target = full_log if os.path.exists(full_log) else (std_log if os.path.exists(std_log) else None)
    if not target:
        return [], None

    return parse_transcript_file(target), target


def list_conversations(brain_dir: str) -> List[Dict]:
    """
    Scans the Antigravity brain directory and lists all conversation sessions,
    sorted by newest modification date first.
    """
    if not brain_dir or not os.path.exists(brain_dir):
        return []

    convs: List[Dict] = []
    try:
        entries = os.scandir(brain_dir)
    except Exception as e:
        sys.stderr.write(f"[WARN] Cannot scan brain dir '{brain_dir}': {e}\n")
        return []

    for entry in entries:
        if not entry.is_dir() or entry.name.startswith("."):
            continue

        conv_id = entry.name
        log_dir = os.path.join(entry.path, ".system_generated", "logs")
        full_log = os.path.join(log_dir, "transcript_full.jsonl")
        std_log = os.path.join(log_dir, "transcript.jsonl")

        log_path = full_log if os.path.exists(full_log) else (std_log if os.path.exists(std_log) else None)
        if not log_path:
            continue

        try:
            mtime = os.path.getmtime(log_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            mtime = 0
            mtime_str = "Noma'lum sana"

        title = "Nomsiz suhbat"
        count = 0
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                        if item.get("type") == "USER_INPUT" and title == "Nomsiz suhbat":
                            c = item.get("content", "")
                            m = USER_REQUEST_REGEX.search(c)
                            if m:
                                title = m.group(1).strip().replace("\n", " ")[:80]
                            elif c:
                                title = c.strip().replace("\n", " ")[:80]
                        if item.get("type") == "PLANNER_RESPONSE" and item.get("content"):
                            count += 1
                    except Exception:
                        continue
        except Exception:
            pass

        convs.append({
            "id": conv_id,
            "title": title,
            "turns_count": count,
            "updated_at": mtime_str,
            "mtime": mtime,
        })

    convs.sort(key=lambda x: x["mtime"], reverse=True)
    return convs


def export_turns_to_markdown(conv_id: str, turns: List[Dict]) -> str:
    """Format conversation turns into a clean, readable Markdown export."""
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    md_lines = [
        "# Antigravity Suhbat Hisoboti\n\n",
        f"- **Suhbat ID**: `{conv_id}`\n",
        f"- **Eksport vaqti**: {now_str}\n",
        f"- **Jami burilishlar (turns)**: {len(turns)}\n\n",
        "---\n\n",
    ]

    for turn in turns:
        md_lines.append(f"## 👤 Savol #{turn['id']} ({turn.get('user_time', '')})\n\n")
        md_lines.append(f"> {turn.get('prompt', '')}\n\n")
        md_lines.append(f"## 🤖 Antigravity Javobi ({turn.get('response_time', '')})\n\n")
        md_lines.append(f"{turn.get('response', '')}\n\n---\n\n")

    return "".join(md_lines)
