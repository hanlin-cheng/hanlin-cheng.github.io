"""Regression checks against real Hugo output, without a browser dependency."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RenderedPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.links = []
        self.table_wrappers = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'table':
            self.table_wrappers.append(any('table-wrapper' in classes for _, classes in self.stack))
        if tag not in {'img', 'input', 'meta', 'link', 'br', 'hr', 'source', 'wbr', 'area', 'base', 'embed', 'param', 'track', 'col'}:
            self.stack.append((tag, attrs.get('class', '').split()))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.text.append(data)


@unittest.skipUnless(shutil.which('hugo'), 'Hugo Extended is required')
class MarkdownRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Keep build output under the workspace for the local Snap Hugo runtime.
        (ROOT / 'resources').mkdir(exist_ok=True)
        cls.output = tempfile.TemporaryDirectory(prefix='markdown-regression-', dir=ROOT / 'resources')
        cls.addClassCleanup(cls.output.cleanup)
        result = subprocess.run(['hugo', '--destination', cls.output.name], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        cls.html = (Path(cls.output.name) / 'markdown-demo.html').read_text()
        cls.page = RenderedPage()
        cls.page.feed(cls.html)

    def test_h4_is_navigable_in_table_of_contents(self):
        self.assertIn('#四级标题', self.page.links)

    def test_plain_money_shell_and_math_survive_markdown(self):
        text = ''.join(self.page.text)
        for value in ('$10 和 $20', '$30 和 $40', '$HOME、${PATH}、$$', r'\(a_1 + b_2 = c\)'):
            self.assertIn(value, text)
        # A browser then verifies only the explicit delimiters become formulas.
        self.assertNotIn('left: "$"', self.html)
        self.assertNotIn('left: "$$"', self.html)

    def test_native_and_html_attribute_tables_are_scroll_wrapped(self):
        self.assertEqual(self.page.table_wrappers, [True, True])

    def test_code_example_keeps_literal_dollars(self):
        self.assertIn('$10 and $20 are prices;', ''.join(self.page.text))
