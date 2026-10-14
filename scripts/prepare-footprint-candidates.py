#!/usr/bin/python3
"""Prepare isolated CAD corrections; leave saved projects and autosaves untouched."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.build/footprint-candidates'
REVIEW = ROOT / 'hardware/review'
for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
    target = ROOT / '.build/kicad' / name
    target.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(target)
import pcbnew


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


from footprint_corrections import point, led, shunt, socket


def prepare(name):
    source = ROOT / 'hardware/pcb' / name
    target = WORK / name
    target.mkdir(parents=True, exist_ok=True)
    protected = {p: digest(p) for p in source.rglob('*') if p.is_file() and
                 (p.suffix in ('.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod') or p.name=='circuit.json')}
    for path in source.iterdir():
        if path.is_dir() and path.suffix == '.pretty':
            shutil.copytree(path,target/path.name,dirs_exist_ok=True)
        elif path.is_file() and (path.suffix in ('.kicad_pro','.kicad_sch','.kicad_sym') or
                                path.name in (f'{name}.kicad_pcb','circuit.json','board-bom.csv','fp-lib-table','sym-lib-table')):
            shutil.copyfile(path,target/path.name)
    board_path = target / f'{name}.kicad_pcb'
    board = pcbnew.LoadBoard(str(board_path))
    changes=[]
    for fp in board.GetFootprints():
        ref=fp.GetReference()
        if ref.startswith('D'):
            led(fp);changes.append(f'{ref}: Kingbright 1.25 x 1.10 mm pads, 1.10 mm gap; cathode pad 1 retained')
        if name=='interposer' and ref=='RSH1':
            shunt(fp);changes.append('RSH1: sense pad length 1.40 -> 1.70 mm, outer edge and .51 mm vertical gap retained')
        if name=='carrier' and ref=='J_EVM':
            socket(fp);changes.append('J_EVM: projected body depth 7.20 -> 4.85 mm; offset and mating orientation remain provisional')
    # Snapshot corrected embedded footprints into the isolated local library only.
    library=target/('PicoPower.pretty' if name=='interposer' else 'Carrier.pretty')
    saved=set()
    for fp in board.GetFootprints():
        item=str(fp.GetFPID().GetLibItemName())
        if item in ('LED_0805','WSK2512_5m_Kelvin','NPPN062FJFN') and item not in saved:
            clone=fp.Duplicate();clone.SetReference('REF**');clone.SetPosition(point(0,0));clone.SetOrientationDegrees(0)
            pcbnew.FootprintSave(str(library),clone);saved.add(item)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path),board)
    record=dict(board=name,status='isolated review candidate; not fabrication-ready',
                baseline_pcb_sha256=digest(source/f'{name}.kicad_pcb'),
                candidate_pcb_sha256=digest(board_path),changes=changes,
                unmerged_autosave_present=any(source.glob('_autosave-*')),
                limitations=['Circuit, BOM and routing otherwise unchanged.',
                             'Physical fit and remaining footprint reviews are not complete.',
                             'Do not replace a saved project or autosave automatically.'])
    (target/'candidate-changes.json').write_text(json.dumps(record,indent=2)+'\n')
    for mode in ('erc','drc'):
        suffix='sch' if mode=='erc' else 'pcb'
        cmd=['kicad-cli',suffix,mode,'--exit-code-violations']
        if mode=='drc':cmd+=['--schematic-parity']
        cmd+=['-o',str(target/f'{mode}.rpt'),str(target/f'{name}.kicad_{suffix}')]
        subprocess.run(cmd,check=True)
    archive=REVIEW/f'{name}-footprint-candidate.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(target.rglob('*')):
            if path.is_file() and path.suffix not in ('.kicad_prl','.lck'):
                handle.write(path,Path(name)/path.relative_to(target))
    (REVIEW/f'{name}-candidate-changes.json').write_text(json.dumps(record,indent=2)+'\n')
    for path,before in protected.items():
        if digest(path)!=before:raise RuntimeError(f'Original source changed: {path}')
    print(f'{name}: isolated candidate ERC/DRC passed; originals and autosaves unchanged')


if __name__=='__main__':
    for name in ('interposer','carrier'):
        prepare(name)
