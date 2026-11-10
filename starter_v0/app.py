from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from time import monotonic

import streamlit as st
import requests

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from telegram_delivery import execute_ui_tool, sync_chat_turn
from version_catalog import load_versions
from version_comparison import render_comparison


ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Desk", page_icon="🔎", layout="wide")
st.html("""
<style>
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    margin-left: auto;
    width: fit-content;
    max-width: 85%;
    background-color: #1e3a5f;
    color: #f8fafc;
    border-radius: 1rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stChatMessageContent"] {
    text-align: right;
    min-width: 0;
    overflow-wrap: anywhere;
    color: #f8fafc;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stMarkdownContainer"] {
    color: #f8fafc;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) a {
    color: #bfdbfe;
}
@media (max-width: 640px) {
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        max-width: 95%;
    }
}
</style>
""")


@st.cache_data(ttl=15, show_spinner=False)
def local_model_available(base_url):
    try:
        response = requests.get(f"{base_url.rstrip('/')}/models", timeout=2)
        response.raise_for_status()
        return bool(response.json().get("data"))
    except (requests.RequestException, ValueError, AttributeError):
        return False


def provider_availability():
    available = {
        "ollama": local_model_available(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")),
    }
    for name in ("openrouter", "openai", "anthropic", "gemini"):
        available[name] = bool(os.getenv(f"{name.upper()}_API_KEY", "").strip())
    return available


def redact(value):
    """Keep configured credentials out of UI and exported evidence."""
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        for key, secret in os.environ.items():
            if ("KEY" in key or "TOKEN" in key) and len(secret) > 8:
                value = value.replace(secret, "[REDACTED]")
    return value


def start_session(provider, model, version, rounds, history_window):
    st.session_state.view_only = False
    saved_version = load_versions().get(version)
    if saved_version:
        prompt_path, tools_path = saved_version["prompt_path"], saved_version["tools_path"]
    else:
        prompt_path = ROOT / "artifacts/system_prompt_local.md" if provider == "ollama" else PROMPT
        tools_path = ROOT / "artifacts/tools_local.yaml" if provider == "ollama" else TOOLS
    artifact = build_artifact_version(version, prompt_path, tools_path)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    session_id = f"ui_{safe_slug(version)}_{provider}_{stamp}_{uuid4().hex[:8]}"
    st.session_state.research = {
        "transcript_id": session_id,
        **artifact_version_dict(artifact),
        "provider": provider,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.prompt_snapshot = prompt_path.read_text(encoding="utf-8")
    st.session_state.tools_snapshot = to_openai_tools(load_tool_declarations(tools_path))
    st.session_state.research["prompt_snapshot"] = st.session_state.prompt_snapshot
    st.session_state.research["tools_snapshot"] = st.session_state.tools_snapshot


def saved_sessions(search):
    sessions = []
    for path in (ROOT / "transcripts").glob("*.transcript.json"):
        if "setup-smoke" in path.name:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            turns = data.get("turns", [])
            if not turns:
                continue
            title = turns[0].get("user", "Hội thoại")
            haystack = " ".join(str(t.get("user", "")) + " " + str(t.get("assistant_text", "")) for t in turns)
            if search.casefold() not in haystack.casefold():
                continue
            label = f"{data.get('updated_at', '')} · {title[:65]} · {data.get('version', '')} · {data.get('model', '')}"
            sessions.append((path, label, data))
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return sorted(sessions, key=lambda item: item[2].get("updated_at", ""), reverse=True)


def restore_session(data):
    if "prompt_snapshot" not in data or "tools_snapshot" not in data:
        current = build_artifact_version(data.get("version", "ui-demo"), PROMPT, TOOLS)
        if data.get("prompt_hash") != current.prompt_hash or data.get("tools_hash") != current.tools_hash:
            return False
        data["prompt_snapshot"] = PROMPT.read_text(encoding="utf-8")
        data["tools_snapshot"] = to_openai_tools(load_tool_declarations(TOOLS))
    st.session_state.research = data
    st.session_state.prompt_snapshot = data["prompt_snapshot"]
    st.session_state.tools_snapshot = data["tools_snapshot"]
    st.session_state.view_only = False
    return True


def select_saved_session(data):
    if not restore_session(data):
        st.session_state.research = data
        st.session_state.tools_snapshot = to_openai_tools(load_tool_declarations(TOOLS))
        st.session_state.view_only = True
    if data.get("version") in load_versions():
        st.session_state.selected_version = data["version"]


def new_chat():
    session = st.session_state.get("research")
    if session:
        start_session(session["provider"], session["model"], st.session_state.get("selected_version", session["version"]),
                      session["max_tool_rounds"], session["history_window"])
    st.session_state.pop("pending_query", None)
    st.session_state.history_search = ""


def telegram_ready():
    return all(os.getenv(key, "").strip() for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"))


def render_turn(turn):
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant", avatar="🔎"):
        if "duration_seconds" in turn:
            st.caption(f"Thời gian xử lý: {turn['duration_seconds']:.1f} giây")
        if turn.get("status") == "provider_error":
            st.error(turn["error"])
        else:
            st.markdown(turn.get("assistant_text") or "Chưa có câu trả lời.")
        if turn.get("status") == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung thông tin.")
        if turn.get("status") == "max_tool_rounds":
            st.warning("Đã đạt giới hạn xử lý. Bạn có thể tiếp tục ở lượt sau.")
        events = turn.get("tool_events", [])
        if turn.get("progress"):
            with st.expander("Các bước xử lý"):
                for step in turn["progress"]:
                    st.caption(f"{step['elapsed_seconds']:.1f}s · {progress_label(step)}")
        if events:
            with st.expander(f"Hoạt động của agent · {len(events)} tool call"):
                for event in events:
                    st.markdown(f"**{event['tool']}**")
                    st.json(event, expanded=False)
        sync = turn.get("telegram_sync", {})
        if sync.get("status") == "sent":
            st.caption("✈ Đã đồng bộ hội thoại sang Telegram")
        elif sync.get("status") in ("error", "partial"):
            st.warning("Telegram chưa đồng bộ đầy đủ. Nội dung chat vẫn được lưu trên ứng dụng.")


def progress_label(event):
    stage = event["stage"]
    if stage == "model_started":
        action = "Đang phân tích yêu cầu" if event["round"] == 1 else "Đang đọc kết quả và chuẩn bị câu trả lời"
        return f"{action} · vòng {event['round']}"
    if stage == "model_completed":
        return "Đã chọn công cụ: " + ", ".join(event["tools"]) if event["tools"] else "Đã tạo câu trả lời"
    if stage == "tool_started":
        return f"Đang chạy {event['tool']}"
    suffix = "gặp lỗi" if event.get("error") else "hoàn tất"
    return f"{event['tool']} {suffix} · {event['duration_seconds']:.1f}s"


with st.sidebar:
    st.title("🔎 Research Desk")
    st.caption("Tra cứu, đọc nguồn và tổng hợp thông tin.")
    st.button("＋ Chat mới", key="new_chat", type="primary", use_container_width=True, on_click=new_chat)
    st.toggle(
        "✈ Đồng bộ Telegram", key="telegram_sync_enabled", disabled=not telegram_ready(),
        help="Bật để tự gửi câu hỏi và câu trả lời của các lượt chat mới sang Telegram. Tắt để dừng đồng bộ.",
    )
    if st.session_state.get("telegram_sync_enabled") and telegram_ready():
        st.caption(f"Đang đồng bộ đến {os.getenv('TELEGRAM_CHAT_ID')}")
    elif not telegram_ready():
        st.caption("Cấu hình TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID trong .env để bật đồng bộ.")
    st.divider()
    versions = load_versions()
    version = st.selectbox("Phiên bản agent", list(versions), index=len(versions)-1,
                           key="selected_version", format_func=lambda name: f"{name} · {versions[name]['description']}")
    st.caption("Chọn phiên bản rồi bấm Chat mới hoặc Áp dụng cấu hình.")
    st.subheader("🕘 Lịch sử hội thoại")
    search = st.text_input("Tìm trong hội thoại", placeholder="Nhập từ khóa…", key="history_search")
    saved = saved_sessions(search.strip())
    if saved:
        active_id = st.session_state.get("research", {}).get("transcript_id")
        for path, label, data in saved:
            title = data["turns"][0].get("user", "Hội thoại")
            st.button(
                title[:80], key=f"history_{path.name}", help=label,
                type="primary" if data.get("transcript_id") == active_id else "secondary",
                use_container_width=True, on_click=select_saved_session, args=(data,),
            )
            st.caption(f"{data.get('updated_at', '')} · {data.get('version', '')} · {data.get('model', '')}")
    else:
        st.caption("Không tìm thấy hội thoại." if search else "Chưa có hội thoại đã lưu.")
    st.divider()
    availability = provider_availability()
    enabled_providers = [name for name, ready in availability.items() if ready]
    provider = st.selectbox("Nhà cung cấp", enabled_providers, disabled=not enabled_providers)
    default_model = make_provider(provider).default_model if provider else ""
    with st.form("settings"):
        model = st.text_input("Model", value=default_model, key=f"model_{provider}")
        with st.expander("Tùy chỉnh"):
            rounds = st.slider("Số vòng tool tối đa", 1, 8, 4)
            history_window = st.slider("Số lượt hội thoại ghi nhớ", 1, 10, 5)
        new_session = st.form_submit_button("Áp dụng cấu hình", disabled=not enabled_providers, use_container_width=True)

    if not enabled_providers:
        st.warning("Chạy Ollama với model đã cài hoặc cấu hình API key trong .env để bắt đầu.")
        if "research" not in st.session_state:
            st.stop()

    if new_session or "research" not in st.session_state:
        selected_model = model.strip() or make_provider(provider).default_model
        start_session(provider, selected_model, version.strip() or "ui-demo", rounds, history_window)

    session = st.session_state.research
    st.divider()
    st.markdown("**Phiên hiện tại**")
    st.caption(f"{session['provider']} · {session['model']}")
    st.caption(f"Phiên bản: {session['version']}")
    st.caption(f"{len(session['turns'])} lượt trao đổi")
    if session["turns"]:
        st.download_button(
            "↓ Tải transcript JSON",
            data=json.dumps(session, ensure_ascii=False, indent=2),
            file_name=f"{session['transcript_id']}.transcript.json",
            mime="application/json",
            use_container_width=True,
        )
    with st.expander("Công cụ có sẵn"):
        for tool in st.session_state.tools_snapshot:
            fn = tool["function"]
            st.markdown(f"**{fn['name']}** — {fn['description']}")

view = st.radio("Chế độ", ["Trò chuyện", "So sánh v0–v1"], horizontal=True, label_visibility="collapsed")
if view == "So sánh v0–v1":
    render_comparison(versions)
    st.stop()

st.title("Bạn muốn tìm hiểu điều gì?")
st.caption("Tìm trên web, theo dõi bài đăng, đọc tài liệu và tổng hợp từ nguồn thực tế.")
st.markdown(f"**Đang dùng:** `{session['version']}` · `{session['model']}` · {session['provider']}")
if provider != session["provider"] or (model.strip() or default_model) != session["model"] or version != session["version"]:
    st.caption("Bấm “Áp dụng cấu hình” để bắt đầu phiên với model và version đã chọn ở thanh bên.")

if not session["turns"]:
    st.info("Chọn nhà cung cấp và model ở thanh bên, hoặc nhập câu hỏi để bắt đầu ngay.")
    examples = [
        ("🌐 Tra cứu web", "Tìm 3 tin mới nhất về AI trong tuần này, kèm nguồn."),
        ("📄 Đọc một trang", "Đọc nội dung https://example.com và tóm tắt bằng tiếng Việt."),
        ("💬 Theo dõi tài khoản", "Lấy 3 bài đăng gần đây của tài khoản sama."),
    ]
    columns = st.columns(3)
    for column, (label, query) in zip(columns, examples):
        with column:
            st.markdown(f"**{label}**")
            st.caption(query)
            if st.button("Thử câu hỏi này", key=label, use_container_width=True):
                st.session_state.pending_query = query

for turn in session["turns"]:
    render_turn(turn)

session_available = availability.get(session["provider"], False)
if st.session_state.get("view_only"):
    st.info("Đang xem phiên cũ. Tạo phiên mới để dùng prompt/tools hiện tại.")
    session_available = False
if not session_available:
    if not st.session_state.get("view_only"):
        st.warning("Nhà cung cấp của phiên này chưa sẵn sàng. Chọn nhà cung cấp khác và bắt đầu phiên mới.")
query = st.chat_input("Nhập câu hỏi hoặc bổ sung thông tin…", disabled=not session_available)
query = query or st.session_state.pop("pending_query", None)
if query and session_available:
    history = []
    for previous in session["turns"]:
        if previous["status"] != "provider_error":
            history.extend([
                {"role": "user", "content": previous["user"]},
                {"role": "assistant", "content": previous["assistant_text"]},
            ])
    turn = {"turn_index": len(session["turns"]) + 1, "started_at": now_iso(), "user": query}
    with st.chat_message("user"):
        st.markdown(query)
    started = monotonic()
    progress_queue = Queue()
    progress_events = []
    with st.status("Agent đang xử lý…", expanded=True) as status:
        timer = st.empty()
        activity = st.empty()
        current_step = "Đang kết nối model"
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    run_model_tool_loop,
                    provider=make_provider(session["provider"]),
                    messages=[
                        {"role": "system", "content": st.session_state.prompt_snapshot},
                        *trim_history(history, session["history_window"]),
                        {"role": "user", "content": query},
                    ],
                    tools=st.session_state.tools_snapshot,
                    model=session["model"],
                    max_tool_rounds=session["max_tool_rounds"],
                    on_progress=progress_queue.put,
                    tool_executor=execute_ui_tool,
                )
                while True:
                    try:
                        event = progress_queue.get(timeout=0.2)
                        progress_events.append(event)
                        current_step = progress_label(event)
                    except Empty:
                        pass
                    elapsed = monotonic() - started
                    timer.markdown(f"⏱ **Đã chờ {elapsed:.0f} giây** · {current_step}")
                    activity.markdown("\n\n".join(
                        f"`{step['elapsed_seconds']:.1f}s` · {progress_label(step)}"
                        for step in progress_events
                    ))
                    if future.done() and progress_queue.empty():
                        break
                result = future.result()
            turn.update(result)
            status.update(label=f"Hoàn tất sau {monotonic() - started:.1f} giây", state="complete")
        except Exception as exc:
            turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}", rounds=[], tool_events=[])
            status.update(label="Có lỗi khi xử lý", state="error")
    turn["duration_seconds"] = round(monotonic() - started, 2)
    turn["progress"] = progress_events
    turn["ended_at"] = now_iso()
    turn = redact(turn)
    if st.session_state.get("telegram_sync_enabled") and telegram_ready():
        with st.spinner("Đang đồng bộ hội thoại sang Telegram…"):
            sync_chat_turn(session, turn, enabled=True)
    session["turns"].append(redact(turn))
    try:
        write_transcript(ROOT / "transcripts" / f"{session['transcript_id']}.transcript.json", session)
    except OSError:
        st.error("Không lưu được transcript trên máy. Bạn vẫn có thể tải JSON ở thanh bên.")
        st.stop()
    st.rerun()
