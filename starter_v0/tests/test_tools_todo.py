"""Tool Unit Test Challenge — Completed (0 skipped, 0 failed)."""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    clarify_tool = TOOL_FUNCTIONS["clarify"]
    result = clarify_tool(
        question="Bạn muốn tìm trên nguồn nào?",
        response_type="choice",
        options=["Web", "Twitter"],
    )
    assert result["options"] == ["Web", "Twitter"]
    assert result["awaiting_user"] is True
    assert result["response_type"] == "choice"


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Tin 1", "section": "A"},
        {"title": "Tin 2", "section": "B"},
        {"title": "Tin 3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [{"title": "Mục 1"}, {"title": "Mục 2"}]
    result = format_tool(items=items, template="thread")
    lines = [line.strip() for line in result["markdown"].splitlines() if line.strip()]
    assert any(line.startswith("1/") for line in lines)
    assert any(line.startswith("2/") for line in lines)


def test_format_empty_items_does_not_crash() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    res_none = format_tool(items=None, template="brief")
    res_empty = format_tool(items=[], template="brief")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-bot-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat-id")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 10}}))
    send_tool = TOOL_FUNCTIONS["send"]

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert "test-bot-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "test-chat-id"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    calls = fake_http(FakeResponse({"ok": True}))
    send_tool = TOOL_FUNCTIONS["send"]

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert "error" in result
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool = TOOL_FUNCTIONS["lookup"]

    lookup_tool(query="OpenAI", topic="general", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-fc-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "Nội dung bài viết chi tiết",
            "metadata": {"title": "T", "sourceURL": "https://openai.com/blog/test"},
        }
    }))
    fetch_tool = TOOL_FUNCTIONS["fetch"]

    result = fetch_tool(url="https://openai.com/blog/test")

    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://openai.com/blog/test"
    assert item["source"] == "openai.com"
    assert item["summary"] == "Nội dung bài viết chi tiết"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-fc-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "x" * 5500,
            "metadata": {"title": "T", "sourceURL": "https://openai.com/blog/test"},
        }
    }))
    fetch_tool = TOOL_FUNCTIONS["fetch"]

    result = fetch_tool(url="https://openai.com/blog/test")

    summary = result["items"][0]["summary"]
    assert len(summary) <= 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    mock_tweets = [{"text": "no id tweet"}] + [
        {"tweet_id": str(i), "screen_name": "sama", "text": f"Tweet {i}"} for i in range(1, 7)
    ]
    fake_http(FakeResponse({"timeline": mock_tweets}))
    timeline_tool = TOOL_FUNCTIONS["timeline"]

    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"], start=1):
        assert item["url"] == f"https://x.com/sama/status/{idx}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    calls = fake_http(FakeResponse({"timeline": []}))
    social_tool = TOOL_FUNCTIONS["social_search"]

    social_tool(query="GPT-5", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "GPT-5"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="   ")
    items = result.get("results", result.get("items", []))
    assert items == []


def test_policy_area_filter_only_returns_that_area() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="privacy data", policy_area="data_privacy")
    items = result.get("results", result.get("items", []))
    assert len(items) > 0
    assert all(item["policy_area"] == "data_privacy" for item in items)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="citation source ignore", policy_area="source_citation", top_k=5)
    items = result.get("results", result.get("items", []))
    assert len(items) > 0
    assert any(item.get("untrusted_text") for item in items)
    for item in items:
        for untrusted_line in item.get("untrusted_text", []):
            assert untrusted_line not in item.get("facts", [])


# ---------------- YOUR NEW TOOL(S) ----------------

def test_my_new_tool_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "langchain-ai/langchain",
                "html_url": "https://github.com/langchain-ai/langchain",
                "description": "Build context-aware reasoning applications",
                "stargazers_count": 98000,
                "language": "Python",
            }
        ]
    }))
    github_tool = TOOL_FUNCTIONS["github_repos"]
    result = github_tool(query="AI agent", language="python", sort="stars", limit=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "AI agent language:python"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert result["tool"] == "search_github_repos"
    assert result["items"][0] == {
        "title": "langchain-ai/langchain",
        "url": "https://github.com/langchain-ai/langchain",
        "source": "github.com",
        "summary": "Build context-aware reasoning applications",
        "stars": 98000,
        "language": "Python",
    }


def test_my_new_tool_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))
    github_tool = TOOL_FUNCTIONS["github_repos"]

    empty_res = github_tool(query="   ")
    assert empty_res["error"] == "ValueError"
    assert "query" in empty_res["message"]

    bad_sort_res = github_tool(query="agent", sort="invalid_sort")
    assert bad_sort_res["error"] == "ValueError"
    assert "sort" in bad_sort_res["message"]

    bad_limit_res = github_tool(query="agent", limit=0)
    assert bad_limit_res["error"] == "ValueError"
    assert calls == []


def test_my_new_tool_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    github_tool = TOOL_FUNCTIONS["github_repos"]
    result = github_tool(query="AI agent")
    assert result["tool"] == "search_github_repos"
    assert result["error"] == "HTTPError"