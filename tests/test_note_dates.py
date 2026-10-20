"""Dates must survive rebuilds, renames, dirty worktrees and source archives."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from note_dates import NoteDates


class NoteDateTests(unittest.TestCase):
    def test_untracked_note_is_registered_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            note = root / 'math/note.md'
            note.parent.mkdir()
            note.write_text('# Note')
            os.utime(note, (1000000000, 1000000000))
            cache = root / 'dates.json'
            dates = NoteDates(root, cache)
            first = dates.get('math/note.md')
            dates.save()
            os.utime(note, (1700000000, 1700000000))
            self.assertEqual(NoteDates(root, cache).get('math/note.md'), first)

    @unittest.skipUnless(shutil.which('git'), 'requires Git')
    def test_history_follows_rename_and_ignores_checkout_mtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args, stamp=None):
                env = os.environ.copy()
                if stamp:
                    env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
                return subprocess.run(['git', '-C', str(root), *args], check=True,
                                      capture_output=True, text=True, env=env)
            git('init', '-q')
            git('config', 'user.name', 'Date regression')
            git('config', 'user.email', 'test@example.invalid')
            note = root / 'old.md'
            note.write_text('# First')
            git('add', 'old.md')
            git('commit', '-qm', 'Add note', stamp='2020-01-02T03:04:05Z')
            git('mv', 'old.md', 'new.md')
            git('commit', '-qm', 'Move note', stamp='2021-06-07T08:09:10Z')
            note = root / 'new.md'
            note.write_text('# Uncommitted update')
            os.utime(note, (1800000000, 1800000000))
            cache = root / 'dates.json'
            dates = NoteDates(root, cache)
            expected = ('2020-01-02T03:04:05Z', '2021-06-07T08:09:10Z')
            self.assertEqual(dates.get('new.md'), expected)
            dates.save()
            # A source archive has no Git history and different filesystem dates.
            shutil.rmtree(root / '.git')
            self.assertEqual(NoteDates(root, cache).get('new.md'), expected)
