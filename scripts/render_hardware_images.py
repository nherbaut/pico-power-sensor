#!/usr/bin/env python3
"""Export accurate PNG drawings from current CAD without changing CAD geometry."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ('interposer', 'carrier')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path):
    header = path.read_bytes()[:24]
    if header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError(f'Invalid PNG: {path}')
    return struct.unpack('>II', header[16:24])


def export_env():
    env = os.environ.copy()
    for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
        target = ROOT / '.build/kicad' / name
        target.mkdir(parents=True, exist_ok=True)
        env[key] = str(target)
    return env


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True, env=export_env())


def crop_preview(source, destination, data):
    """Frame the PCB, excluding off-board USB-cable courtyards in KiCad's plot."""
    tree = ET.parse(source)
    root = tree.getroot()
    ns = 'http://www.w3.org/2000/svg'
    radius = data['mounting_drill_mm'] / 2
    holes = [c for c in root.iter('{'+ns+'}circle') if abs(float(c.get('r', '0'))-radius) < .0001]
    # Other mechanical pads (such as the fuse holder post) can use the same
    # drill. Match the whole mounting pattern, not just the radius/count.
    positions = [h['position_mm'] for h in data['mounting_holes']]
    offsets = set()
    for candidate in holes:
        dx, dy = float(candidate.get('cx'))-positions[0][0], float(candidate.get('cy'))-positions[0][1]
        if all(any(abs(float(c.get('cx'))-hx-dx)<.001 and abs(float(c.get('cy'))-hy-dy)<.001
                   for c in holes) for hx,hy in positions):
            offsets.add((round(dx,4),round(dy,4)))
    if len(offsets) != 1:
        raise ValueError('Cannot uniquely locate the PCB mounting pattern in the plot')
    x, y = offsets.pop()
    width, height = data['width_mm']+1.5, data['height_mm']+1.5
    root.set('viewBox', f'{x-.75} {y-.75} {width} {height}')
    root.set('width', f'{width}mm')
    root.set('height', f'{height}mm')
    root.insert(0, ET.Element('{'+ns+'}rect', {'x': str(x-.75), 'y': str(y-.75),
                    'width': str(width), 'height': str(height), 'fill': '#20262e'}))
    ET.register_namespace('', ns)
    tree.write(destination, encoding='utf-8', xml_declaration=True)


def render_board_images(board, refresh_exports=False):
    out = ROOT / 'hardware/pcb' / board
    temp = ROOT / '.build/hardware-images' / board
    temp.mkdir(parents=True, exist_ok=True)
    pdf, svg = out/'schematic.pdf', out/'layout-front.svg'
    if refresh_exports:
        # Image-only refresh reads present CAD into temporary exports. It never
        # reroutes boards or overwrites saved PDF/SVG/checks/review packages.
        pdf, svg = temp/'schematic.pdf', temp/'layout-front.svg'
        run('kicad-cli', 'sch', 'export', 'pdf', '-o', pdf, out/(board+'.kicad_sch'))
        run('kicad-cli', 'pcb', 'export', 'svg', '--mode-single', '--exclude-drawing-sheet',
            '--fit-page-to-board', '--layers', 'F.Cu,F.Silkscreen,Edge.Cuts', '-o', svg,
            out/(board+'.kicad_pcb'))
    run('pdftoppm', '-f', '1', '-l', '1', '-singlefile', '-scale-to', '8000', '-png', pdf, temp/'schematic')
    (temp/'schematic.png').replace(out/'schematic.png')
    run('pdftoppm', '-f', '1', '-l', '1', '-singlefile', '-scale-to', '2200', '-png', pdf, temp/'schematic-preview')
    (temp/'schematic-preview.png').replace(out/'schematic-preview.png')
    data = json.loads((out/'circuit.json').read_text())['board']
    crop_preview(svg, temp/'front-cropped.svg', data)
    run('rsvg-convert', '-w', '1800', '-o', temp/'layout-front.png', temp/'front-cropped.svg')
    (temp/'layout-front.png').replace(out/'layout-front.png')
    sources = [board+'.kicad_sch', board+'.kicad_pcb', 'circuit.json']
    images = ['schematic.png', 'schematic-preview.png', 'layout-front.png']
    manifest = {'cad_sha256': {name: digest(out/name) for name in sources},
                'png_sha256': {name: digest(out/name) for name in images},
                'dimensions_px': {name: png_dimensions(out/name) for name in images},
                'status': 'CAD export; physical validation not performed'}
    (out/'images.json').write_text(json.dumps(manifest, indent=2)+'\n')
    verify_board_images(board)
    print(f'{board}: schematic PNG (8000px longest side), front PCB PNG (1800px wide).')


def verify_board_images(board):
    """CI needs only Python and committed assets, not native CAD/rendering tools."""
    out = ROOT / 'hardware/pcb' / board
    if not (out/'images.json').is_file():
        raise ValueError(f'{board} PNG exports are missing; run make hardware-images')
    manifest = json.loads((out/'images.json').read_text())
    for name in [board+'.kicad_sch', board+'.kicad_pcb', 'circuit.json']:
        if manifest['cad_sha256'].get(name) != digest(out/name):
            raise ValueError(f'{board} PNGs are stale; run make hardware-images or the board export target')
    for name in ['schematic.png', 'schematic-preview.png', 'layout-front.png']:
        if manifest['png_sha256'].get(name) != digest(out/name):
            raise ValueError(f'{board}/{name} differs from its export manifest; refresh hardware images')
        if list(png_dimensions(out/name)) != manifest['dimensions_px'][name]:
            raise ValueError(f'{board}/{name}: PNG dimensions do not match manifest')
    if max(png_dimensions(out/'schematic.png')) != 8000 or png_dimensions(out/'layout-front.png')[0] != 1800:
        raise ValueError(f'{board}: unexpected drawing resolution')
    if max(png_dimensions(out/'schematic-preview.png')) != 2200:
        raise ValueError(f'{board}: unexpected schematic preview resolution')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', choices=BOARDS)
    args = parser.parse_args()
    for board in [args.board] if args.board else BOARDS:
        render_board_images(board, refresh_exports=True)


if __name__ == '__main__':
    main()
