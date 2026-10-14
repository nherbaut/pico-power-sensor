#!/usr/bin/env python3
"""Diagnostic DC copper model; not a full loss budget or fabrication approval.

Requires numpy/scipy/shapely and the kicad-design skill's copper_guards.py.
KiCad 9 stores numeric net IDs on tracks: expand those IDs on an analysis-only
copy and cross-check the parser against pcbnew before using its solver.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver', type=Path, default=Path.home()/'.codex/skills/kicad-design/scripts/copper_guards.py')
    args = parser.parse_args()
    require(args.solver.is_file(), 'Missing external solver; pass --solver PATH')
    spec = importlib.util.spec_from_file_location('copper', args.solver)
    solver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver)
    from shapely.geometry import box

    source = ROOT/'hardware/pcb/interposer/interposer.kicad_pcb'
    before = digest(source)
    scratch = ROOT/'.build/copper-screen'
    scratch.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source.parent, scratch/'interposer', dirs_exist_ok=True)
    board_path = scratch/'interposer/interposer.kicad_pcb'
    native_path = scratch/'native-inventory.json'
    subprocess.run(['/usr/bin/python3', '-c', '''
import json, pcbnew, sys
from pathlib import Path
b=pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1], b)
b=pcbnew.LoadBoard(sys.argv[1])
d={'pads':[], 'tracks':0, 'vias':0}
for fp in b.GetFootprints():
 for p in fp.Pads():
  d['pads'].append(dict(ref=fp.GetReference(),pad=p.GetNumber(),
   x=pcbnew.ToMM(p.GetPosition().x),y=pcbnew.ToMM(p.GetPosition().y),net=p.GetNetname()))
for t in b.GetTracks():d['vias' if isinstance(t,pcbnew.PCB_VIA) else 'tracks']+=1
Path(sys.argv[2]).write_text(json.dumps(d))
''', str(board_path), str(native_path)], check=True)
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--schematic-parity',
                    '--exit-code-violations', '-o', str(scratch/'drc.rpt'), str(board_path)], check=True)
    # This is deliberately not saved as a .kicad_pcb or passed to KiCad.
    text = board_path.read_text()
    nets = dict(re.findall(r'\(net\s+(\d+)\s+("(?:[^"\\]|\\.)*")\)', text))
    nets.setdefault('0', '""')
    text = re.sub(r'\(net\s+(\d+)\)', lambda m: '(net '+m[1]+' '+nets[m[1]]+')', text)
    expanded = scratch/'named-net-analysis.txt'
    expanded.write_text(text)
    model = solver.parse_board(expanded)
    native = json.loads(native_path.read_text())
    require(len(model['pads']) == len(native['pads']), 'Parser omitted pads')
    require(len(model['segments']) == native['tracks'], 'Parser omitted tracks')
    require(len(model['vias']) == native['vias'], 'Parser omitted vias')
    for pad in native['pads']:
        require(any(q['ref'] == pad['ref'] and q['pad'] == pad['pad'] and
                    abs(q['x']-pad['x']) < 1e-6 and abs(q['y']-pad['y']) < 1e-6 and
                    (q['net'] or '') == pad['net'] for q in model['pads']), 'Pad coordinate/net mismatch: '+str(pad))
    stackups = list(solver.sexpr_blocks(board_path.read_text(), 'stackup'))
    require(len(stackups) == 1, 'Missing or ambiguous stackup')
    copper = {}
    for layer in solver.sexpr_blocks(stackups[0], 'layer'):
        name = re.match(r'\(layer\s+"([^"]+)"', layer)
        thickness = re.search(r'\(thickness\s+([\d.]+)\)', layer)
        if name and name[1] in ('F.Cu', 'B.Cu') and thickness:
            copper[name[1]] = float(thickness[1])
    require(copper == {'F.Cu': .07, 'B.Cu': .07}, 'Both copper layers must be 70 um for this model')
    # Calibrate a known rectangle and a deliberate break before grading real CAD.
    calibration = dict(pads=[dict(ref=r,pad='1',net='CAL',x=x,y=0,layers={'F.Cu'},
                                geom=box(x-.025,-1,x+.025,1),thru=False)
                             for r,x in [('A',0),('B',20)]], segments=[], vias=[],
                       zone_fills={('CAL','F.Cu'):[box(0,-1,20,1)]},
                       zones_declared={('CAL','F.Cu')},any_fill=True,nets={'CAL'})
    resistance, _ = solver.check_resistance(calibration,'CAL','A.1','B.1',grid=.05,oz=2)
    expected = 1.7241e-8/70e-6*20/2
    require(abs(resistance/expected-1) < .03, 'Rectangle calibration failed')
    broken = copy.deepcopy(calibration)
    broken['zone_fills'] = {('CAL','F.Cu'):[box(0,-1,9,1),box(11,-1,20,1)]}
    broken_r, _ = solver.check_resistance(broken,'CAL','A.1','B.1',grid=.05,oz=2)
    require(math.isinf(broken_r), 'Disconnected calibration failed')
    # Optimistic boundary: ideal external tie of both Pi 5 V header contacts.
    for pad in model['pads']:
        if pad['ref'] == 'J2' and pad['pad'] == '4':
            pad['pad'] = '2'
    results = []
    for grid in (.1, .05):
        r, nodes = solver.check_resistance(model,'/PI_5V','RSH1.4','J2.2',grid=grid,oz=2)
        require(math.isfinite(r) and r > 0, 'Unresolved copper model; not a board verdict')
        results.append(dict(grid_mm=grid,copper_resistance_mohm=r*1000,drop_at_5A_mV=r*5000,nodes=nodes))
    require(digest(source) == before, 'Live CAD changed during diagnostic')
    report = dict(evidence_type='DC raster calculation, not a physical measurement or complete loss bound',
        tool='kicad-design/scripts/copper_guards.py',tool_sha256=digest(args.solver),
        source_board_sha256=before,scratch_board_sha256=digest(board_path),
        native_parser_counts=dict(pads=len(model['pads']),tracks=len(model['segments']),vias=len(model['vias'])),
        calibration=dict(rectangle_mm=[20,2],copper_um=70,analytical_mohm=expected*1000,
                         model_mohm=resistance*1000,disconnected_fixture_rejected=True),
        results=results, assumptions=[
            '70 um copper per side; room-temperature resistivity 1.7241e-8 ohm m',
            'Both Pi 5V contacts ideally tied; header/contact resistance excluded',
            'KiCad 9 numeric net IDs expanded on analysis-only text; live CAD unchanged',
            'Native pad coordinates/nets and track/via counts cross-checked',
            'Pad shapes approximated by solver; fixed 0.2 mOhm interlayer transitions',
            'Only shunt-to-Pi positive branch; upstream copper and return not modeled'])
    output = ROOT/'hardware/review/copper-screen.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
