#!/usr/bin/env python3
"""Update local electronic-protection study; never modify production CAD/BOM."""
import csv
import hashlib
import json
import math
from pathlib import Path
from electronic_protection_analysis import analyze

ROOT = Path(__file__).resolve().parents[1]


def validate_copper(copper, board_sha256):
    """Reject stale CAD evidence or an inconsistent six-branch loop budget."""
    if copper['source_board_sha256'] != board_sha256:
        raise ValueError('Copper evidence is stale; rerun make copper-screen for the current PCB.')
    branches = copper['branches']
    if len(branches) != 6:
        raise ValueError('The complete copper loop must contain six branches.')
    values = [row['copper_resistance_mohm'] for row in branches]
    total = copper['loop']['copper_resistance_mohm']
    if any(not math.isfinite(value) or value <= 0 for value in values + [total]):
        raise ValueError('Copper resistances must be finite and positive.')
    if not math.isclose(math.fsum(values), total, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError('Copper branch sum disagrees with the reported loop resistance.')


def main():
    copper = json.loads((ROOT/'hardware/review/copper-screen.json').read_text())
    board = ROOT/'hardware/pcb/interposer/interposer.kicad_pcb'
    validate_copper(copper, hashlib.sha256(board.read_bytes()).hexdigest())
    report = analyze(copper['loop']['copper_resistance_mohm'])
    report['source_board_sha256'] = copper['source_board_sha256']
    report['sources'] = [
        dict(url='https://www.ti.com/lit/ds/symlink/ina300.pdf',revision='SBOS613C June 2021',pages='3,5,12,18,32',
             use='pin map; threshold source and offset; NAF; latch; active DGS ordering code'),
        dict(url='https://www.ti.com/lit/ds/symlink/tps25982.pdf',revision='SLVSEI3D May 2026',pages='4,8,9',
             use='5V-compatible variant; on-resistance at 2A; current-limit spread'),
        dict(url='https://www.ti.com/lit/ds/symlink/sn74aup1g17.pdf',revision='SCES579J September 2017',pages='6,7',
             use='buffer logic levels and off leakage'),
        dict(url='https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf',revision='Rev D',pages='4,7',
             use='SHDN falling threshold; slow gate-discharge path'),
        dict(url='https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe',revision='GD July 17 2025',pages='2',
             use='6.3A cold 9.5mOhm and rated-current maximum drop 130mV')]
    folder = ROOT/'hardware/review'
    (folder/'electronic-protection-study.json').write_text(json.dumps(report,indent=2)+'\n')
    with (folder/'copper-loop-budget.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=['net','source_terminal','sink_terminal','reference_resistance_mohm','reference_drop_at_5A_mV','basis'],lineterminator='\n')
        writer.writeheader()
        for row in copper['branches']:
            writer.writerow(dict(net=row['net'],source_terminal=row['terminals'][0],sink_terminal=row['terminals'][1],
                                 reference_resistance_mohm=f"{row['copper_resistance_mohm']:.6f}",
                                 reference_drop_at_5A_mV=f"{row['drop_at_5A_mV']:.6f}",
                                 basis='0.1mm DC raster, 70um/side, ideal parallel terminals; not measured'))
    print('Exported electronic-protection study and six-branch copper budget; main CAD/BOM unchanged.')


if __name__ == '__main__':
    main()
