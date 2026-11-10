from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Desk", page_icon="🔎", layout="wide")


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
    artifact = build_artifact_version(version, PROMPT, TOOLS)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    session_id = f"ui_{safe_slug(version)}_{provider}_{stamp}_{uuid4().hex[:8]}"
    st.session_state.research = {
        "transcript_id": session_id,
        **artifact_version_dict(artifact),
        "provider": provider,
        "model": model,
        "system_prompt": str(PROMPT),
        "tools": str(TOOLS),
        "history_window": history_window,
        "max_tool_rounds": rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.prompt_snapshot = PROMPT.read_text(encoding="utf-8")
    st.session_state.tools_snapshot = to_openai_tools(load_tool_declarations(TOOLS))


def render_turn(turn):
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant", avatar="🔎"):
        if turn.get("status") == "provider_error":
            st.error(turn["error"])
        else:
            st.markdown(turn.get("assistant_text") or "Chưa có câu trả lời.")
        if turn.get("status") == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung thông tin.")
        if turn.get("status") == "max_tool_rounds":
            st.warning("Đã đạt giới hạn xử lý. Bạn có thể tiếp tục ở lượt sau.")
        events = turn.get("tool_events", [])
        if events:
            with st.expander(f"Hoạt động của agent · {len(events)} tool call"):
                for event in events:
                    st.markdown(f"**{event['tool']}**")
                    st.json(event, expanded=False)


with st.sidebar:
    st.title("🔎 Research Desk")
    st.caption("Tra cứu, đọc nguồn và tổng hợp thông tin.")
    with st.form("settings"):
        provider = st.selectbox("Nhà cung cấp", ["ollama", "openrouter", "openai", "anthropic", "gemini"])
        model = st.text_input("Model", placeholder="Để trống để dùng model mặc định")
        version = st.text_input("Phiên bản", value="ui-demo")
        with st.expander("Tùy chỉnh"):
            rounds = st.slider("Số vòng tool tối đa", 1, 8, 4)
            history_window = st.slider("Số lượt hội thoại ghi nhớ", 1, 10, 5)
        new_session = st.form_submit_button("Bắt đầu phiên mới", use_container_width=True)

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

st.title("Bạn muốn tìm hiểu điều gì?")
st.caption("Tìm trên web, theo dõi bài đăng, đọc tài liệu và tổng hợp từ nguồn thực tế.")

if not session["turns"]:
    st.info("Chọn model ở thanh bên, hoặc bắt đầu ngay với Ollama đang chạy trên máy.")
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

query = st.chat_input("Nhập câu hỏi hoặc bổ sung thông tin…")
query = query or st.session_state.pop("pending_query", None)
if query:
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
    with st.spinner("Agent đang tra cứu và xử lý…"):
        try:
            result = run_model_tool_loop(
                provider=make_provider(session["provider"]),
                messages=[
                    {"role": "system", "content": st.session_state.prompt_snapshot},
                    *trim_history(history, session["history_window"]),
                    {"role": "user", "content": query},
                ],
                tools=st.session_state.tools_snapshot,
                model=session["model"],
                max_tool_rounds=session["max_tool_rounds"],
            )
            turn.update(result)
        except Exception as exc:
            turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}", rounds=[], tool_events=[])
    turn["ended_at"] = now_iso()
    session["turns"].append(redact(turn))
    try:
        write_transcript(ROOT / "transcripts" / f"{session['transcript_id']}.transcript.json", session)
    except OSError:
        st.error("Không lưu được transcript trên máy. Bạn vẫn có thể tải JSON ở thanh bên.")
        st.stop()
    st.rerun()
