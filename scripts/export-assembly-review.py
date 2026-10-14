#!/usr/bin/python3
"""Export local planning data only; no supplier upload or fabrication outputs."""
import csv
import json
from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]


def rows_for(name, circuit, board):
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    rows = []
    for p in circuit['parts']:
        if not p.get('on_board', True) or not p.get('in_bom', True):
            continue
        ref = p['ref']; fp = footprints[ref]
        if ref.startswith('TP'):
            method, quantity = 'bare PCB feature', 0
        elif ref == 'J_PICO':
            method, quantity = 'owned socketed module; do not order or solder to PCB', 0
        elif any(pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for pad in fp.Pads()):
            method, quantity = 'manual through-hole', 1
        else:
            method, quantity = 'factory SMT', 1
        rows.append(dict(board=name, reference=ref, manufacturer_reference=p['mpn'],
                         value=p['value'], quantity=quantity, assembly=method,
                         documentation_url=p['documentation_url'],
                         status='planning only; technical review and supplier availability pending'))
    if name == 'carrier':
        rows.append(dict(board=name, reference='J_PICO socket strips',
                         manufacturer_reference='SSW-120-01-G-S', value='1x20 female socket',
                         quantity=2, assembly='manual through-hole; replaces module in purchasing list',
                         documentation_url='https://www.samtec.com/products/ssw-120-01-g-s',
                         status='planning only; drawing and physical fit pending'))
    if name == 'interposer':
        rows.append(dict(board=name, reference='F1 cartridge', manufacturer_reference='021706.3MXP',
                         value='6.3 A fast 5x20 cartridge', quantity=1,
                         assembly='manual insertion after inspection',
                         documentation_url='https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe',
                         status='retained provisional part; complete voltage-drop budget unresolved'))
    return rows


def main():
    rows = []
    for name in ('interposer', 'carrier'):
        folder = ROOT/'hardware/pcb'/name
        data = json.loads((folder/'circuit.json').read_text())
        board = pcbnew.LoadBoard(str(folder/(name+'.kicad_pcb')))
        rows += rows_for(name, data, board)
    with (ROOT/'hardware/assembly-review.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    print(f'Exported {len(rows)} assembly planning rows; not an order-ready package.')


if __name__ == '__main__':
    main()
