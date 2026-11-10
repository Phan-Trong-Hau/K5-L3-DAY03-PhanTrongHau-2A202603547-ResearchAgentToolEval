---
name: extract_links
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [text, max_results]
outputs: [items, item_count, total_unique, truncated]
side_effect: false
---

# extract_links

Post-submission addition by Lưu Văn Việt Đức — 2A202603445, reviewed separately
from the submitted v3 release under version `v3-extract-links`.

Extract and list HTTP/HTTPS URLs already present in user-provided plain text or
Markdown notes, articles, or newsletters. Runs locally with the Python standard
library, no API key, no new dependencies, no network calls, and no file writes.
It does not search for sources, download pages, check accessibility, or describe
page contents. Use `lookup`, `fetch`, `github_repos`, or `export_chat` for their
respective search, retrieval, repository search, and transcript export tasks.
Pass the provided text verbatim; do not invent text or URLs.

## Inputs

| Input | Type | Meaning |
|---|---|---|
| `text` | Required string | Nonempty text to process, preserved verbatim in the call. |
| `max_results` | Integer, default `10` | Maximum returned URLs, inclusive range `1`–`50`. Booleans are rejected. |

## Output

Success is a dictionary with `tool: "extract_links"` and:

- `items`: objects with exactly `title`, `url`, `source`, `summary`. Both `title`
  and `url` are the extracted URL; `source` is its hostname (without credentials
  or port, lowercased by Python's URL parser); `summary` is always `""`.
- `item_count`: the number of objects actually returned.
- `total_unique`: all valid unique URLs found before the limit is applied.
- `truncated`: `true` only when valid unique URLs were omitted by the limit.

First occurrence determines order. Deduplication compares extracted URL strings
exactly after removing delimiters. URL casing, queries (including tracking
parameters), fragments, percent escapes, and trailing slashes are preserved;
URLs differing in any of these remain separate. Host syntax is validated without
DNS resolution: DNS labels (including single-label hosts such as `localhost`),
IDNA hostnames, IPv4, and bracketed IPv6 are supported. Invalid host labels,
missing hosts, malformed ports/percent escapes, and non-HTTP(S) schemes are
ignored. A valid nonempty input containing no URLs succeeds with empty `items`,
both counts `0`, and `truncated: false`.

## Examples

```python
extract_links("Sources: [A](https://example.com/a), "
              "[https://example.com/a](https://example.com/a) and "
              "[https://example.org/b](https://example.org/b)")
# {
#   "tool": "extract_links",
#   "items": [
#     {"title": "https://example.com/a", "url": "https://example.com/a",
#      "source": "example.com", "summary": ""},
#     {"title": "https://example.org/b", "url": "https://example.org/b",
#      "source": "example.org", "summary": ""}
#   ],
#   "item_count": 2, "total_unique": 2, "truncated": False
# }

extract_links("https://example.com/a <https://example.org/b>", max_results=1)
# Returns only the first URL; item_count=1, total_unique=2, truncated=True.
```

## Errors

Expected input errors return `{"tool": "extract_links", "error": "TypeError"
or "ValueError", "message": "..."}` and are not raised to the agent.

- `TypeError`: `text` is not a string; `max_results` is not an integer or is a boolean.
- `ValueError`: `text` is empty/whitespace-only; `max_results` is outside `1`–`50`.

Malformed URL candidates are skipped while other valid URLs are retained.
Unexpected programming errors are not hidden by a catch-all exception.

## Limits of text scanning

Supports bare URLs, standard inline `[label](URL)` links, and `<URL>` autolinks.
Quotes, backticks, whitespace, angle brackets, and unmatched closing `)`, `]`,
or `}` end a candidate. Balanced brackets within a URL, such as
`https://example.com/wiki/Topic_(detail)`, are kept.

This is not a full Markdown/HTML parser: it scans literal text, including URL
labels, code, and reference definitions; it does not resolve reference links,
decode HTML entities, unescape Markdown, or interpret nested/escaped link syntax.
Separate links with whitespace or normal Markdown delimiters. Adjacent links
joined only by punctuation and unbalanced brackets within URLs are ambiguous.
For bare URLs, trailing `. , ; : ! ? *` and common fullwidth sentence punctuation
are treated as prose/Markdown delimiters. In a complete `<URL>` autolink or
`[label](URL)` destination, final punctuation belongs to the URL and is preserved.
A bare URL that genuinely ends in one of these characters should use an explicit
link delimiter or percent-encode it to retain it unambiguously. No guarantee is made that
a syntactically valid host exists, is reachable, or contains trustworthy content.
