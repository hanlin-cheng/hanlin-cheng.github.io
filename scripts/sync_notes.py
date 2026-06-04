#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = ROOT / "notes"
CONTENT_DIR = ROOT / "content" / "notes"
STATIC_DIR = ROOT / "static" / "notes"
STATIC_SEARCH_INDEX = ROOT / "static" / "search-index.json"

SECTIONS = {
    "Algorithm": "算法",
    "C++": "C++",
    "Linux": "Linux",
    "QT": "Qt",
    "command": "命令与工具",
    "slam_config": "SLAM 配置",
    "something_else": "其他",
}

SKIP_DIRS = {".git", ".obsidian", ".agents", ".codex"}
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


def normalize_markdown(text: str) -> str:
    text = text.replace("](/./media/", "](media/")
    text = text.replace("](./media/", "](media/")
    text = text.replace('src="./media/', 'src="media/')
    text = text.replace('src="/./media/', 'src="media/')
    return text


def front_matter(title: str, category: str, source: str, weight: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return "\n".join(
        [
            "---",
            f"title: {quote_yaml(title)}",
            f"date: {quote_yaml(now)}",
            "draft: false",
            f"weight: {weight}",
            "categories:",
            f"  - {quote_yaml(category)}",
            "source:",
            f"  path: {quote_yaml(source)}",
            "---",
            "",
        ]
    )


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
        if item.name in SKIP_DIRS or item.name not in SECTIONS:
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
    for src in sorted(NOTES_DIR.rglob("*.md")):
        rel = src.relative_to(NOTES_DIR)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        section, category = section_for(rel)
        if section not in SECTIONS:
            continue

        body = normalize_markdown(src.read_text(encoding="utf-8", errors="ignore"))
        title = title_from_markdown(body, src.stem)
        target = CONTENT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            front_matter(title, category, str(rel), stable_weight(rel)) + body,
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
    clean_generated()
    copy_assets()
    pages = sync_markdown()
    write_index(pages)
    print(f"Synced {len(pages)} notes from {NOTES_DIR}")


if __name__ == "__main__":
    main()
