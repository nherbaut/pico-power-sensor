#!/usr/bin/env python3
"""Check local href/src destinations, including GitHub Pages subpaths."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'public'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ('href', 'src') and value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', required=True)
    args = parser.parse_args()
    prefix = urlsplit(args.base_url).path.rstrip('/')
    errors = []
    pages = list(ROOT.rglob('*.html'))
    if not pages:
        raise SystemExit('No HTML pages found; build the site first.')
    for page in pages:
        links = Links()
        links.feed(page.read_text())
        for link in links.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = unquote(parsed.path)
            if path.startswith('/'):
                if prefix and not (path == prefix or path.startswith(prefix + '/')):
                    errors.append(f'{page.relative_to(ROOT)}: missing base path in {link}')
                    continue
                target = ROOT / path[len(prefix):].lstrip('/')
            else:
                target = page.parent / path
            if target.is_dir():
                target = target / 'index.html'
            if not target.exists():
                errors.append(f'{page.relative_to(ROOT)}: missing {link}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked internal links and assets in {len(pages)} HTML pages.')


if __name__ == '__main__':
    main()
