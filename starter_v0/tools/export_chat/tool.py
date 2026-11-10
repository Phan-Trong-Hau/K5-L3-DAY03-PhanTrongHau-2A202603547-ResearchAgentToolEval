from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err

# Module-level so tests can point them at a temp dir (monkeypatch).
TRANSCRIPTS_DIR = ROOT / "transcripts"
EXPORTS_DIR = ROOT / "exports"

ALLOWED_FORMATS = {"markdown", "text"}
SUFFIX = ".transcript.json"
PREVIEW_CHARS = 3000
MAX_TURNS_CAP = 200
_SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def _list_transcripts() -> list[Path]:
    if not TRANSCRIPTS_DIR.is_dir():
        return []
    return [p for p in TRANSCRIPTS_DIR.glob(f"*{SUFFIX}") if p.is_file()]


def _find_transcript(transcript_id: str) -> Path:
    paths = _list_transcripts()
    if not paths:
        raise FileNotFoundError(f"no transcripts found in {TRANSCRIPTS_DIR.name}/")
    if not transcript_id:
        # Most recently written session = the current/latest chat.
        return max(paths, key=lambda p: p.stat().st_mtime)
    wanted = transcript_id[: -len(SUFFIX)] if transcript_id.endswith(SUFFIX) else transcript_id
    if not _SAFE_ID.match(wanted) or ".." in wanted:
        raise ValueError(f"invalid transcript_id: {transcript_id!r}")
    exact = TRANSCRIPTS_DIR / f"{wanted}{SUFFIX}"
    if exact.is_file():
        return exact
    matches = sorted(p for p in paths if p.name.startswith(wanted))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f"transcript_id {transcript_id!r} is ambiguous ({len(matches)} matches)")
    raise FileNotFoundError(f"transcript not found: {transcript_id!r}")


def _tool_lines(turn: dict[str, Any]) -> list[str]:
    lines = []
    for event in turn.get("tool_events") or []:
        name = event.get("tool") or event.get("name") or "?"
        args = json.dumps(event.get("args") or {}, ensure_ascii=False)
        result = event.get("result") or {}
        status = f"error: {result.get('error')}" if isinstance(result, dict) and result.get("error") else "ok"
        lines.append(f"{name}({args}) -> {status}")
    return lines


def _render(data: dict[str, Any], turns: list[dict[str, Any]], fmt: str, include_tools: bool) -> str:
    tid = data.get("transcript_id", "")
    meta = [
        ("Version", data.get("version") or data.get("artifact_version")),
        ("Provider", data.get("provider")),
        ("Model", data.get("model")),
        ("Created", data.get("created_at")),
        ("Updated", data.get("updated_at")),
    ]
    out: list[str] = []
    if fmt == "markdown":
        out.append(f"# Lịch sử chat — {tid}\n")
        out += [f"- **{k}:** {v}" for k, v in meta if v]
        for turn in turns:
            out.append(f"\n## Lượt {turn.get('turn_index', '?')}" + (f" — {turn['started_at']}" if turn.get("started_at") else ""))
            out.append(f"\n**User:** {turn.get('user', '')}")
            if include_tools:
                tools = _tool_lines(turn)
                if tools:
                    out.append("\n**Tools:**")
                    out += [f"- `{line}`" for line in tools]
            out.append(f"\n**Agent:** {turn.get('assistant_text') or ''}")
    else:
        out.append(f"Lich su chat - {tid}")
        out += [f"{k}: {v}" for k, v in meta if v]
        for turn in turns:
            out.append(f"\n--- Luot {turn.get('turn_index', '?')} ---")
            out.append(f"User: {turn.get('user', '')}")
            if include_tools:
                out += [f"Tool: {line}" for line in _tool_lines(turn)]
            out.append(f"Agent: {turn.get('assistant_text') or ''}")
    return "\n".join(out).strip() + "\n"


def export_chat_history(
    transcript_id: str = "",
    format: str = "markdown",
    include_tools: bool = False,
    max_turns: int = 50,
) -> dict[str, Any]:
    """Export a saved chat transcript (transcripts/*.transcript.json) to exports/<id>.md|.txt."""
    try:
        if not isinstance(transcript_id, str):
            raise ValueError("transcript_id must be a string")
        if format not in ALLOWED_FORMATS:
            raise ValueError(f"format must be one of {sorted(ALLOWED_FORMATS)}, got {format!r}")
        max_turns_int = int(max_turns)
        if max_turns_int <= 0:
            raise ValueError("max_turns must be a positive integer")
        max_turns_int = min(max_turns_int, MAX_TURNS_CAP)
        include = include_tools if isinstance(include_tools, bool) else str(include_tools).lower() == "true"

        path = _find_transcript(transcript_id.strip())
        data = json.loads(path.read_text(encoding="utf-8"))
        all_turns = data.get("turns") or []
        if not all_turns:
            raise ValueError(f"transcript {path.name} has no turns")
        turns = all_turns[-max_turns_int:]  # keep the most recent turns

        tid = data.get("transcript_id") or path.name[: -len(SUFFIX)]
        content = _render({**data, "transcript_id": tid}, turns, format, include)
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = EXPORTS_DIR / f"{tid}.{'md' if format == 'markdown' else 'txt'}"
        out_path.write_text(content, encoding="utf-8")

        return {
            "tool": "export_chat_history",
            "transcript_id": tid,
            "format": format,
            "turn_count": len(turns),
            "total_turns": len(all_turns),
            "path": out_path.relative_to(ROOT).as_posix() if out_path.is_relative_to(ROOT) else str(out_path),
            "preview": content[:PREVIEW_CHARS],
            "truncated": len(content) > PREVIEW_CHARS,
        }
    except Exception as exc:
        return err("export_chat_history", exc)
