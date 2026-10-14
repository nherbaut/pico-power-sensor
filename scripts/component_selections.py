"""Apply explicit prototype selections; selection is not fabrication approval."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def references(expression):
    result = []
    for group in expression.split(';'):
        group = group.strip()
        if '-' not in group:
            result.append(group)
            continue
        match = re.fullmatch(r'([A-Z_]+)(\d+)-([A-Z_]+)(\d+)', group)
        if not match or match[1] != match[3] or int(match[2]) > int(match[4]):
            raise ValueError('Invalid reference range: ' + group)
        result.extend(f'{match[1]}{n}' for n in range(int(match[2]), int(match[4])+1))
    return result


def selections(board):
    with (ROOT / 'hardware/passive-proposals.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        if row['board'] != board or not row['status'].startswith('selected for prototype'):
            continue
        for ref in references(row['references']):
            if ref in result:
                raise ValueError('Duplicate selection: ' + ref)
            result[ref] = row
    return result


def apply_selections(board, parts):
    by_ref = {p['ref']: p for p in parts}
    for ref, row in selections(board).items():
        p = by_ref[ref]
        p.update(mpn=row['manufacturer_reference'], manufacturer=row['manufacturer'],
                 documentation_url=row['documentation_url'],
                 selection_status='selected for prototype; release reviews pending')
        if row['manufacturer'] == 'Murata':
            p['footprint'] = 'C_0805_Murata'
            p['footprint_source'] = 'Murata GRM21 reflow land pattern: gap 1.2; pads 0.6 x 1.25 mm'
        if row['manufacturer_reference'].startswith('TNPW'):
            p['footprint'] = 'R_0805_TNPW'
            p['footprint_source'] = 'Vishay 28950 IPC reflow 0805: gap 1.0; pads 0.90 x 1.45 mm'
        if board == 'interposer' and ref == 'C1':
            p['footprint'] = 'C_0805_KEMET'
            p['footprint_source'] = 'KEM_C1003_C0G_SMD 2025-02-20 p12 table 3 density B: centres +/-0.90; pads 1.15 x 1.45; courtyard 3.50 x 2.00 mm'
        if board == 'interposer' and ref == 'C2':
            p['value'] = '100nF X7R 100V'
        if board == 'carrier' and ref == 'C_SDBULK':
            p['value'] = '22uF X5R 16V'


def constraints():
    return dict(ambient_C=[10, 40], prototype_budget_EUR=[100, 200],
                budget_excludes='owned equipment',
                assembly='factory SMT; manual through-hole connectors',
                fault_policy='operator abort and supply power cycle; not a hardware fault latch',
                fablab_equipment='user confirmed access; no measurements performed')
