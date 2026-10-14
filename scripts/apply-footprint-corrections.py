#!/usr/bin/python3
"""Apply the manufacturer land-pattern corrections to the routed interposer.

Targeted edit of the saved board: Q1 and Q2 get the Infineon BSC010N04LS6 copper and U1 the
LTC4367 recommended pads. Tracks, vias, nets, positions and zones outside those footprints
are untouched. The local library snapshots are refreshed too. Run native ERC/DRC afterwards.
Safe to repeat.
"""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
    target = ROOT / '.build/kicad' / name
    target.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(target)
sys.path.insert(0, str(ROOT / 'scripts'))
import pcbnew
from footprint_corrections import mosfet, msop8

BOARD = ROOT / 'hardware/pcb/interposer/interposer.kicad_pcb'
LIBRARY = ROOT / 'hardware/pcb/interposer/PicoPower.pretty'
CORRECTIONS = {'Q1': mosfet, 'Q2': mosfet, 'U1': msop8}
SNAPSHOTS = {'SuperSO8_Draft': mosfet, 'MSOP8_P0.65': msop8}


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    done = []
    for fp in board.GetFootprints():
        if fp.GetReference() in CORRECTIONS:
            CORRECTIONS[fp.GetReference()](fp)
            done.append(fp.GetReference())
    if sorted(done) != sorted(CORRECTIONS):
        raise SystemExit('Missing footprints: ' + ', '.join(sorted(set(CORRECTIONS) - set(done))))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD), board)
    for name, correction in SNAPSHOTS.items():
        snapshot = pcbnew.FootprintLoad(str(LIBRARY), name)
        correction(snapshot)
        pcbnew.FootprintSave(str(LIBRARY), snapshot)
    print('Applied land-pattern corrections to', ', '.join(sorted(done)), '; run native ERC/DRC.')


if __name__ == '__main__':
    main()
