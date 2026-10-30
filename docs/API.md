# API Reference

### 1. `GET /api/conversations`
Returns a list of all detected Antigravity conversation sessions sorted newest first.

**Response (200 OK)**:
```json
[
  {
    "id": "b9217d27-8252-42f8-9577-0fca5fbca902",
    "title": "Docker Compose Port Konfliktlarini Hal Qilish",
    "turns_count": 8,
    "updated_at": "2026-10-30 11:00:00",
    "mtime": 1793339000.0
  }
]
```

---

### 2. `GET /api/conversation?id=<CONV_ID>`
Returns detailed turn history for the specified conversation.

**Response (200 OK)**:
```json
{
  "conversation": { "id": "...", "title": "..." },
  "turns": [
    {
      "id": 1,
      "prompt": "Savol matni",
      "user_time": "2026-10-30 10:45:00",
      "response_time": "2026-10-30 10:45:05",
      "response": "Model javob matni..."
    }
  ]
}
```

---

### 3. `GET /api/stream?id=<CONV_ID>`
Server-Sent Events (SSE) live feed.

**Events**:
- `init`: Emitted immediately upon connection with current history.
- `update`: Emitted when log file is updated on disk.
- `: ping`: Heartbeat every 10 seconds to maintain connection.

---

### 4. `GET /api/export?id=<CONV_ID>`
Downloads full conversation session as a formatted Markdown (`.md`) report.

---

### 5. `GET /healthz` (or `/api/health`)
Returns service health and status.
