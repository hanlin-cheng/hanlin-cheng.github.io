import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from note_links import link_targets, rewrite_links
import sync_notes as sync


class LinkParsingTests(unittest.TestCase):
    def test_nested_parentheses_spaces_and_titles(self):
        text = '[标定](<../robotics/标定(lidar imu).md#参数>)\n![图](../media/a(b).png "图题")'
        self.assertEqual([x.value for x in link_targets(text)],
                         ['../robotics/标定(lidar imu).md#参数', '../media/a(b).png'])
        self.assertEqual([x.kind for x in link_targets(text)], ['markdown', 'image'])

    def test_code_examples_are_not_rewritten(self):
        text = '```md\n![示例](old.png)\n```\n`[代码](old.md)`\n![真图](old.png)'
        updated = rewrite_links(text, lambda value, kind: value.replace('old', 'new'))
        self.assertIn('![示例](old.png)', updated)
        self.assertIn('`[代码](old.md)`', updated)
        self.assertIn('![真图](new.png)', updated)

    def test_html_and_reference_links(self):
        text = '<img src="../media/a.png?x=1&amp;y=2">\n[x]: <a(b).md>\n![[image.png|图]]'
        links = list(link_targets(text))
        self.assertEqual([x.kind for x in links], ['html-image', 'reference'])
        self.assertEqual(links[0].value, '../media/a.png?x=1&y=2')


class GenerationTests(unittest.TestCase):
    def test_cover_ignores_links_and_keeps_balanced_filename(self):
        body = '[附件](manual.pdf)\n![图片](<../media/Algorithm/a(b).png>)'
        self.assertEqual(sync.first_local_image(body, 'math'), '/notes/media/Algorithm/a(b).png')

    def test_html_uses_source_directory_without_changing_code(self):
        body = '<img src="../media/Algorithm/a.png">\n```html\n<img src="example.png">\n```'
        result = sync.normalize_markdown(body, 'math/note.md')
        self.assertIn('src="/notes/media/Algorithm/a.png"', result)
        self.assertIn('src="example.png"', result)

    def test_shared_assets_categories_and_old_urls(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            notes = root / 'notes'
            (notes / 'math').mkdir(parents=True)
            (notes / 'media/Algorithm').mkdir(parents=True)
            (notes / 'math/note.md').write_text('# 数学笔记\n![图](../media/Algorithm/a(b).png)')
            (notes / 'media/Algorithm/a(b).png').write_bytes(b'original-image')
            (notes / 'media/Algorithm/ignore.pyc').write_bytes(b'bytecode')
            (notes / 'README.md').write_text('# 不发布根索引')
            migration = root / 'migration.json'
            migration.write_text(json.dumps({'legacy_urls': {'math/note.md': ['/notes/algorithm/old.html']}}))
            with patch.multiple(sync, NOTES_DIR=notes, CONTENT_DIR=root/'content',
                                STATIC_DIR=root/'static', STATIC_SEARCH_INDEX=root/'index.json',
                                MIGRATION_FILE=migration, DATE_CACHE_FILE=root/"dates.json"):
                sync.main()
                body = (root / 'content/math/note.md').read_text()
                self.assertIn('"数学基础"', body)
                self.assertIn('"/notes/algorithm/old.html"', body)
                self.assertIn('path: "math/note.md"', body)
                self.assertEqual((root/'static/media/Algorithm/a(b).png').read_bytes(), b'original-image')
                self.assertFalse((root/'static/media/Algorithm/ignore.pyc').exists())
                self.assertEqual(len(json.loads((root/'index.json').read_text())), 1)

    def test_empty_notes_does_not_delete_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            notes = root/'notes';notes.mkdir()
            output = root/'content';output.mkdir()
            (output/'keep.md').write_text('keep')
            with patch.multiple(sync, NOTES_DIR=notes, CONTENT_DIR=output):
                with self.assertRaises(SystemExit):sync.main()
                self.assertEqual((output/'keep.md').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
