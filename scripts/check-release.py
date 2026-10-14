#!/usr/bin/env python3
"""Check recorded release evidence; never approve, fabricate or energize hardware."""
import argparse
import csv
import hashlib
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    'interposer': {
        'fabrication': {'source', 'erc', 'drc', 'bom', 'footprints', 'power-budget',
                        'protection', 'routing', 'mechanics', 'stackup', 'package',
                        'schematic-review', 'rule-map'},
        'connection': {'continuity', 'faults', 'inrush', 'load', 'buffer', 'metrology'},
    },
    'carrier': {
        'fabrication': {'source', 'erc', 'drc', 'bom', 'footprints', 'sense-ic',
                        'mechanics', 'sd-power', 'stackup', 'package',
                        'schematic-review', 'rule-map'},
        'connection': {'continuity', 'supplies', 'interfaces', 'storage'},
    },
}
FIELDS = {'board', 'gate', 'check_id', 'category', 'requirement', 'status',
          'evidence', 'remaining', 'reviewer', 'reviewed_on', 'design_sha256'}


def design_hash(root, board):
    folder = root / 'hardware/pcb' / board
    sources = {folder / name for name in (f'{board}.kicad_pcb', f'{board}.kicad_sch',
               f'{board}.kicad_pro', 'circuit.json', 'board-bom.csv', 'fp-lib-table', 'sym-lib-table')}
    sources.update(folder.rglob('*.kicad_mod'))
    sources.update(folder.glob('*.kicad_sym'))
    sources.update(root / 'hardware' / name for name in ('bom.csv', 'passive-proposals.csv'))
    digest = hashlib.sha256()
    for path in sorted(sources):
        digest.update(path.relative_to(root).as_posix().encode() + b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def blockers(rows, board, gate, fingerprint, root=ROOT):
    errors = []
    gates = ('fabrication', 'connection') if gate == 'connection' else ('fabrication',)
    for stage in gates:
        selected = [r for r in rows if r['board'] == board and r['gate'] == stage]
        ids = [r['check_id'] for r in selected]
        expected = REQUIRED[board][stage]
        if len(ids) != len(set(ids)):
            errors.append(f'{stage}: duplicate checklist IDs')
        for missing in sorted(expected - set(ids)):
            errors.append(f'{stage}/{missing}: missing required check')
        for row in selected:
            label = f"{stage}/{row['check_id']}"
            if row['check_id'] not in expected:
                errors.append(f'{label}: unknown check ID')
            if row['status'] != 'passed':
                errors.append(f"{label}: {row['status']} — {row['remaining'] or row['requirement']}")
                continue
            if row['design_sha256'] != fingerprint:
                errors.append(f'{label}: evidence is for a different design snapshot')
            if not all(row.get(k, '').strip() for k in ('evidence', 'reviewer', 'reviewed_on')):
                errors.append(f'{label}: evidence, reviewer and date are required')
            if row.get('remaining', '').strip():
                errors.append(f'{label}: unresolved work remains')
            for evidence in row['evidence'].split(';'):
                evidence = evidence.strip()
                if not evidence:
                    continue
                parsed = urlsplit(evidence)
                if parsed.scheme in ('https', 'http') and parsed.netloc:
                    continue
                target = (root / parsed.path).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    errors.append(f'{label}: missing or invalid evidence file {evidence}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', choices=REQUIRED, required=True)
    parser.add_argument('--gate', choices=('fabrication', 'connection'), required=True)
    args = parser.parse_args()
    with (ROOT / 'hardware/release-checklist.csv').open(newline='') as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or ()) != FIELDS:
            raise SystemExit('Invalid release checklist columns')
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise SystemExit('Malformed release checklist row')
    for row in rows:
        if row['board'] not in REQUIRED or row['gate'] not in REQUIRED[row['board']]:
            raise SystemExit('Unknown board or gate in checklist')
        if row['status'] not in ('passed', 'pending', 'partial', 'failed'):
            raise SystemExit('Unknown checklist status; exclusions are not supported')
    fingerprint = design_hash(ROOT, args.board)
    errors = blockers(rows, args.board, args.gate, fingerprint)
    print(f'{args.board} {args.gate}: design {fingerprint}')
    if errors:
        print('NOT RELEASED')
        for error in errors:
            print(f'- {error}')
        raise SystemExit(1)
    print('Recorded checklist evidence is complete. This command does not authorize ordering or power-up.')


if __name__ == '__main__':
    main()
