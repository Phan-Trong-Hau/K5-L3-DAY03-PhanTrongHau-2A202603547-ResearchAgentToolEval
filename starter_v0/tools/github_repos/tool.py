from __future__ import annotations

from typing import Any
import os

import requests

from tools._shared import TIMEOUT, err

ALLOWED_SORTS = {"stars", "forks", "updated"}


def search_github_repos(
    query: str = "",
    language: str = "",
    sort: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if sort not in ALLOWED_SORTS:
            raise ValueError(f"sort must be one of {sorted(ALLOWED_SORTS)}, got {sort!r}")
        limit_int = int(limit)
        if limit_int <= 0:
            raise ValueError("limit must be a positive integer")
        limit_int = min(limit_int, 20)

        q = query.strip()
        if isinstance(language, str) and language.strip():
            q = f"{q} language:{language.strip()}"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AI20k-Day03-Research-Agent/1.0",
        }
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": q,
                "sort": sort,
                "order": "desc",
                "per_page": limit_int,
            },
            headers=headers,
            timeout=TIMEOUT,
        )
        if response.status_code in (403, 429):
            metadata = getattr(response, "headers", {})
            payload = response.json()
            message = str(payload.get("message", "")) if isinstance(payload, dict) else ""
            if metadata.get("X-RateLimit-Remaining") == "0" or "rate limit" in message.lower() or response.status_code == 429:
                return {
                    "tool": "search_github_repos", "error": "rate_limit",
                    "message": "GitHub đang giới hạn request. Chờ quota reset hoặc cấu hình GITHUB_TOKEN trong .env; không gọi lại liên tục.",
                    "retry_after": metadata.get("Retry-After"),
                    "reset_at": metadata.get("X-RateLimit-Reset"),
                }
        response.raise_for_status()
        data = response.json()
        raw_items = data.get("items", []) or []
        items = [
            {
                "title": item.get("full_name") or item.get("name"),
                "url": item.get("html_url"),
                "source": "github.com",
                "summary": item.get("description") or "",
                "stars": item.get("stargazers_count", 0),
                "language": item.get("language"),
            }
            for item in raw_items[:limit_int]
        ]
        return {
            "tool": "search_github_repos",
            "query": query.strip(),
            "language": language.strip() if isinstance(language, str) else "",
            "sort": sort,
            "items": items,
        }
    except Exception as exc:
        return err("search_github_repos", exc)

