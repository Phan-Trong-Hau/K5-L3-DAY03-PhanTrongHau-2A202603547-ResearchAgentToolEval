"""Telegram chat mirroring controlled by the user's UI toggle."""
import os

from chat import execute_tool_call
from providers.base import ToolCall
from tools.send.tool import send_telegram


def execute_ui_tool(call: ToolCall) -> dict:
    if call.name == "send":
        return {
            "tool": call.name, "args": call.args,
            "result": {"tool": "send_telegram", "status": "needs_confirmation",
                       "message": "Telegram delivery is controlled by the user's sync toggle in the UI. Do not call send again. Answer the user normally."},
        }
    return execute_tool_call(call)


def message_chunks(text: str, limit: int = 4000) -> list[str]:
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split = text.rfind("\n", 0, limit + 1)
        if split < limit // 2:
            split = limit
        chunks.append(text[:split])
        text = text[split:]
    return chunks


def sync_chat_turn(session: dict, turn: dict, enabled: bool) -> dict:
    """Mirror a new turn once; never resend automatically after an uncertain failure."""
    if "telegram_sync" in turn:
        return turn["telegram_sync"]
    record = {"status": "skipped", "deliveries": []}
    turn["telegram_sync"] = record
    if not enabled:
        return record
    record.update(status="sending", chat_id=os.getenv("TELEGRAM_CHAT_ID", ""))
    tools = ", ".join(event["tool"] for event in turn.get("tool_events", [])) or "Không dùng tool"
    answer = turn.get("assistant_text") or turn.get("error") or "Chưa có câu trả lời."
    text = (
        f"Research Desk · {session['transcript_id']}\n"
        f"{session['provider']} · {session['model']} · Lượt {turn['turn_index']}\n"
        f"{turn.get('ended_at', '')} · {turn.get('duration_seconds', 0):.1f}s\n\n"
        f"Bạn:\n{turn['user']}\n\nAgent:\n{answer}\n\nCông cụ: {tools}"
    )
    chunks = message_chunks(text)
    record["total_parts"] = len(chunks)
    for part, chunk in enumerate(chunks, 1):
        try:
            delivery = send_telegram(text=chunk, confirmed=True)
        except Exception:
            delivery = {"error": "delivery_error", "message": "Không đồng bộ được tin nhắn Telegram."}
        record["deliveries"].append({**delivery, "part": part, "confirmed_by": "ui_sync_toggle"})
        if delivery.get("status") != "sent":
            record["status"] = "partial" if part > 1 else "error"
            record["message"] = delivery.get("message", "Không đồng bộ được tin nhắn Telegram.")
            break
    else:
        record["status"] = "sent"
    return record
