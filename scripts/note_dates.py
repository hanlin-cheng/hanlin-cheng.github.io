"""Stable note dates from committed history, with a persisted archive fallback."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


def utc_date(value: str) -> str:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


class NoteDates:
    def __init__(self, notes: Path, cache: Path):
        self.notes = notes.resolve()
        self.cache = cache
        self.previous = json.loads(cache.read_text()) if cache.exists() else {}
        self.entries = {}
        root = self.git('rev-parse', '--show-toplevel')
        self.has_history = bool(root and Path(root).resolve() == self.notes
                                and self.git('rev-parse', '--is-shallow-repository') == 'false')

    def git(self, *args: str) -> str:
        try:
            result = subprocess.run(['git', '-C', str(self.notes), *args],
                                    capture_output=True, text=True, timeout=15)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (OSError, subprocess.TimeoutExpired):
            return ''

    def get(self, source: str) -> tuple[str, str]:
        history = self.git('log', '--follow', '--format=%cI', 'HEAD', '--', source) if self.has_history else ''
        if history:
            dates = [utc_date(value) for value in history.splitlines() if value.strip()]
            published, modified = dates[-1], max(dates)
        elif source in self.previous:
            record = self.previous[source]
            published = utc_date(record['date'])
            modified = utc_date(record.get('lastmod', published))
        else:
            # First observation of an untracked/archive-only note. Persist once;
            # later checkouts or repeated synchronizations cannot reset its date.
            published = datetime.fromtimestamp((self.notes / source).stat().st_mtime,
                                               timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            modified = published
        modified = max(published, modified)
        self.entries[source] = {'date': published, 'lastmod': modified}
        return published, modified

    def save(self):
        text = json.dumps(self.entries, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
        if not self.cache.exists() or self.cache.read_text() != text:
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            self.cache.write_text(text)
