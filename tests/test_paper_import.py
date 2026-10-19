"""Optional importer checks: run using the paper-import virtual environment."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    import import_paper_readings as importer
except ImportError:
    importer = None


@unittest.skipIf(importer is None, 'requires requirements-paper-import.txt')
class PaperImportTests(unittest.TestCase):
    def test_math_compatibility_retains_meaning(self):
        self.assertEqual(importer.compatible_math(r'\textsc{Stop}'), r'\text{Stop}')
        self.assertEqual(importer.compatible_math(r'H_\max'), r'H_{\max}')
        self.assertEqual(importer.compatible_math(r'{I_i\}_{i=1}^{N}'), r'\{I_i\}_{i=1}^{N}')
        self.assertEqual(importer.compatible_math(r'\max_i x_i'), r'\max_i x_i')

    def test_conversion_keeps_math_tables_sources_and_local_images(self):
        article = {'title': 'Example (arXiv 2026)',
                   'url': 'https://example.test/paper_reading/2601.12345_Example/technical_report.html'}
        source = ('<section class="markdown-section"><h1 id="example">Original heading</h1>'
                  '<p>' + '研究内容与实验说明。' * 40 + '</p>'
                  '<h2 id="method">Method</h2><span class="arithmatex">\\(x_1 + y\\)</span>'
                  '<div class="arithmatex">\\[a &lt; b\n= c\\]</div>'
                  '<table><tr><th>Formula</th></tr><tr><td>'
                  '<span class="arithmatex">\\(\\lvert x \\rvert\\)</span>'
                  '</td></tr></table><img src="assets/a.png" onclick="bad()">'
                  '<a href="paper_cn.pdf">PDF</a><script>bad()</script></section>')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.multiple(importer, NOTES=root/'notes', CACHE=root/'cache'):
                with patch.object(importer, 'fetch', side_effect=lambda url, cache:
                                  source.encode() if url.endswith('.html') else b'image-bytes'):
                    result = importer.import_article(article, {})
            text = (root/'notes'/result['path']).read_text()
            self.assertIn(r'\(x_1 + y\)', text)
            self.assertIn('<div class="paper-math">\\[a &lt; b\n= c\\]</div>', text)
            self.assertIn(r'\(\lvert x \rvert\)', text)
            self.assertIn('<table>', text)
            self.assertIn('{#method}', text)
            self.assertIn('原文链接', text)
            self.assertIn('https://example.test/paper_reading/2601.12345_Example/paper_cn.pdf', text)
            self.assertNotIn('PLACEHOLDER', text)
            self.assertNotIn('bad()', text)
            self.assertEqual(result['math_expressions'], 3)
            self.assertTrue((root/'notes'/result['images'][0]['path']).exists())

    def test_unrelated_note_is_not_overwritten(self):
        article = {'title': 'Example (arXiv 2026)', 'url': 'https://example.test/2601.12345/a.html'}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root/'papers'/f'{importer.article_slug(article)}.md'
            target.parent.mkdir()
            target.write_text('An existing personal note')
            with patch.object(importer, 'NOTES', root):
                with self.assertRaises(ValueError):
                    importer.import_article(article, {})
            self.assertEqual(target.read_text(), 'An existing personal note')


if __name__ == '__main__':
    unittest.main()
