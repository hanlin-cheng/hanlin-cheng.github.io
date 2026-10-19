#!/usr/bin/env python3
"""Validate local note links (including README), excluding code examples."""
from pathlib import Path
import argparse
from urllib.parse import unquote, urlsplit
from note_links import link_targets


def check(root: Path) -> tuple[int, list[str]]:
    checked = 0
    missing = []
    for note in sorted(root.rglob('*.md')):
        if any(part.startswith('.') for part in note.relative_to(root).parts):
            continue
        for link in link_targets(note.read_text(encoding='utf-8')):
            url = urlsplit(link.value)
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            target = (root / path.lstrip('/')) if path.startswith('/') else (note.parent / path)
            if link.kind == 'wiki' and not target.suffix and not target.exists():
                target = target.with_suffix('.md')
            checked += 1
            if not target.is_file():
                missing.append(f'{note.relative_to(root)}: {link.value}')
    return checked, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1]/'notes')
    args = parser.parse_args()
    count, missing = check(args.root)
    print(f'Checked {count} local links; missing: {len(missing)}')
    for entry in missing:print(entry)
    raise SystemExit(bool(missing))


if __name__ == '__main__':main()
