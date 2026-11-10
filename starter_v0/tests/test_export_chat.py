"""Unit tests for the export_chat tool (offline, uses tmp dirs only)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools import TOOL_FUNCTIONS
from tools.export_chat import tool as export_module

export_chat = TOOL_FUNCTIONS["export_chat"]


def _write_transcript(directory: Path, tid: str, turns: list[dict], mtime: float | None = None) -> Path:
    path = directory / f"{tid}.transcript.json"
    data = {
        "transcript_id": tid,
        "version": "v1",
        "provider": "openrouter",
        "model": "openai/gpt-4o-mini",
        "created_at": "2026-11-10T12:00:00",
        "updated_at": "2026-11-10T12:05:00",
        "turns": turns,
    }
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def _turn(i: int, user: str, answer: str, tool_events: list | None = None) -> dict:
    return {"turn_index": i, "started_at": f"2026-11-10T12:0{i}:00", "user": user,
            "assistant_text": answer, "tool_events": tool_events or []}


@pytest.fixture()
def dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    transcripts, exports = tmp_path / "transcripts", tmp_path / "exports"
    transcripts.mkdir()
    monkeypatch.setattr(export_module, "TRANSCRIPTS_DIR", transcripts)
    monkeypatch.setattr(export_module, "EXPORTS_DIR", exports)
    return transcripts, exports


def test_export_latest_transcript_to_markdown_file(dirs: tuple[Path, Path]) -> None:
    transcripts, exports = dirs
    _write_transcript(transcripts, "old_session", [_turn(1, "cũ", "cũ")], mtime=1_000)
    _write_transcript(transcripts, "new_session", [_turn(1, "Tin AI hôm nay?", "Đây là 3 tin AI.")], mtime=2_000)

    result = export_chat()

    assert "error" not in result
    assert result["transcript_id"] == "new_session"
    assert result["turn_count"] == 1
    out = exports / "new_session.md"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Lịch sử chat — new_session")
    assert "**User:** Tin AI hôm nay?" in text
    assert "**Agent:** Đây là 3 tin AI." in text
    assert "**Model:** openai/gpt-4o-mini" in text
    assert result["preview"] == text


def test_export_by_id_as_text_with_tool_calls(dirs: tuple[Path, Path]) -> None:
    transcripts, exports = dirs
    events = [
        {"tool": "lookup", "args": {"query": "AI", "topic": "news"}, "result": {"items": []}},
        {"tool": "fetch", "args": {"url": "https://x.com"}, "result": {"error": "HTTPError"}},
    ]
    _write_transcript(transcripts, "abc_123", [_turn(1, "hỏi", "đáp", events)])

    result = export_chat(transcript_id="abc_123", format="text", include_tools=True)

    assert result["path"].endswith("abc_123.txt")
    text = (exports / "abc_123.txt").read_text(encoding="utf-8")
    assert 'Tool: lookup({"query": "AI", "topic": "news"}) -> ok' in text
    assert "Tool: fetch" in text and "-> error: HTTPError" in text
    assert "User: hỏi" in text and "Agent: đáp" in text


def test_tool_calls_hidden_by_default(dirs: tuple[Path, Path]) -> None:
    transcripts, _ = dirs
    events = [{"tool": "lookup", "args": {"query": "AI"}, "result": {}}]
    _write_transcript(transcripts, "s1", [_turn(1, "hỏi", "đáp", events)])

    result = export_chat(transcript_id="s1")

    assert "lookup" not in result["preview"]


def test_max_turns_keeps_most_recent_turns(dirs: tuple[Path, Path]) -> None:
    transcripts, _ = dirs
    _write_transcript(transcripts, "long", [_turn(i, f"câu {i}", f"trả lời {i}") for i in range(1, 6)])

    result = export_chat(transcript_id="long", max_turns="2")  # model may send a numeric string

    assert result["turn_count"] == 2
    assert result["total_turns"] == 5
    assert "câu 1" not in result["preview"]
    assert "câu 4" in result["preview"] and "câu 5" in result["preview"]


def test_unique_prefix_and_filename_are_accepted(dirs: tuple[Path, Path]) -> None:
    transcripts, _ = dirs
    _write_transcript(transcripts, "ui_v1_openrouter_20261110_aaaa", [_turn(1, "a", "b")])

    assert export_chat(transcript_id="ui_v1_openrouter")["transcript_id"] == "ui_v1_openrouter_20261110_aaaa"
    assert "error" not in export_chat(transcript_id="ui_v1_openrouter_20261110_aaaa.transcript.json")


@pytest.mark.parametrize("bad_id", ["../.env", "..\\secrets", "a/b", "x;rm"])
def test_path_traversal_ids_are_rejected(dirs: tuple[Path, Path], bad_id: str) -> None:
    transcripts, exports = dirs
    _write_transcript(transcripts, "s1", [_turn(1, "a", "b")])

    result = export_chat(transcript_id=bad_id)

    assert result["error"] == "ValueError"
    assert not exports.exists()


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"format": "pdf"}, "ValueError"),
        ({"max_turns": 0}, "ValueError"),
        ({"max_turns": "abc"}, "ValueError"),
        ({"transcript_id": "missing"}, "FileNotFoundError"),
    ],
)
def test_bad_model_args_return_error_dict(dirs: tuple[Path, Path], kwargs: dict, error: str) -> None:
    transcripts, exports = dirs
    _write_transcript(transcripts, "s1", [_turn(1, "a", "b")])

    result = export_chat(**kwargs)

    assert result["tool"] == "export_chat_history"
    assert result["error"] == error
    assert not exports.exists()


def test_no_transcripts_and_empty_turns_return_error(dirs: tuple[Path, Path]) -> None:
    transcripts, _ = dirs
    assert export_chat()["error"] == "FileNotFoundError"

    _write_transcript(transcripts, "empty", [])
    result = export_chat(transcript_id="empty")
    assert result["error"] == "ValueError"
    assert "no turns" in result["message"]


def test_ambiguous_prefix_returns_error(dirs: tuple[Path, Path]) -> None:
    transcripts, _ = dirs
    _write_transcript(transcripts, "ui_a_1", [_turn(1, "a", "b")])
    _write_transcript(transcripts, "ui_a_2", [_turn(1, "a", "b")])

    result = export_chat(transcript_id="ui_a")

    assert result["error"] == "ValueError"
    assert "ambiguous" in result["message"]
