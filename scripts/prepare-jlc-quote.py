#!/usr/bin/python3
"""Prepare a quote-only JLCPCB package for each board: Gerbers and drills, BOM and placement file.

This is NOT a fabrication release. The release checklist is still open, so every output is
labelled "quote only" and nothing is uploaded or ordered from here. Gerber, drill and position
files come from kicad-cli; the BOM and CPL follow JLCPCB's column layout. The LCSC part column
is left empty on purpose: the owner maps each part in JLCPCB's tool. Placement rotations are
KiCad's and are not corrected for JLCPCB's package conventions, so check them in JLCPCB's viewer.
"""
import argparse
import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ('interposer', 'carrier')
GERBER_LAYERS = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'
# Parts that are specialised or unusual enough to check against JLCPCB's catalogue first.
CHECK_FIRST = {
    'INA229AIDGSR': 'power monitor; no common substitute',
    'LTC4367IMS8#PBF': 'protection controller; the -1 variants restart much faster, do not substitute',
    'BSC010N04LS6ATMA1': 'power MOSFET; 1 mOhm class, drives the voltage-drop budget',
    'SN74AXC4T245PWR': 'power-off tolerant level shifter; substitutes may not isolate when a rail is off',
    'TLV75533PDBVR': 'SD card regulator; thermal limit already tight',
    'WSK25125L000DEA': '5 mOhm 4-terminal shunt; sets the measurement scale',
    '693072010801': 'hinged microSD socket; pad pattern is specific to this part',
    'C0805C123J5GACTU': 'C0G 12 nF; a different dielectric changes the gate slew',
}
PRECISION = ('TNPW',)


def env():
    result = os.environ.copy()
    for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
        target = ROOT / '.build/kicad' / name
        target.mkdir(parents=True, exist_ok=True)
        result[key] = str(target)
    return result


def run(*args):
    subprocess.run([str(a) for a in args], check=True, env=env(), capture_output=True, text=True)


def smt_rows(board):
    """References placed by the assembler, from the assembly planning list."""
    with (ROOT / 'hardware/assembly-review.csv').open(newline='') as handle:
        rows = [r for r in csv.DictReader(handle) if r['board'] == board and r['assembly'] == 'factory SMT']
    return {r['reference']: r for r in rows}


def part_details(board):
    import json
    data = json.loads((ROOT / f'hardware/pcb/{board}/circuit.json').read_text())
    return {p['ref']: p for p in data['parts']}


def bom_models():
    with (ROOT / 'hardware/bom.csv').open(newline='') as handle:
        return {r['manufacturer_reference']: r for r in csv.DictReader(handle) if r['manufacturer_reference']}


def selections(board):
    """Owner-chosen JLCPCB parts by reference; candidates are listed but never fill the BOM."""
    path = ROOT / 'hardware/jlcpcb-selection.csv'
    chosen, candidates = {}, {}
    if path.exists():
        with path.open(newline='') as handle:
            for row in csv.DictReader(handle):
                if row['board'] != board:
                    continue
                target = chosen if row['status'].startswith('chosen') else candidates
                for ref in row['references'].split(';'):
                    target[ref] = row
    return chosen, candidates


def jlc_bom(board, refs, parts):
    """One BOM line per manufacturer reference and footprint; Comment is the value when all agree."""
    groups = {}
    for ref in sorted(refs, key=natural):
        part = parts[ref]
        groups.setdefault((part['mpn'], part['footprint']), []).append(ref)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    lines = {}
    chosen, _ = selections(board)
    for (mpn, footprint), designators in groups.items():
        values = {parts[r]['value'] for r in designators}
        comment = values.pop() if len(values) == 1 else mpn
        lines[(comment, footprint, mpn)] = designators
        picks = {chosen[r]['lcsc_part'] for r in designators if r in chosen}
        lcsc = picks.pop() if len(picks) == 1 and all(r in chosen for r in designators) else ''
        writer.writerow([comment, ','.join(designators), footprint, lcsc])
    return out.getvalue(), lines


def natural(ref):
    digits = ''.join(c for c in ref if c.isdigit())
    return (ref.rstrip('0123456789'), int(digits) if digits else 0, ref)


def parts_to_map(board, groups, refs, models):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(['designators', 'quantity', 'manufacturer_reference', 'value', 'specification', 'check_first', 'note', 'lcsc_part', 'selection_status', 'selection_differences', 'jlc_rotation_offset_deg'])
    chosen, candidates = selections(board)
    for (value, _footprint, mpn), designators in groups.items():
        model = models.get(mpn, {})
        notes = []
        if mpn in CHECK_FIRST:
            notes.append(CHECK_FIRST[mpn])
        if mpn.startswith(PRECISION):
            notes.append('precision divider resistor (0.1 %, 25 ppm/K): a substitute must match tolerance and drift')
        picked = [chosen[r] for r in designators if r in chosen]
        candidate = [candidates[r] for r in designators if r in candidates]
        row = (picked or candidate or [None])[0]
        lcsc = row['lcsc_part'] if picked and len(picked) == len(designators) else ''
        status = ('chosen: ' if picked else 'candidate: ') + row['selected_mpn'] + ' (' + row['lcsc_part'] + ', ' + row['jlcpcb_type'] + ')' if row else ''
        writer.writerow([','.join(designators), len(designators), mpn, value, model.get('model', ''),
                         'yes' if mpn in CHECK_FIRST else '', '; '.join(notes), lcsc, status,
                         row['differences'] + ' | open: ' + row['open_checks'] if row else '',
                         row.get('jlc_rotation_offset_deg', '') if row else ''])
    return out.getvalue()


def rotation_offsets(board):
    """Degrees added to KiCad's rotation for owner-chosen parts whose JLCPCB footprint is turned."""
    chosen, _ = selections(board)
    return {ref: float(row.get('jlc_rotation_offset_deg') or 0) for ref, row in chosen.items()}


def jlc_cpl(pos_csv, refs, offsets=None):
    reader = csv.DictReader(io.StringIO(pos_csv))
    rows = {}
    for row in reader:
        if row['Ref'] in refs:
            rows[row['Ref']] = row
    missing = sorted(set(refs) - set(rows))
    if missing:
        raise SystemExit('Placement data missing for: ' + ', '.join(missing))
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for ref in sorted(rows, key=natural):
        row = rows[ref]
        rotation = (float(row['Rot']) + (offsets or {}).get(ref, 0.0)) % 360
        writer.writerow([ref, row['PosX'] + 'mm', row['PosY'] + 'mm',
                         'Top' if row['Side'].strip().lower() == 'top' else 'Bottom', f'{rotation:.6f}'])
    return out.getvalue(), rows


def notice(board):
    return (f'QUOTE ONLY - NOT FOR FABRICATION\n\nBoard: {board}\n'
            'These files were generated to obtain a price. The hardware release checklist is not complete '
            '(see hardware/release-checklist.csv), so do not order from them.\n'
            'The LCSC column of the BOM is empty on purpose; map each part in JLCPCB\'s tool.\n'
            'Placement rotations are KiCad\'s, plus any offset recorded in hardware/jlcpcb-selection.csv: '
            'check every part in JLCPCB\'s viewer.\n'
            'If a board has no paste Gerber (the interposer does not), JLCPCB builds the stencil from the copper pads; '
            'confirm that in their review.\n')


def prepare(board, out_root):
    out = out_root / board
    if out.exists():
        shutil.rmtree(out)
    gerbers = out / 'gerbers'
    gerbers.mkdir(parents=True)
    pcb = ROOT / f'hardware/pcb/{board}/{board}.kicad_pcb'
    run('kicad-cli', 'pcb', 'export', 'gerbers', '--output', gerbers, '--layers', GERBER_LAYERS, pcb)
    run('kicad-cli', 'pcb', 'export', 'drill', '--output', str(gerbers) + '/', '--format', 'excellon',
        '--excellon-separate-th', '--excellon-units', 'mm', '--drill-origin', 'absolute', pcb)
    pos = out / 'positions-kicad.csv'
    run('kicad-cli', 'pcb', 'export', 'pos', '--output', pos, '--format', 'csv', '--units', 'mm', '--side', 'both', pcb)
    refs = smt_rows(board)
    parts = part_details(board)
    unknown = sorted(set(refs) - set(parts))
    if unknown:
        raise SystemExit(f'{board}: assembly list references not in the circuit: {unknown}')
    bom_text, groups = jlc_bom(board, refs, parts)
    cpl_text, _ = jlc_cpl(pos.read_text(), refs, rotation_offsets(board))
    (out / f'{board}-BOM-quote-only.csv').write_text(bom_text)
    (out / f'{board}-CPL-quote-only.csv').write_text(cpl_text)
    (out / f'{board}-parts-to-map.csv').write_text(parts_to_map(board, groups, refs, bom_models()))
    (out / 'QUOTE-ONLY.txt').write_text(notice(board))
    archive = out / f'{board}-gerbers-QUOTE-ONLY.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(gerbers.iterdir()):
            if path.suffix.lower() in ('.gbr', '.drl', '.gtl', '.gbl', '.gts', '.gbs', '.gto', '.gbo', '.gtp', '.gbp', '.gm1', '.gko') \
                    or path.name.endswith(('.drl', '.gbrjob')):
                z.write(path, path.name)
        z.writestr('QUOTE-ONLY.txt', notice(board))
    return dict(board=board, placements=len(refs), distinct=len(groups), archive=archive,
                files=sorted(p.name for p in gerbers.iterdir()))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--output', type=Path, default=ROOT / '.build/jlc-quote')
    args = parser.parse_args()
    for board in BOARDS:
        info = prepare(board, args.output)
        print(f"{info['board']}: {info['placements']} placements, {info['distinct']} distinct BOM lines, "
              f"{len(info['files'])} Gerber/drill files, {info['archive']}")
    print('Quote-only package written to', args.output, '- nothing was uploaded or ordered.')


if __name__ == '__main__':
    sys.exit(main())
