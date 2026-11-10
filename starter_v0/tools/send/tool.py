from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _safe_error(exc: Exception) -> dict[str, Any]:
    result = err("send_telegram", exc)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if token:
        result["message"] = result["message"].replace(token, "[REDACTED]")
    return result


def _credentials() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
    return token, chat_id


def _result(response: requests.Response) -> dict[str, Any]:
    response.raise_for_status()
    data = response.json()
    if data.get("ok") is not True:
        raise RuntimeError(data.get("description") or "Telegram rejected the request")
    return data.get("result", {})


def check_telegram_connection() -> dict[str, Any]:
    """Read-only check; never posts a test message."""
    try:
        token, chat_id = _credentials()
        base = f"https://api.telegram.org/bot{token}"
        bot = _result(requests.get(f"{base}/getMe", timeout=TIMEOUT))
        chat = _result(requests.get(f"{base}/getChat", params={"chat_id": chat_id}, timeout=TIMEOUT))
        return {"status": "connected", "bot_username": bot.get("username"),
                "chat_id": chat.get("id", chat_id),
                "chat_title": chat.get("title") or chat.get("first_name") or chat_id}
    except Exception as exc:
        return _safe_error(exc)


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if confirmed is not True:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Message must be a non-empty string")
        if len(text) > 4096:
            raise ValueError("Message exceeds Telegram's 4096 character limit")
        token, chat_id = _credentials()
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=TIMEOUT,
        )
        message = _result(response)
        return {"tool": "send_telegram", "status": "sent",
                "message_id": message.get("message_id"), "chat_id": chat_id}
    except Exception as exc:
        return _safe_error(exc)

