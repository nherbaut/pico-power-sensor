#!/usr/bin/python3
"""Synchronize PCB net names/attributes with the schematic and set stackup."""
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    p=ROOT/'.build/kicad'/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
import pcbnew
OUT=ROOT/'hardware/pcb/interposer'
path=OUT/'interposer.kicad_pcb'
b=pcbnew.LoadBoard(str(path))
data=json.loads((OUT/'circuit.json').read_text())
parts={p['ref']:p for p in data['parts']}
for net in b.GetNetsByNetcode().values():
    name=str(net.GetNetname())
    if name and not name.startswith(('/', 'unconnected-')):net.SetNetname('/'+name)
for fp in b.GetFootprints():
    if fp.GetReference() not in parts:continue # Board-only mounting holes.
    p=parts[fp.GetReference()]
    attrs=fp.GetAttributes()
    if p.get('in_bom',True):attrs &= ~pcbnew.FP_EXCLUDE_FROM_BOM
    else:attrs |= pcbnew.FP_EXCLUDE_FROM_BOM
    fp.SetAttributes(attrs)
    for pad in fp.Pads():
        nc_name={('U1','6'):'FAULT_N',('U2','10'):'2B2'}.get((fp.GetReference(),pad.GetNumber()))
        if nc_name and pad.GetNetCode()==0:
            net=pcbnew.NETINFO_ITEM(b,f'unconnected-({fp.GetReference()}-{nc_name}-Pad{pad.GetNumber()})')
            b.Add(net);pad.SetNet(net)
for text in b.GetDrawings():
    if isinstance(text,pcbnew.PCB_TEXT) and text.GetText() in ['5.1V DC','+','-']:
        x={'5.1V DC':21,'+':14.08,'-':9}[text.GetText()]
        text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(16)))
pcbnew.SaveBoard(str(path),b)
s=path.read_text()
if '(stackup' not in s:
    s=s.replace('(setup\n','''(setup
        (stackup
            (layer "F.SilkS" (type "Top Silk Screen"))
            (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
            (layer "F.Cu" (type "copper") (thickness 0.07))
            (layer "dielectric 1" (type "core") (thickness 1.44) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
            (layer "B.Cu" (type "copper") (thickness 0.07))
            (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
            (layer "B.SilkS" (type "Bottom Silk Screen"))
            (copper_finish "None")
            (dielectric_constraints no)
        )
''',1)
    path.write_text(s)
print('Synchronized schematic net names and BOM flags; 70 um copper stackup recorded.')
