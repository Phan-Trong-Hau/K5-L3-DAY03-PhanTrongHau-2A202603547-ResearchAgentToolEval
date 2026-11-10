from conftest import FakeResponse
from tools.github_repos.tool import search_github_repos


def test_github_uses_optional_token_in_header(monkeypatch, fake_http):
    monkeypatch.setenv("GITHUB_TOKEN", "test-github-token")
    calls = fake_http(FakeResponse({"items": []}))
    search_github_repos("RAG", language="Python", limit=3)
    assert calls[0]["headers"]["Authorization"] == "Bearer test-github-token"
    assert calls[0]["params"]["q"] == "RAG language:Python"


def test_github_works_without_token(fake_http):
    calls = fake_http(FakeResponse({"items": []}))
    search_github_repos("RAG")
    assert "Authorization" not in calls[0]["headers"]


def test_github_rate_limit_returns_reset_without_retry(fake_http):
    response = FakeResponse({"message": "API rate limit exceeded"}, status_code=403)
    response.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "12345"}
    calls = fake_http(response)
    result = search_github_repos("RAG")
    assert result["error"] == "rate_limit"
    assert result["reset_at"] == "12345"
    assert len(calls) == 1


def test_github_forbidden_is_not_assumed_to_be_rate_limit(fake_http):
    response = FakeResponse({"message": "Forbidden"}, status_code=403)
    response.headers = {}
    fake_http(response)
    assert search_github_repos("RAG")["error"] == "HTTPError"
