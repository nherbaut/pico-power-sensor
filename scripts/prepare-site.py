#!/usr/bin/env python3
"""Prepare Hugo inputs from repository sources without changing those sources."""
import csv
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from render_hardware_images import BOARDS, verify_board_images

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.build/site'
FOLDERS = ('hardware', 'docs', 'nodes', 'tests', 'src', 'config')
DATASETS = {
    'bom': 'Reference bill of materials',
    'optional-bom': 'Optional components',
    'procurement': 'Purchases and receipts',
    'inventory': 'Hardware inventory',
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def content_path(source):
    if source.name == 'README.md':
        return source.parent / '_index.md'
    return source


def route(source):
    target = content_path(source)
    if target.name == '_index.md':
        return '/' if target.parent == Path('.') else '/' + target.parent.as_posix() + '/'
    return '/' + target.with_suffix('').as_posix().lower() + '/'


def hardware_table_links(text, components):
    """Link manufacturer/part and supplier cells in source Markdown tables."""
    headers = []
    fenced = False
    lines = []
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith('```'):
            fenced = not fenced
        if fenced or not line.startswith('|'):
            headers = []
            lines.append(line)
            continue
        cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
        if any(cell.lower() in ('supplier / reference', 'reference', 'fournisseur', 'supplier') for cell in cells):
            headers = [cell.lower() for cell in cells]
        elif headers and len(headers) == len(cells):
            supplier_columns = [i for i, header in enumerate(headers)
                                if header in ('supplier / reference', 'reference', 'fournisseur', 'supplier')]
            for i in supplier_columns:
                match = re.fullmatch(r'(Farnell|RS) (\d+)', cells[i])
                if not match:
                    continue
                component = next((row for row in components.values()
                                  if row['supplier'] == match[1] and row['supplier_reference'] == match[2]), None)
                if not component:
                    continue
                if component['product_url'].startswith('https://'):
                    cells[i] = f'[{cells[i]}]({component["product_url"]})'
                for j, header in enumerate(headers):
                    if header in ('part', 'fabricant', 'manufacturer') and '[' not in cells[j] and component['documentation_url'].startswith('https://'):
                        cells[j] = f'[{cells[j]}]({component["documentation_url"]})'
                line = '| ' + ' | '.join(cells) + ' |\n'
        lines.append(line)
    return ''.join(lines)


def prepare():
    for board in BOARDS:
        verify_board_images(board)
    # Only this generated subtree is replaced, never the source documents.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    sources = [Path('README.md')]
    for folder in FOLDERS:
        sources.extend(sorted(p.relative_to(ROOT) for p in (ROOT / folder).rglob('*.md')
                              if 'local' not in p.parts and not p.name.startswith('secrets.')))
    routes = {source: route(source) for source in sources}
    datasets = {}
    for name, title in DATASETS.items():
        source = Path('hardware') / (name + '.csv')
        with (ROOT / source).open(encoding='utf-8', newline='') as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fields = reader.fieldnames
        if not fields or any(None in row or None in row.values() for row in rows):
            raise ValueError(f'Invalid CSV: {source}')
        datasets[name] = {'fields': fields, 'rows': rows}
        routes[source] = '/hardware/' + name + '/'
        write(OUTPUT / 'content/hardware' / (name + '.md'),
              '+++\ntitle = ' + json.dumps(title, ensure_ascii=False) +
              '\ndataset = ' + json.dumps(name) + '\n+++\n')
        destination = OUTPUT / 'static/data' / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, destination)
    write(OUTPUT / 'data/hardware.json', json.dumps(datasets, ensure_ascii=False, indent=2))
    components = {row['component_id']: row for name in ('bom', 'optional-bom')
                  for row in datasets[name]['rows']}
    write(OUTPUT / 'data/components.json', json.dumps(components, ensure_ascii=False, indent=2))

    def link(source, match):
        destination = match.group(2)
        # Markdown permits a quoted title after a link/image destination.
        # Resolve only the URL, then preserve the title for Hugo's caption hook.
        title = ''
        titled = re.fullmatch(r'''(\S+)(\s+"(?:[^"\\]|\\.)*"|\s+'(?:[^'\\]|\\.)*')''', destination)
        if titled:
            destination, title = titled.groups()
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        target = ((ROOT / source.parent) / parsed.path).resolve()
        try:
            relative = target.relative_to(ROOT)
        except ValueError:
            raise ValueError(f'Link outside repository: {source} -> {destination}')
        if 'local' in relative.parts or target.name.startswith(('secrets.', '.env')):
            raise ValueError(f'Link to excluded local configuration: {source} -> {destination}')
        if relative not in routes and target.is_dir():
            relative = relative / 'README.md'
        if relative in routes:
            new = routes[relative]
        elif target.is_file() and target.suffix.lower() in ('.csv', '.json', '.png', '.jpg', '.jpeg', '.svg', '.pdf', '.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_mod', '.kicad_sym', '.zip', '.txt', '.step', '.rpt'):
            new = '/data/' + relative.as_posix()
            output = OUTPUT / 'static/data' / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target, output)
        else:
            raise ValueError(f'Unpublished link: {source} -> {destination}')
        return match.group(1) + '(' + urlunsplit(('', '', new, parsed.query, parsed.fragment)) + title + ')'

    for source in sources:
        text = (ROOT / source).read_text(encoding='utf-8')
        text = hardware_table_links(text, components)
        heading = re.search(r'^# (.+)$', text, re.MULTILINE)
        title = heading.group(1) if heading else source.stem
        if heading:
            text = text[:heading.start()] + text[heading.end():]
        text = re.sub(r'(\[[^\]]*\])\(([^)]+)\)', lambda m: link(source, m), text)
        metadata = '+++\ntitle = ' + json.dumps(title, ensure_ascii=False)
        metadata += '\nsource = ' + json.dumps(source.as_posix()) + '\n+++\n'
        write(OUTPUT / 'content' / content_path(source), metadata + text)
    print(f'Prepared {len(sources)} documents and {len(datasets)} CSV tables for Hugo.')


if __name__ == '__main__':
    prepare()
