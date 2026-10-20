#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from note_links import link_targets, rewrite_links
from note_dates import NoteDates


ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"
CONTENT_DIR = ROOT / "content" / "notes"
STATIC_DIR = ROOT / "static" / "notes"
STATIC_SEARCH_INDEX = ROOT / "static" / "search-index.json"

SECTIONS = {
    "math": "数学基础",
    "robotics": "SLAM 与机器人",
    "ros": "ROS 与中间件",
    "cpp": "C++ 开发",
    "engineering": "开发工具与工程实践",
    "linux": "Linux 与嵌入式",
    "qt": "Qt 开发",
    "misc": "应用与杂记",
    "papers": "论文阅读",
}
MIGRATION_FILE = ROOT / "data" / "note-migration.json"
DATE_CACHE_FILE = ROOT / "data" / "note-dates.json"


SKIP_DIRS = {".git", ".agents", ".codex"}
SKIP_SUFFIXES = {".whl", ".pyc"}


def quote_yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def stable_weight(path: Path) -> int:
    digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()
    return int(digest[:6], 16)


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def section_for(path: Path) -> tuple[str, str]:
    section = path.parts[0]
    return section, SECTIONS.get(section, section)


def normalize_markdown(text: str, source: str | None = None) -> str:
    def rewrite(value: str, kind: str) -> str:
        if value.startswith("/./media/"):
            value = value[3:]
        elif value.startswith("./media/"):
            value = value[2:]
        if not source or not kind.startswith("html"):
            return value
        url = urlsplit(value)
        if url.scheme or url.netloc or value.startswith(("/", "#")):
            return value
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(url.path)))
        if target.startswith("../"):
            raise ValueError(f"HTML attachment escapes notes root: {source}: {value}")
        result = "/notes/" + quote(target, safe="/%+._-()")
        if url.query:
            result += "?" + url.query
        if url.fragment:
            result += "#" + url.fragment
        return result

    return rewrite_links(text, rewrite)


IMAGE_SUFFIXES = {".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp", ""}


def is_local_image(src: str) -> bool:
    return not re.match(r"^(?:[a-z][a-z0-9+.-]*:)?//", src, re.IGNORECASE) and not src.startswith(
        ("data:", "#", "/")
    )


def clean_image_src(src: str) -> str:
    src = src.strip().strip("<>")
    while src.startswith("./"):
        src = src[2:]
    return src.replace("\\", "/")


def cover_url(section: str, src: str) -> str:
    src = quote(clean_image_src(src), safe="/%+._-()")
    return "/notes/" + posixpath.normpath(f"{section}/{src}")


def first_local_image(text: str, section: str) -> str | None:
    for link in link_targets(text):
        if link.kind not in {"image", "html-image"}:
            continue
        src = clean_image_src(link.value)
        if link.kind == "html-image" and src.startswith("/notes/"):
            return src
        if is_local_image(src):
            return cover_url(section, src)
    return None


def fallback_section_image(section: str) -> str | None:
    media_dir = NOTES_DIR / section / "media"
    if not media_dir.exists():
        return None

    for path in sorted(media_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            rel = path.relative_to(NOTES_DIR / section).as_posix()
            return cover_url(section, rel)
    return None


def front_matter(
    title: str, category: str, source: str, weight: int, image: str | None = None,
    aliases: list[str] | None = None, *, date: str, lastmod: str
) -> str:
    lines = [
        "---",
        f"title: {quote_yaml(title)}",
        f"date: {quote_yaml(date)}",
        f"lastmod: {quote_yaml(lastmod)}",
        "draft: false",
        f"weight: {weight}",
    ]
    if aliases:
        lines.append("aliases:")
        lines.extend(f"  - {quote_yaml(alias)}" for alias in aliases)
    if image:
        lines.append(f"image: {quote_yaml(image)}")
    lines.extend(
        [
            "categories:",
            f"  - {quote_yaml(category)}",
            "source:",
            f"  path: {quote_yaml(source)}",
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def clean_generated() -> None:
    for path in (CONTENT_DIR, STATIC_DIR, STATIC_SEARCH_INDEX):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_SEARCH_INDEX.parent.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    for item in NOTES_DIR.iterdir():
        if item.name in SKIP_DIRS or item.name not in {*SECTIONS, "media"}:
            continue
        if not item.is_dir():
            continue
        target_root = STATIC_DIR / item.name
        for path in item.rglob("*"):
            rel = path.relative_to(item)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if path.is_file() and path.suffix.lower() not in {".md", *SKIP_SUFFIXES}:
                target = target_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)


def sync_markdown() -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    dates = NoteDates(NOTES_DIR, DATE_CACHE_FILE)
    migration = json.loads(MIGRATION_FILE.read_text()) if MIGRATION_FILE.exists() else {}
    legacy_urls = migration.get("legacy_urls", {})
    for src in sorted(NOTES_DIR.rglob("*.md")):
        rel = src.relative_to(NOTES_DIR)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        section, category = section_for(rel)
        if section not in SECTIONS:
            continue

        body = normalize_markdown(src.read_text(encoding="utf-8", errors="ignore"), rel.as_posix())
        title = title_from_markdown(body, src.stem)
        image = first_local_image(body, section) or fallback_section_image(section)
        target = CONTENT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        published, modified = dates.get(rel.as_posix())
        target.write_text(
            front_matter(title, category, rel.as_posix(), stable_weight(rel), image, legacy_urls.get(rel.as_posix()), date=published, lastmod=modified) + body,
            encoding="utf-8",
        )
        pages.append(
            {
                "title": title,
                "category": category,
                "path": f"notes/{rel.with_suffix('.html').as_posix()}",
                "source": rel.as_posix(),
            }
        )
    dates.save()
    return pages


def write_index(pages: list[dict[str, str]]) -> None:
    (CONTENT_DIR / "_index.md").write_text(
        "---\ntitle: \"全部笔记\"\n---\n",
        encoding="utf-8",
    )
    STATIC_SEARCH_INDEX.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if not NOTES_DIR.exists():
        raise SystemExit(
            "notes/ submodule not found. Run: git submodule update --init --recursive"
        )
    if not any(path.is_file() and path.suffix.lower() == ".md"
               for section in SECTIONS for path in (NOTES_DIR / section).glob("**/*")):
        raise SystemExit("No publishable notes found; refusing to clear generated files.")
    clean_generated()
    copy_assets()
    pages = sync_markdown()
    write_index(pages)
    print(f"Synced {len(pages)} notes from {NOTES_DIR}")


if __name__ == "__main__":
    main()
