"""Read and rewrite note links while leaving fenced and inline code unchanged."""
from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
import html
import re


@dataclass(frozen=True)
class LinkTarget:
    start: int
    end: int
    value: str
    kind: str


def protected_ranges(text: str) -> list[tuple[int, int]]:
    """Return code spans that must never be changed during link migration."""
    ranges = []
    fence = None
    start = offset = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
                start = offset
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                ranges.append((start, offset + len(line)))
                fence = None
        offset += len(line)
    if fence:
        ranges.append((start, len(text)))
    ranges.extend(match.span() for match in re.finditer(r"(`+)[^`\n]*?\1", text))
    return ranges


def link_targets(text: str) -> Iterator[LinkTarget]:
    """Scan this repository's Markdown/HTML/reference/wiki link forms.

    This is a targeted link scanner, not a complete CommonMark parser. In
    particular, it balances parentheses in destinations used by these notes.
    """
    protected = protected_ranges(text)
    results = []

    def skipped(start: int) -> bool:
        return any(left <= start < right for left, right in protected)

    for match in re.finditer(r"!?\[[^\]\n]*\]\(", text):
        if skipped(match.start()):
            continue
        begin = cursor = match.end()
        depth = 1
        escaped = angle = False
        while cursor < len(text):
            char = text[cursor]
            if char == "\n":
                break
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "<" and cursor == begin:
                angle = True
            elif char == ">" and angle:
                angle = False
            elif not angle:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        break
            cursor += 1
        if depth != 0:
            continue
        raw = text[begin:cursor]
        begin += len(raw) - len(raw.lstrip())
        raw = raw.strip()
        if raw.startswith("<") and ">" in raw:
            end = begin + raw.index(">")
            begin += 1
        else:
            title = re.search(r'''\s+["'].*["']\s*$''', raw)
            end = begin + (title.start() if title else len(raw))
        if end > begin:
            kind = "image" if match.group().startswith("!") else "markdown"
            results.append(LinkTarget(begin, end, text[begin:end], kind))

    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", text):
        if skipped(match.start()):
            continue
        begin, end = match.span(1)
        if text[begin] == "<":
            begin += 1
            end -= 1
        results.append(LinkTarget(begin, end, text[begin:end], "reference"))

    for tag in re.finditer(r"<(?:img|a|source)\b[^>]*>", text, re.I):
        if skipped(tag.start()):
            continue
        for attr in re.finditer(r'''\b(?:src|href)\s*=\s*(["'])(.*?)\1''', tag.group(), re.I):
            begin = tag.start() + attr.start(2)
            end = tag.start() + attr.end(2)
            is_image = re.match(r"<img\b", tag.group(), re.I) and attr.group().lower().startswith("src")
            kind = "html-image" if is_image else "html"
            results.append(LinkTarget(begin, end, html.unescape(text[begin:end]), kind))

    for match in re.finditer(r"!?\[\[([^\]\n]+)\]\]", text):
        if skipped(match.start()):
            continue
        begin = match.start(1)
        end = begin + len(match.group(1).split("|", 1)[0])
        results.append(LinkTarget(begin, end, text[begin:end], "wiki"))

    yield from sorted(results, key=lambda link: link.start)


def rewrite_links(text: str, rewrite: Callable[[str, str], str]) -> str:
    for link in reversed(list(link_targets(text))):
        value = rewrite(link.value, link.kind)
        if value == link.value:
            continue
        if link.kind.startswith("html"):
            value = html.escape(value, quote=True)
        text = text[:link.start] + value + text[link.end:]
    return text
