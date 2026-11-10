"""Offline UI checks for version isolation and evidence comparison."""
import streamlit as st
import pytest
from streamlit.testing.v1 import AppTest

from conftest import FakeResponse
from version_catalog import ROOT, load_versions


@pytest.fixture
def ui_env(monkeypatch):
    monkeypatch.setattr("env_loader.load_lab_env", lambda root: None)
    for key in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse({"data": [{"id": "qwen2.5:7b"}]}))
    st.cache_data.clear()
    yield
    st.cache_data.clear()


def test_switching_versions_preserves_separate_conversations(ui_env):
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    assert not app.exception
    for version in ("v0", "v1", "v2", "v3"):
        app.selectbox(key="selected_version").select(version).run()
        assert not app.exception
        assert app.session_state["research"]["version"] == version
        assert app.session_state["research"]["prompt_hash"] == load_versions()[version]["prompt_hash"]
    app.selectbox(key="selected_version").select("v0").run()
    app.button(key="new_chat").click().run()
    old_id = app.session_state["research"]["transcript_id"]
    app.session_state["research"]["turns"] = [{"turn_index": 1, "user": "Câu hỏi v0", "assistant_text": "Kết quả v0", "status": "answered", "tool_events": []}]
    app.selectbox(key="selected_version").select("v1").run()
    assert not app.session_state["research"]["turns"]
    app.selectbox(key="selected_version").select("v0").run()
    assert app.session_state["research"]["transcript_id"] == old_id
    assert app.session_state["research"]["turns"][0]["user"] == "Câu hỏi v0"
    app.button(key="new_chat").click().run()
    assert not app.session_state["research"]["turns"]
    assert app.session_state["research"]["transcript_id"] != old_id


def test_comparison_displays_all_versions_and_group_when_available(ui_env):
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    app.radio[0].set_value("So sánh phiên bản").run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ["65%", "85%", "90%", "100%"]
    app.radio(key="compare_suite").set_value("group").run()
    assert not app.exception
    assert app.selectbox(key="compare_before").value == "v2"
    assert app.selectbox(key="compare_after").value == "v3"
    app.selectbox(key="compare_before").select("v0").run()
    assert not app.exception
    assert app.radio(key="compare_suite").value == "base"


def test_comparison_can_be_viewed_without_a_provider(ui_env, monkeypatch):
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse({"data": []}))
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    app.radio[0].set_value("So sánh phiên bản").run()
    assert not app.exception
    assert len(app.metric) == 4
