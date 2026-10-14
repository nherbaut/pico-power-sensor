#!/usr/bin/python3
"""Read current CAD and export review geometry and full-size paper plots only."""
import hashlib
import importlib.util
import json
import copy
import os
from pathlib import Path
import subprocess
from design_analysis import supplemental_analysis

ROOT = Path(__file__).resolve().parents[1]
for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
    target = ROOT / '.build/kicad' / name
    target.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(target)
import pcbnew

spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/check-release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
OUTPUT = ROOT / 'hardware/review'


def mm(point):
    return [round(pcbnew.ToMM(point.x), 6), round(pcbnew.ToMM(point.y), 6)]


def export(board_name):
    folder = ROOT / 'hardware/pcb' / board_name
    source = folder / f'{board_name}.kicad_pcb'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    board = pcbnew.LoadBoard(str(source))
    circuit = json.loads((folder / 'circuit.json').read_text())
    parts = {p['ref']: p for p in circuit['parts']}
    footprints = []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        position = fp.GetPosition()
        orientation = fp.GetOrientationDegrees()
        pads = []
        for pad in fp.Pads():
            offset = pad.GetFPRelativePosition()
            pads.append(dict(number=pad.GetNumber(), local_position_mm=mm(offset),
                             board_position_mm=mm(pad.GetPosition()),
                             attribute=int(pad.GetAttribute()),
                             size_mm=mm(pad.GetSize()), drill_mm=mm(pad.GetDrillSize()),
                             shape=int(pad.GetShape()), net=pad.GetNetname()))
        p = parts.get(fp.GetReference(), {})
        footprints.append(dict(reference=fp.GetReference(), footprint=str(fp.GetFPID().GetLibItemName()),
                               position_mm=mm(position), rotation_degrees=orientation,
                               proposed_mpn_in_cad=p.get('mpn', ''),
                               library_source=p.get('footprint_source', 'custom'), pads=pads))
    document = dict(board=board_name, design_sha256=release.design_hash(ROOT, board_name),
                    evidence_type='automated CAD geometry extraction; not footprint approval or physical measurement',
                    footprints=footprints)
    (OUTPUT / f'{board_name}-geometry.json').write_text(json.dumps(document, indent=2) + '\n')
    subprocess.run(['kicad-cli', 'pcb', 'export', 'pdf', '--mode-single', '--black-and-white',
                    '--layers', 'F.Fab,Edge.Cuts', '--sketch-pads-on-fab-layers',
                    '--drill-shape-opt', '2', '-o', str(OUTPUT / f'{board_name}-mockup.pdf'), str(source)], check=True)
    subprocess.run(['python3', str(ROOT / 'scripts/finish-review-pdf.py'),
                    str(OUTPUT / f'{board_name}-mockup.pdf'), board_name,
                    str(circuit['board']['width_mm'])], check=True)
    if hashlib.sha256(source.read_bytes()).hexdigest() != before:
        raise RuntimeError('CAD source unexpectedly changed during review export')
    print(f'{board_name}: exported geometry and 1:1 PCB plot; source unchanged')


def calculations():
    spec = importlib.util.spec_from_file_location('interposer', ROOT / 'scripts/check-interposer.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    circuit = json.loads((ROOT / 'hardware/pcb/interposer/circuit.json').read_text())
    nominal = checker.check_circuit(circuit)
    drift = copy.deepcopy(circuit)
    # Conservative independent +/-25 ppm/K drift for proposed threshold resistors.
    # Max excursion from 25 C over -40..85 C is 65 K. These are assumptions, not measurements.
    drift['protection']['resistor_tolerance'] = (1 + circuit['protection']['resistor_tolerance']) * (1 + 25e-6 * 65) - 1
    temperature = checker.check_circuit(drift)
    current = circuit['load']['max_amperes']
    shunt_max = circuit['shunt']['ohms'] * (1 + circuit['shunt']['tolerance'])
    mosfets_reference = 2 * 0.0014
    fuse_cold_nominal = .0095
    limit = 0.1 / current
    report = dict(design_sha256=release.design_hash(ROOT, 'interposer'),
                  evidence_type='design arithmetic and datasheet reference conditions; not physical measurements',
                  initial_tolerance_protection=nominal['protection_input_thresholds_V'],
                  proposed_25ppm_resistors_minus40_to85C=temperature['protection_input_thresholds_V'],
                  assumed_combined_resistor_tolerance=drift['protection']['resistor_tolerance'],
                  power_path=dict(target_drop_V=0.1, current_A=current, total_budget_ohm=limit,
                                  shunt_initial_tolerance_max_ohm=shunt_max,
                                  two_mosfets_room_temperature_reference_ohm=mosfets_reference,
                                  remaining_before_connectors_fuse_copper_hot_effects_ohm=limit-shunt_max-mosfets_reference,
                                  fuse_nominal_cold_ohm=fuse_cold_nominal,
                                  reference_drop_with_fuse_before_holder_contacts_copper_V=current*(shunt_max+mosfets_reference+fuse_cold_nominal),
                                  remaining_reference_budget_after_fuse_ohm=limit-shunt_max-mosfets_reference-fuse_cold_nominal,
                                  complete_budget=False),
                  protection_gain_constraints=dict(
                      min_gain_for_5_10V_ov_recovery_under_stated_corners=5.1/(.4925-.032),
                      max_gain_for_5_25V_trip_ceiling_under_stated_corners=5.25/.5075,
                      simultaneous_constraints_feasible=False),
                  limitations=['Comparator hysteresis figures use the datasheet conditions; verify at 5.1 V.',
                               'Leakage, ageing, resistor correlation and transients are not covered by these intervals.',
                               'MOSFET resistance reference is not a hot assembled-board bound.',
                               'Fuse reference is nominal cold resistance, not a guaranteed hot resistance.',
                               'No reset/recovery procedure or Pi-safe transient ceiling has been validated.'])
    report['prototype_review'] = supplemental_analysis()
    (OUTPUT / 'design-analysis.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in ('interposer', 'carrier'):
        export(name)
    calculations()
