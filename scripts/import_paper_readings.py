#!/usr/bin/env python3
"""Import the explicitly authorized article list; retain sources and local images.

Run with the optional dependencies in requirements-paper-import.txt. Ordinary
blog builds do not need these dependencies or access to the original website.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from html import escape
import json
from pathlib import Path
import re
import time
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, NavigableString
from markdownify import MarkdownConverter

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / 'notes'
MANIFEST = ROOT / 'data/paper-reading-sources.json'
CACHE = ROOT / 'resources/paper-import-cache'


def fetch(url: str, cache: Path) -> bytes:
    if cache.exists():
        return cache.read_bytes()
    error = None
    for attempt in range(3):
        try:
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (authorized personal blog migration)'})
            with urlopen(request, timeout=40) as response:
                content = response.read()
            cache.parent.mkdir(parents=True, exist_ok=True)
            temporary = cache.with_suffix(cache.suffix + '.partial')
            temporary.write_bytes(content)
            temporary.replace(cache)
            return content
        except Exception as exc:
            error = exc
            time.sleep(attempt + 1)
    raise RuntimeError(f'Unable to fetch {url}: {error}')


def canonical(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, unquote(parts.path), '', ''))


def article_slug(article: dict) -> str:
    name = article['title'].split(' (')[0].strip()
    name = re.sub(r'[^\w.+-]+', '-', name, flags=re.UNICODE).strip('-')
    identifier = re.search(r'\d{4}\.\d{4,5}(?:v\d+)?', article['url'])
    prefix = identifier.group() if identifier else 'CVPR2026'
    return f'{prefix}-{name}'


def compatible_math(value: str) -> str:
    """Normalize six source expressions for the blog's existing KaTeX renderer."""
    value = value.replace(r'\textsc{', r'\text{')
    value = re.sub(r'_\\max\b', lambda _: r'_{\max}', value)
    value = re.sub(r'(?<!\\)\{I_i\\\}_\{i=1\}\^\{N\}',
                   lambda _: r'\{I_i\}_{i=1}^{N}', value)
    return value


class ReportConverter(MarkdownConverter):
    def convert_hN(self, n, el, text, parent_tags):
        heading = super().convert_hN(n, el, text, parent_tags)
        if el.get('id') and '_inline' not in parent_tags:
            heading = heading.rstrip() + ' {#' + el['id'] + '}\n\n'
        return heading


def import_article(article: dict, urls: dict[str, str]) -> dict:
    slug = article_slug(article)
    destination = NOTES / 'papers' / f'{slug}.md'
    marker = f'<!-- paper-source: {article["url"]} -->'
    if destination.exists() and marker not in destination.read_text():
        raise ValueError(f'Refusing to overwrite an unrelated note: {destination}')
    source = fetch(article['url'], CACHE / f'{slug}.html')
    soup = BeautifulSoup(source.decode('utf-8'), 'html.parser')
    body = soup.select_one('.markdown-section')
    if not body or not body.find('h1') or len(body.get_text(strip=True)) < 200:
        raise ValueError(f'Missing article body or password screen: {article["url"]}')
    for element in body.select('script,style,button,iframe,form,input'):
        element.decompose()
    for element in body.find_all():
        for attribute in list(element.attrs):
            if attribute.lower().startswith('on') or attribute in {'srcset', 'data-srcset'}:
                del element[attribute]
    # The Markdown title supplies the article heading. Preserve its old anchor.
    heading = body.find('h1')
    original_title = heading.get_text(' ', strip=True)
    old_anchor = heading.get('id')
    if old_anchor:
        anchor = soup.new_tag('span', id=old_anchor)
        heading.replace_with(anchor)
    else:
        heading.decompose()

    images = []
    for index, image in enumerate(body.find_all('img')):
        value = image.get('data-src') or image.get('src')
        if not value or value.startswith('data:'):
            continue
        url = urljoin(article['url'], value)
        if urlsplit(url).scheme not in {'https', 'http'}:
            raise ValueError(f'Unexpected image URL: {url}')
        filename = unquote(urlsplit(url).path.rsplit('/', 1)[-1]) or f'figure-{index + 1}.png'
        filename = re.sub(r'[^\w.+-]', '_', filename)[:120]
        filename = hashlib.sha256(url.encode()).hexdigest()[:10] + '-' + filename
        target = NOTES / 'media/papers' / slug / filename
        data = fetch(url, CACHE / 'images' / slug / filename)
        if not data:
            raise ValueError(f'Empty image: {url}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        image['src'] = f'../media/papers/{slug}/{filename}'
        image['alt'] = image.get('alt') or f'{article["title"]} 图 {index + 1}'
        image.attrs.pop('data-src', None)
        # Avoid carrying fixed-size source layout into the responsive blog.
        image.attrs.pop('width', None)
        image.attrs.pop('height', None)
        image.attrs.pop('style', None)
        images.append({'source': url, 'path': target.relative_to(NOTES).as_posix(),
                       'sha256': hashlib.sha256(data).hexdigest()})

    for link in body.find_all('a', href=True):
        href = link['href']
        if href.startswith('#'):
            continue
        absolute = urljoin(article['url'], href)
        parts = urlsplit(absolute)
        if parts.scheme not in {'http', 'https', 'mailto'}:
            link.unwrap()
            continue
        target_slug = urls.get(canonical(absolute))
        if target_slug:
            link['href'] = f'{target_slug}.md' + (f'#{parts.fragment}' if parts.fragment else '')
        else:
            # PDF/translation links remain explicit original links, not broken
            # relative URLs or additional imported articles.
            link['href'] = absolute

    replacements = {}
    math_count = 0
    math_fixes = []
    for element in list(body.select('.arithmatex')):
        math = element.get_text().strip()
        normalized = compatible_math(math)
        if normalized != math:
            math_fixes.append({'original': math, 'normalized': normalized})
        math = normalized
        if math.startswith(r'\[') and math.endswith(r'\]'):
            value = '\n\n<div class="paper-math">\\[' + escape(math[2:-2].strip()) + '\\]</div>\n\n'
        elif math.startswith(r'\(') and math.endswith(r'\)'):
            value = '<span class="paper-math">\\(' + escape(math[2:-2]) + '\\)</span>'
        else:
            value = math
        token = f'PAPERMATHPLACEHOLDER{len(replacements)}END'
        replacements[token] = value
        element.replace_with(NavigableString(token))
        math_count += 1

    # HTML tables preserve complex cells and avoid breaking LaTeX vertical bars.
    for table in list(body.find_all('table')):
        token = f'PAPERTABLEPLACEHOLDER{len(replacements)}END'
        for tag in [table, *table.find_all()]:
            for attribute in list(tag.attrs):
                if attribute not in {'src', 'href', 'alt', 'id', 'colspan', 'rowspan'}:
                    del tag[attribute]
        replacements[token] = '\n\n' + str(table) + '\n\n'
        table.replace_with(NavigableString(token))

    converted = ReportConverter(heading_style='ATX', bullets='-', code_language='',
                                escape_underscores=False).convert(str(body)).strip()
    # Tables may contain math tokens: restore outer tables before inner formulas.
    for token, value in reversed(list(replacements.items())):
        converted = converted.replace(token, value)
    if re.search(r'PAPER(?:MATH|TABLE)PLACEHOLDER\d+END', converted):
        raise ValueError(f'Unrestored conversion token: {article["url"]}')
    text = (f'# {article["title"]}\n\n{marker}\n\n'
            f'> 原文链接：[{article["title"]}]({article["url"]})\n\n{converted}\n')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
    return {**article, 'original_title': original_title,
            'path': destination.relative_to(NOTES).as_posix(),
            'images': images, 'math_expressions': math_count,
            'math_compatibility_fixes': math_fixes,
            'source_sha256': hashlib.sha256(source).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get('authorized_by_user') is not True:
        raise SystemExit('This import requires explicit authorization for the source content.')
    articles = manifest['articles']
    if len(articles) != 98 or len({a['url'] for a in articles}) != 98:
        raise SystemExit('Expected exactly 98 distinct source articles.')
    slugs = [article_slug(a) for a in articles]
    if len(set(slugs)) != len(slugs):
        raise SystemExit('Destination filenames collide.')
    urls = {canonical(a['url']): article_slug(a) for a in articles}
    imported = {}
    errors = []
    with ThreadPoolExecutor(max_workers=min(max(args.workers, 1), 4)) as executor:
        jobs = {executor.submit(import_article, a, urls): a for a in articles}
        for job in as_completed(jobs):
            article = jobs[job]
            try:
                imported[article['url']] = job.result()
                if len(imported) % 10 == 0:
                    print(f'Imported {len(imported)}/98', flush=True)
            except Exception as exc:
                errors.append({'url': article['url'], 'error': str(exc)})
                print(f'Failed: {article["title"]}: {exc}', flush=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE/'errors.json').write_text(json.dumps(errors, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(f'{len(errors)} articles failed; rerun to resume from cache.')
    manifest['articles'] = [imported[a['url']] for a in articles]
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    readme = NOTES/'README.md'
    text = readme.read_text()
    start = text.index('### 论文阅读')
    end = text.index('## Resource', start)
    index = ['### 论文阅读', ''] + [f'- [{a["title"]}](<{a["path"]}>)' for a in manifest['articles']]
    readme.write_text(text[:start]+'\n'.join(index)+'\n\n'+text[end:])
    print(f'Complete: 98 articles, {sum(len(a["images"]) for a in imported.values())} images, '
          f'{sum(a["math_expressions"] for a in imported.values())} formulas', flush=True)


if __name__ == '__main__':
    main()
