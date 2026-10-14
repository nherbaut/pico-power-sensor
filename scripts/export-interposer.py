#!/usr/bin/env python3
"""Export review artifacts, without manufacturing outputs."""
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from render_hardware_images import render_board_images
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/pcb/interposer'
env=os.environ.copy()
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    p=ROOT/'.build/kicad'/name;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
def cli(*args):subprocess.run(['kicad-cli',*map(str,args)],check=True,env=env)
cli('sch','export','pdf','-o',OUT/'schematic.pdf',OUT/'interposer.kicad_sch')
for side in ['front','back']:
    layers='F.Cu,F.Silkscreen,Edge.Cuts' if side=='front' else 'B.Cu,B.Silkscreen,Edge.Cuts'
    cli('pcb','export','svg','--mode-single','--exclude-drawing-sheet','--fit-page-to-board','--layers',layers,'-o',OUT/f'layout-{side}.svg',OUT/'interposer.kicad_pcb')
reports=OUT/'checks';reports.mkdir(exist_ok=True)
for name in ['erc.rpt','drc.rpt','source-check.json']:
    shutil.copyfile(ROOT/'.build/hardware'/name,reports/name)
render_board_images('interposer')
archive=OUT/'interposer-review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path!=archive and path.suffix not in ['.kicad_prl','.lck','.bak']:
            z.write(path,Path('interposer')/path.relative_to(OUT))
print('Exported schematic PDF, copper previews, check reports and portable review archive.')
