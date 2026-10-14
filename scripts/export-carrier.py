#!/usr/bin/python3
"""Export portable carrier review artifacts; never manufacturing outputs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from render_hardware_images import render_board_images

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/pcb/carrier'


def mounting_drawing():
    data=json.loads((OUT/'circuit.json').read_text());board=data['board']
    w,h=board['width_mm'],board['height_mm']
    lines=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 780">',
           '<rect width="900" height="780" fill="white"/>',
           '<g font-family="sans-serif" fill="#182b3a">',
           '<text x="40" y="38" font-size="24">PicoPower carrier — mounting review</text>',
           '<text x="40" y="65" font-size="16">Dimensions in mm. Origin: PCB top-left. Physical fit remains unverified.</text>',
           '<g transform="translate(170 150) scale(8)">',
           f'<rect width="{w}" height="{h}" fill="#f3f7f4" stroke="#234b3b" stroke-width=".2"/>']
    for hole in board['mounting_holes']:
        x,y=hole['position_mm']
        lines += [f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="#b56917" stroke-width=".15" stroke-dasharray=".4 .4"/>',
                  f'<circle cx="{x}" cy="{y}" r="1.35" fill="white" stroke="#182b3a" stroke-width=".15"/>',
                  f'<text x="{x}" y="{y+4.5 if y==4 else y-4.5}" text-anchor="middle" font-size="1.4">{hole["ref"]}</text>']
    x0,y0,x1,y1=board['antenna_keepout_mm']
    lines += [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#ffedd5" stroke="#b56917" stroke-width=".12"/>',
              '<text x="41" y="49" font-size="1.1" text-anchor="middle">ANTENNA</text>',
              '<rect x="30.39" y="2.13" width="21" height="50" fill="none" stroke="#567381" stroke-width=".15"/>',
              '<text x="41" y="28" font-size="1.5" text-anchor="middle">PICO</text>',
              '<rect x="13.15" y="39.25" width="13.7" height="13.7" fill="#e0e7ef" stroke="#567381" stroke-width=".15"/>',
              '<text x="20" y="46" font-size="1.3" text-anchor="middle">microSD</text>',
              '<rect x=".35" y="21.75" width="7.2" height="12.5" fill="#dae6ed" stroke="#567381" stroke-width=".15"/>',
              '<path d="M-11 28 H0" fill="none" stroke="#567381" stroke-width=".25"/>',
              '<text x="-12" y="26" text-anchor="end" font-size="1.5">EVM</text>',
              f'<path d="M0 -3 V-7 H{w} V-3" fill="none" stroke="#182b3a" stroke-width=".12"/>',
              f'<text x="{w/2}" y="-8.5" font-size="1.7" text-anchor="middle">{w}</text>',
              f'<path d="M{w+3} 0 H{w+7} V{h} H{w+3}" fill="none" stroke="#182b3a" stroke-width=".12"/>',
              f'<text x="{w+9}" y="{h/2}" font-size="1.7">{h}</text>',
              '<path d="M4 58 V61 H62 V58" fill="none" stroke="#182b3a" stroke-width=".12"/>',
              '<text x="33" y="63.5" text-anchor="middle" font-size="1.5">58 hole-center spacing</text>',
              '</g>',
              '<text x="40" y="720" font-size="16">H1 (4,4), H2 (62,4), H3 (4,50), H4 (62,50): Ø2.7 NPTH; Ø6 copper keepout.</text>',
              '<text x="40" y="748" font-size="15">Use a shared base with independent EVM supports; confirm its height and mounting locations.</text>',
              '</g></svg>']
    (OUT/'mounting.svg').write_text('\n'.join(lines)+'\n')


def crop_copper_preview(path):
    # KiCad fits to the Pico footprint's USB-cable courtyard, even when that
    # layer is not plotted. Derive the plot offset from the four NPTH holes.
    tree=ET.parse(path);root=tree.getroot();ns='http://www.w3.org/2000/svg'
    holes=[c for c in root.iter('{'+ns+'}circle') if abs(float(c.get('r','0'))-1.35)<.0001]
    if len(holes)!=4:raise ValueError('Cannot identify mounting holes for SVG viewport')
    data=json.loads((OUT/'circuit.json').read_text())['board']
    x=min(float(c.get('cx')) for c in holes)-4
    y=min(float(c.get('cy')) for c in holes)-4
    width,height=data['width_mm']+1.5,data['height_mm']+1.5
    root.set('viewBox',f'{x-.75} {y-.75} {width} {height}')
    root.set('width',f'{width}mm');root.set('height',f'{height}mm')
    root.insert(0,ET.Element('{'+ns+'}rect',{'x':str(x-.75),'y':str(y-.75),
                                         'width':str(width),'height':str(height),'fill':'#20262e'}))
    ET.register_namespace('',ns)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def main():
    spec=importlib.util.spec_from_file_location('carrier_checks',ROOT/'scripts/check-carrier.py')
    checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
    def cli(*args):subprocess.run(['kicad-cli',*map(str,args)],check=True,env=checks.env())
    cli('sch','export','pdf','-o',OUT/'schematic.pdf',OUT/'carrier.kicad_sch')
    cli('sch','export','svg','-o',OUT/'schematic-svg',OUT/'carrier.kicad_sch')
    for side in ['front','back']:
        layers='F.Cu,F.Silkscreen,Edge.Cuts' if side=='front' else 'B.Cu,B.Silkscreen,Edge.Cuts'
        cli('pcb','export','svg','--mode-single','--exclude-drawing-sheet','--fit-page-to-board',
            '--layers',layers,'-o',OUT/f'layout-{side}.svg',OUT/'carrier.kicad_pcb')
        crop_copper_preview(OUT/f'layout-{side}.svg')
    mounting_drawing()
    render_board_images('carrier')
    archive=OUT/'carrier-review.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p!=archive and p.suffix not in ['.kicad_prl','.lck','.bak'] and 'backups' not in p.parts:
                z.write(p,Path('carrier')/p.relative_to(OUT))
    print('Exported carrier review archive, schematic PDF/SVG and copper views. No Gerbers generated.')


if __name__=='__main__':main()
