#!/usr/bin/python3
"""Apply the Infineon BSC010N04LS6 land pattern to Q1 and Q2 of the routed interposer.

Targeted edit of the saved board: pads, nets, tracks and zones outside Q1/Q2 are untouched.
Also refreshes the local SuperSO8_Draft library snapshot. Run native ERC/DRC afterwards.
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
from footprint_corrections import mosfet

BOARD = ROOT / 'hardware/pcb/interposer/interposer.kicad_pcb'
LIBRARY = ROOT / 'hardware/pcb/interposer/PicoPower.pretty'


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    done = []
    for fp in board.GetFootprints():
        if fp.GetReference() in ('Q1', 'Q2'):
            mosfet(fp)
            done.append(fp.GetReference())
    if done != ['Q1', 'Q2'] and sorted(done) != ['Q1', 'Q2']:
        raise SystemExit('Q1 and Q2 not both found')
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD), board)
    snapshot = pcbnew.FootprintLoad(str(LIBRARY), 'SuperSO8_Draft')
    mosfet(snapshot)
    pcbnew.FootprintSave(str(LIBRARY), snapshot)
    print('Applied the Infineon land pattern to', ' and '.join(sorted(done)), '; run native ERC/DRC.')


if __name__ == '__main__':
    main()
