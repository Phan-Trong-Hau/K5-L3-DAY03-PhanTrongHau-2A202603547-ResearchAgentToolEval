"""Extract HTTP(S) links from text without fetching or rewriting them."""
from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from tools._shared import err


_URL_START = re.compile(r"(?<![\w+.-])https?://", re.IGNORECASE)
_HOST_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")
_CLOSERS = {")": "(", "]": "[", "}": "{"}
_TRAILING_PUNCTUATION = ".,;:!?*，。；：！？"


def _candidate_end(text: str, start: int) -> int:
    """Stop at text delimiters or an unmatched closing Markdown bracket."""
    brackets: list[str] = []
    end = start
    while end < len(text):
        char = text[end]
        if char.isspace() or char in "<>\"'`“”‘’":
            break
        if char in "([{":
            brackets.append(char)
        elif char in _CLOSERS:
            if not brackets or brackets[-1] != _CLOSERS[char]:
                break
            brackets.pop()
        end += 1
    return end


def _hostname(url: str) -> str | None:
    """Validate syntax only; urlsplit alone does not validate DNS host labels."""
    if "\\" in url or any(ord(char) < 32 or ord(char) == 127 for char in url):
        return None
    if re.search(r"%(?![0-9A-Fa-f]{2})", url):
        return None
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        # Accessing .port rejects malformed and out-of-range ports.
        port = parsed.port
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not hostname:
        return None
    if port is None and parsed.netloc.endswith(":"):
        return None

    if ":" in hostname:
        try:
            ipaddress.IPv6Address(hostname)
        except ValueError:
            return None
    else:
        try:
            ascii_host = hostname.encode("idna").decode("ascii").removesuffix(".")
        except UnicodeError:
            return None
        if not ascii_host or len(ascii_host) > 253:
            return None
        if not all(_HOST_LABEL.fullmatch(label) for label in ascii_host.split(".")):
            return None
        if re.fullmatch(r"[0-9.]+", ascii_host) and "." in ascii_host:
            try:
                ipaddress.IPv4Address(ascii_host)
            except ValueError:
                return None
    return hostname


def extract_links(text: str, max_results: int = 10) -> dict:
    """Return unique links in appearance order; input errors are error dicts."""
    if not isinstance(text, str):
        return err("extract_links", TypeError("text must be a string"))
    if not text.strip():
        return err("extract_links", ValueError("text must not be empty or whitespace-only"))
    if isinstance(max_results, bool) or not isinstance(max_results, int):
        return err("extract_links", TypeError("max_results must be an integer (not a boolean)"))
    if not 1 <= max_results <= 50:
        return err("extract_links", ValueError("max_results must be between 1 and 50"))

    seen: set[str] = set()
    items: list[dict[str, str]] = []
    position = 0
    while match := _URL_START.search(text, position):
        end = _candidate_end(text, match.end())
        start = match.start()
        url = text[start:end]
        # Explicit link delimiters disambiguate punctuation belonging to the URL.
        autolink = start > 0 and text[start - 1] == "<" and text[end:end + 1] == ">"
        markdown_link = text[max(0, start - 2):start] == "](" and text[end:end + 1] == ")"
        if not (autolink or markdown_link):
            url = url.rstrip(_TRAILING_PUNCTUATION)
        hostname = _hostname(url)
        # Retry after a malformed prefix so it cannot hide a later valid URL.
        position = end if hostname else match.end()
        if hostname and url not in seen:
            seen.add(url)
            if len(items) < max_results:
                items.append({"title": url, "url": url, "source": hostname, "summary": ""})

    return {
        "tool": "extract_links",
        "items": items,
        "item_count": len(items),
        "total_unique": len(seen),
        "truncated": len(seen) > len(items),
    }
