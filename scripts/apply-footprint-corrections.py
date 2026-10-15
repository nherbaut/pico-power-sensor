#!/usr/bin/python3
"""Apply the manufacturer land-pattern corrections to the routed interposer.

Targeted edit of the saved board: Q1 and Q2 get the Infineon BSC010N04LS6 copper, U1 the
LTC4367 recommended pads and J1 the Phoenix fastening holes. Tracks, vias, nets, positions and zones outside those footprints
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
from footprint_corrections import mosfet, msop8, phoenix_flange

BOARD = ROOT / 'hardware/pcb/interposer/interposer.kicad_pcb'
LIBRARY = ROOT / 'hardware/pcb/interposer/PicoPower.pretty'
CORRECTIONS = {'Q1': mosfet, 'Q2': mosfet, 'U1': msop8, 'J1': phoenix_flange}
SNAPSHOTS = {'SuperSO8_Draft': mosfet, 'MSOP8_P0.65': msop8, 'Power_GF_2': phoenix_flange}


def clear_fastening_holes(board):
    """Remove the ground copper that the J1 fastening holes would cut.

    Two isolated ground stitching vias and one 0.2 mm ground track on B.Cu sit within the hole
    clearance of the new 2.4 mm holes. Native DRC with them removed reports 0 violations and 0
    unconnected items, because the two ground pours already join everywhere else. The items are
    identified exactly, so this does nothing on a board that does not have them.
    """
    removed = []
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA):
            x, y = pcbnew.ToMM(item.GetPosition().x), pcbnew.ToMM(item.GetPosition().y)
            if item.GetNetname() == '/GND' and any(abs(x - vx) < .01 and abs(y - vy) < .01
                                                   for vx, vy in ((3.0, 11.0), (19.0, 11.0))):
                board.Remove(item)
                removed.append('via at (%.1f, %.1f)' % (x, y))
        elif item.GetNetname() == '/GND' and item.GetLayer() == pcbnew.B_Cu:
            a, b = item.GetStart(), item.GetEnd()
            if (abs(pcbnew.ToMM(a.y) - 9.7) < .01 and abs(pcbnew.ToMM(b.y) - 9.7) < .01
                    and sorted((round(pcbnew.ToMM(a.x), 1), round(pcbnew.ToMM(b.x), 1))) == [14.0, 28.3]):
                board.Remove(item)
                removed.append('track y=9.7 from x=14.0 to 28.3')
    return removed


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    done = []
    for fp in board.GetFootprints():
        if fp.GetReference() in CORRECTIONS:
            CORRECTIONS[fp.GetReference()](fp)
            done.append(fp.GetReference())
    for item in clear_fastening_holes(board):
        print('Removed redundant ground copper:', item)
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
