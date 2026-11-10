import requests
import pytest

from conftest import FakeResponse
from providers.base import ToolCall
from telegram_delivery import execute_ui_tool, message_chunks, sync_chat_turn
from tools.send.tool import check_telegram_connection, send_telegram


@pytest.fixture
def telegram_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:test-secret-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")


@pytest.mark.parametrize("confirmed", [False, "true", "false", 1, None])
def test_send_requires_boolean_confirmation(confirmed, fake_http):
    calls = fake_http(FakeResponse())
    assert send_telegram("Draft", confirmed=confirmed)["status"] == "needs_confirmation"
    assert calls == []


def test_confirmed_send_posts_exact_plain_text_and_returns_message_id(telegram_env, fake_http):
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 42}}))
    text = "AI **digest** [source](https://example.com) _unfinished"
    result = send_telegram(text, confirmed=True)
    assert result == {"tool": "send_telegram", "status": "sent", "message_id": 42, "chat_id": "@test_channel"}
    assert calls[0]["json"] == {"chat_id": "@test_channel", "text": text}
    assert calls[0]["method"] == "POST"


@pytest.mark.parametrize("text", ["", "   ", None, [], "a" * 4097])
def test_invalid_text_never_calls_network(text, telegram_env, fake_http):
    calls = fake_http(FakeResponse())
    assert send_telegram(text, confirmed=True)["error"] == "ValueError"
    assert calls == []


def test_missing_credentials_returns_error_without_network(fake_http):
    calls = fake_http(FakeResponse())
    assert send_telegram("Draft", confirmed=True)["error"] == "RuntimeError"
    assert calls == []


def test_api_rejection_does_not_report_sent(telegram_env, fake_http):
    fake_http(FakeResponse({"ok": False, "description": "chat not found"}))
    result = send_telegram("Draft", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert result["message"] == "chat not found"


def test_network_errors_redact_bot_token(telegram_env, fake_http):
    fake_http(requests.HTTPError("401 for https://api.telegram.org/bot123:test-secret-token/sendMessage"))
    result = send_telegram("Draft", confirmed=True)
    assert result["error"] == "HTTPError"
    assert "123:test-secret-token" not in result["message"]
    assert "[REDACTED]" in result["message"]


def test_connection_check_only_reads_bot_and_chat(telegram_env, monkeypatch):
    calls = []
    def get(url, **kwargs):
        calls.append((url, kwargs))
        data = {"username": "research_bot"} if url.endswith("/getMe") else {"id": -100123, "title": "Research"}
        return FakeResponse({"ok": True, "result": data})
    monkeypatch.setattr(requests, "get", get)
    result = check_telegram_connection()
    assert result["status"] == "connected"
    assert result["chat_title"] == "Research"
    assert [url.rsplit("/", 1)[-1] for url, _ in calls] == ["getMe", "getChat"]
    assert calls[1][1]["params"] == {"chat_id": "@test_channel"}


def test_model_cannot_bypass_ui_confirmation_even_with_confirmed_true(fake_http):
    calls = fake_http(FakeResponse())
    event = execute_ui_tool(ToolCall("send", {"text": "Draft", "confirmed": True}))
    assert event["result"]["status"] == "needs_confirmation"
    assert calls == []


def test_other_ui_tools_still_execute():
    event = execute_ui_tool(ToolCall("clarify", {"question": "Which source?"}))
    assert event["result"]["awaiting_user"] is True


@pytest.fixture
def chat_turn():
    return (
        {"transcript_id": "demo", "provider": "ollama", "model": "qwen2.5:7b"},
        {"turn_index": 1, "user": "Tin AI hôm nay?", "assistant_text": "Bản tin AI và nguồn: https://example.com",
         "duration_seconds": 2.5, "tool_events": [{"tool": "lookup"}]},
    )


def test_sync_off_never_sends(chat_turn, fake_http):
    calls = fake_http(FakeResponse())
    result = sync_chat_turn(*chat_turn, enabled=False)
    assert result["status"] == "skipped"
    assert calls == []


def test_sync_includes_both_sides_and_metadata_once(chat_turn, telegram_env, fake_http):
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 9}}))
    result = sync_chat_turn(*chat_turn, enabled=True)
    assert result["status"] == "sent"
    text = calls[0]["json"]["text"]
    for value in [chat_turn[1]["user"], chat_turn[1]["assistant_text"], "qwen2.5:7b", "lookup", "2.5s"]:
        assert value in text
    assert result["deliveries"][0]["confirmed_by"] == "ui_sync_toggle"
    sync_chat_turn(*chat_turn, enabled=True)
    assert len(calls) == 1


def test_long_sync_splits_without_losing_text(chat_turn, telegram_env, fake_http):
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 9}}))
    chat_turn[1]["assistant_text"] = "Bản tin rất dài\n" * 1000
    result = sync_chat_turn(*chat_turn, enabled=True)
    assert result["status"] == "sent"
    assert len(calls) > 1
    assert all(len(call["json"]["text"]) <= 4000 for call in calls)
    assert chat_turn[1]["assistant_text"] in "".join(call["json"]["text"] for call in calls)


def test_partial_sync_stops_and_does_not_resend_on_rerun(chat_turn, monkeypatch):
    from unittest.mock import Mock
    sender = Mock(side_effect=[{"status": "sent", "message_id": 1}, {"error": "HTTPError", "message": "429"}])
    monkeypatch.setattr("telegram_delivery.send_telegram", sender)
    chat_turn[1]["assistant_text"] = "x" * 10000
    result = sync_chat_turn(*chat_turn, enabled=True)
    assert result["status"] == "partial"
    assert sender.call_count == 2
    sync_chat_turn(*chat_turn, enabled=True)
    assert sender.call_count == 2


def test_chunking_keeps_newlines_and_unicode():
    text = "Nội dung tiếng Việt 🔎\n" * 500
    chunks = message_chunks(text)
    assert "".join(chunks) == text
    assert all(0 < len(chunk) <= 4000 for chunk in chunks)
