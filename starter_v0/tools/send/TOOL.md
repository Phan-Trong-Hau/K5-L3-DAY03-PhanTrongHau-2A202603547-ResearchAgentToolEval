---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status, message_id, chat_id]
side_effect: true
requires_confirmation: true
---
# send

Posts text to a Telegram channel. The message is only sent when `confirmed` is true.

Accepts 1–4096 characters as plain text, preserving URLs without Markdown parsing errors.
Returns Telegram message ID after a successful send. Invalid input, missing credentials,
HTTP failures and API rejection return an error dictionary; bot tokens are redacted.

In the Streamlit UI, a model call to `send` creates a draft even if it sets `confirmed=true`.
The user reviews the destination/content and confirms in the Telegram dialog before sending.
The sidebar connection check uses `getMe` and `getChat`; it does not send a message.
