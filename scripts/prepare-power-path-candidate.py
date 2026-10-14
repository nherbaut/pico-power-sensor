#!/usr/bin/python3
"""Prepare one bounded copper alternative; never overwrite the live interposer."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
import pcbnew
from render_hardware_images import crop_preview

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.build/power-path-candidate/interposer'
REVIEW = ROOT/'hardware/review'


def point(x,y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'hardware/pcb/interposer'
    original = {p: digest(p) for p in source.rglob('*') if p.is_file()}
    shutil.copytree(source, OUT, dirs_exist_ok=True)
    board_path = OUT/'interposer.kicad_pcb'
    board = pcbnew.LoadBoard(str(board_path))
    net = board.FindNet('/PI_5V')
    if net is None:
        raise RuntimeError('Missing measured 5 V rail')
    polygon = [(8.75,35.5),(56.8,35.5),(58.6,33.7),(57,31),(58.8,29.8),
               (61.5,32.5),(61.5,35),(58,38.5),(8.75,38.5)]
    for layer in (pcbnew.F_Cu,pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        layers = pcbnew.LSET();layers.AddLayer(layer);zone.SetLayerSet(layers)
        zone.SetNet(net);zone.SetAssignedPriority(10)
        zone.SetLocalClearance(pcbnew.FromMM(.2));zone.SetMinThickness(pcbnew.FromMM(.2))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline();outline.NewOutline()
        for x,y in polygon:
            outline.Append(pcbnew.FromMM(x),pcbnew.FromMM(y))
        board.Add(zone)
    # Use the existing conservative obstacle engine rather than guessing sites.
    spec = importlib.util.spec_from_file_location('router',ROOT/'scripts/route-interposer.py')
    router_module = importlib.util.module_from_spec(spec);spec.loader.exec_module(router_module)
    router_module.OUT = OUT
    blocked = router_module.Router(board).obstacles(net.GetNetCode(),.8).any(axis=0)
    placed = []
    for desired_x,desired_y in [(10,37),(15,37),(20,37),(25,37),(30,37),(35,37),
                               (40,37),(45,37),(50,37),(55,37),(60,33),(60,34),(60,35)]:
        options = [(desired_x+dx,desired_y+dy)
                   for dx in (0,-.25,.25,-.5,.5,-.75,.75,-1,1,-1.5,1.5,-2,2,-3,3)
                   for dy in (0,-.25,.25,-.5,.5,-.75,.75)]
        options.sort(key=lambda p: math.dist(p,(desired_x,desired_y)))
        legal = [(x,y) for x,y in options
                 if not blocked[round(y/router_module.STEP),round(x/router_module.STEP)]
                 and all(math.dist((x,y),p) >= 1 for p in placed)]
        if not legal:
            raise RuntimeError('No legal stitching site near '+str((desired_x,desired_y)))
        x,y = legal[0];placed.append((x,y))
        via = pcbnew.PCB_VIA(board);via.SetPosition(point(x,y))
        via.SetWidth(pcbnew.FromMM(.8));via.SetDrill(pcbnew.FromMM(.4))
        via.SetViaType(pcbnew.VIATYPE_THROUGH);via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
        via.SetNet(net);board.Add(via)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path),board)
    report_path = OUT.parent/'drc.rpt'
    subprocess.run(['kicad-cli','pcb','drc','--severity-all','--schematic-parity',
                    '--exit-code-violations','-o',str(report_path),str(board_path)],check=True)
    report = report_path.read_text()
    if not all(s in report for s in ('Found 0 DRC violations','Found 0 unconnected pads','Found 0 Footprint errors')):
        raise RuntimeError('Candidate did not pass native DRC/parity')
    for path,sha in original.items():
        if digest(path) != sha:
            raise RuntimeError('Live source changed: '+str(path))
    REVIEW.mkdir(exist_ok=True)
    preview_svg = OUT.parent/'layout-front.svg'
    cropped = OUT.parent/'front-cropped.svg'
    subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--exclude-drawing-sheet',
                    '--fit-page-to-board','--layers','F.Cu,F.Silkscreen,Edge.Cuts','-o',str(preview_svg),str(board_path)],check=True)
    crop_preview(preview_svg,cropped,json.loads((OUT/'circuit.json').read_text())['board'])
    subprocess.run(['rsvg-convert','-w','1800','-o',str(REVIEW/'power-path-candidate.png'),str(cropped)],check=True)
    (OUT/'STUDY-README.txt').write_text(
        'COPPER STUDY ONLY. Not the authoritative interposer and not released.\n'
        'Added PI_5V copper on both faces and 13 stitching vias. Parts/pinout unchanged.\n'
        'DRC 0 violations/0 unconnected/0 parity. Complete voltage-loss target remains open.\n'
        'No Gerbers, fabrication authorization or bench measurements.\n')
    with zipfile.ZipFile(REVIEW/'power-path-candidate.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.suffix in ('.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod') or path.name in ('fp-lib-table','sym-lib-table','circuit.json','STUDY-README.txt'):
                archive.write(path,'interposer/'+path.relative_to(OUT).as_posix())
        archive.write(report_path,'drc.rpt')
    evidence = dict(status='isolated copper study; not promoted or released',
                    source_board_sha256=original[source/'interposer.kicad_pcb'],
                    candidate_board_sha256=digest(board_path),stitch_vias_mm=placed,
                    layers=['F.Cu','B.Cu'],polygon_mm=polygon,
                    drc='0 violations, 0 unconnected, 0 parity; effective-default release audit remains open')
    (REVIEW/'power-path-candidate.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('Exported isolated CAD candidate, preview and native DRC evidence; live CAD unchanged.')


if __name__ == '__main__':
    main()
