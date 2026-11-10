---
name: export_chat
track: bonus
kind: local_formatter
provider: none (local transcripts)
requires_env: []
inputs: [transcript_id, format, include_tools, max_turns]
outputs: [transcript_id, format, turn_count, total_turns, path, preview, truncated]
side_effect: local_file_write
---
# export_chat

Exports a saved chat session from `transcripts/*.transcript.json` (written by `chat.py`
and the Streamlit UI) into a readable file under `exports/`:

- `format=markdown` → `exports/<transcript_id>.md` (headings per turn, User / Agent).
- `format=text` → `exports/<transcript_id>.txt` (plain text).

Behaviour:

- `transcript_id` empty → exports the most recently updated transcript (the current/latest chat).
  Accepts the full id, the file name, or a unique prefix. Ids are restricted to
  `[A-Za-z0-9_.-]` so the tool can never read outside `transcripts/`.
- `include_tools=true` adds one line per tool call: `name(args) -> ok | error: ...`.
- `max_turns` keeps only the most recent N turns (capped at 200).
- Returns the output `path` plus a `preview` (first 3000 chars); errors return
  `{"tool": "export_chat_history", "error": ..., "message": ...}` instead of raising.

Only writes inside `exports/` (gitignored). Read-only on transcripts. No network, no API key.
