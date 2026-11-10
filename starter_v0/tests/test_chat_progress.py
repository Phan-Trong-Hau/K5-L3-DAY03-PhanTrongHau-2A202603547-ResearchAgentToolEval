from unittest.mock import Mock

import pytest

from chat import run_model_tool_loop
from providers.base import ModelResponse, ToolCall


def run(provider, events):
    return run_model_tool_loop(provider=provider, messages=[], tools=[], model=None,
                               max_tool_rounds=3, on_progress=events.append)


def test_progress_tracks_model_tool_and_final_response(monkeypatch):
    provider = Mock()
    provider.complete.side_effect = [
        ModelResponse(text=None, tool_calls=[ToolCall("lookup", {"query": "AI"})]),
        ModelResponse(text="Answer", tool_calls=[]),
    ]
    monkeypatch.setattr("chat.execute_tool_call", lambda call: {"tool": call.name, "result": {"items": []}})
    events = []
    result = run(provider, events)
    assert result["assistant_text"] == "Answer"
    assert [e["stage"] for e in events] == [
        "model_started", "model_completed", "tool_started", "tool_completed",
        "model_started", "model_completed",
    ]
    assert events[2]["tool"] == "lookup"
    assert events[3]["duration_seconds"] >= 0
    assert [e["elapsed_seconds"] for e in events] == sorted(e["elapsed_seconds"] for e in events)


def test_tool_error_is_reported_in_progress(monkeypatch):
    provider = Mock()
    provider.complete.side_effect = [
        ModelResponse(text=None, tool_calls=[ToolCall("lookup", {})]),
        ModelResponse(text="Failed to retrieve", tool_calls=[]),
    ]
    monkeypatch.setattr("chat.execute_tool_call", lambda call: {"tool": call.name, "result": {"error": "HTTPError"}})
    events = []
    run(provider, events)
    assert next(e for e in events if e["stage"] == "tool_completed")["error"] is True


def test_model_failure_keeps_started_event():
    provider = Mock()
    provider.complete.side_effect = RuntimeError("offline")
    events = []
    with pytest.raises(RuntimeError, match="offline"):
        run(provider, events)
    assert [e["stage"] for e in events] == ["model_started"]
