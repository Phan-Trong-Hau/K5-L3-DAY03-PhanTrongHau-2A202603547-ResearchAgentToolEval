"""UI action boundary: model output creates a draft, only a UI click sends it."""
from chat import execute_tool_call
from providers.base import ToolCall


def execute_ui_tool(call: ToolCall) -> dict:
    if call.name == "send":
        return {
            "tool": call.name, "args": call.args,
            "result": {"tool": "send_telegram", "status": "needs_confirmation",
                       "message": "Draft ready. The user must review and confirm in the Telegram dialog. Do not call send again."},
        }
    return execute_tool_call(call)
