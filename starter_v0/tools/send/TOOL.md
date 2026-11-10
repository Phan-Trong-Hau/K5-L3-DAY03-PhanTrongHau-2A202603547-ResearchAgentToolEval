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

In the Streamlit UI, the user controls a Telegram sync toggle (off by default).
When enabled, each new completed chat turn mirrors the user message, agent answer,
model, duration and tool names. Enabling the toggle authorizes this delivery until disabled.
Long messages are split into chunks. Existing history is not replayed, and failed/partial
deliveries are recorded without automatic retries. Model calls to `send` never bypass the toggle.
