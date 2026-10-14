#!/usr/bin/python3
"""Use KiCad's native footprint library to refine the review PCB.

Run with /usr/bin/python3 (the distribution's pcbnew module, not Conda).
"""
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key, name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    path=ROOT/'.build/kicad'/name;path.mkdir(parents=True,exist_ok=True)
    os.environ[key]=str(path)
import pcbnew

OUT=ROOT/'hardware/pcb/interposer'
LIB=Path('/usr/share/kicad/footprints')
LIBRARY_PARTS={
    'D1':('LED_SMD','LED_0805_2012Metric'),
    'J1':('Connector_Phoenix_MSTB','PhoenixContact_MSTB_2,5_2-GF-5,08_1x02_P5.08mm_Horizontal_ThreadedFlange'),
    'F1':('Fuse','Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open'),
    'Q1':('Package_TO_SOT_SMD','TDSON-8-1'),
    'Q2':('Package_TO_SOT_SMD','TDSON-8-1'),
    'U2':('Package_SO','TSSOP-16_4.4x5mm_P0.65mm'),
    'U1':('Package_SO','MSOP-8_3x3mm_P0.65mm'),
    'RSH1':('Resistor_SMD','R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm'),
    'J3':('Connector_JST','JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'),
    'J4':('Connector_JST','JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical'),
}


def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))


def main():
    data=json.loads((OUT/'circuit.json').read_text())
    board=pcbnew.LoadBoard(str(OUT/'interposer.kicad_pcb'))
    if not board:raise SystemExit('Cannot load review PCB')
    oldparts={fp.GetReference():fp for fp in board.GetFootprints()}
    nets={str(n.GetNetname()):n for n in board.GetNetsByNetcode().values()}
    for p in data['parts']:
        if not p.get('on_board',True):continue
        ref=p['ref'];old=oldparts[ref]
        if ref in LIBRARY_PARTS:
            lib,name=LIBRARY_PARTS[ref]
        elif ref.startswith('C') and p['footprint']=='C_0805':
            lib,name='Capacitor_SMD','C_0805_2012Metric'
        elif ref.startswith(('R','C')):
            lib,name='Resistor_SMD','R_0805_2012Metric'
        elif ref.startswith('TP'):
            lib,name='TestPoint','TestPoint_Pad_D2.0mm'
        else:continue
        fp=pcbnew.FootprintLoad(str(LIB/(lib+'.pretty')),name)
        if not fp:raise SystemExit(f'Footprint missing: {lib}:{name}')
        fp.SetFPID(pcbnew.LIB_ID('PicoPower',p['footprint']))
        fp.SetReference(ref);fp.SetValue(p['value']);fp.SetPath(old.GetPath())
        fp.SetPosition(point(*p['position_mm']))
        if ref in ['Q1','J1']:fp.SetOrientationDegrees(180)
        for pad in fp.Pads():
            number=pad.GetNumber();net=p['pins'].get(number)
            if number and number not in p['pins']:
                raise SystemExit(f'Unexpected numbered footprint pad {ref}.{number}')
            if net:pad.SetNet(nets[net])
        board.Remove(old);board.Add(fp)
        # Keep a local library snapshot so the project is portable.
        library_fp=pcbnew.FootprintLoad(str(LIB/(lib+'.pretty')),name)
        library_fp.SetFPID(pcbnew.LIB_ID('PicoPower',p['footprint']))
        library_fp.SetValue(p['value'])
        pcbnew.FootprintSave(str(OUT/'PicoPower.pretty'),library_fp)
        p['footprint_source']=f'{lib}:{name}'
    for fp in board.GetFootprints():
        # Native reference placement is retained; values are hidden in silk.
        fp.Value().SetVisible(False)
        if fp.GetReference()=='J1':fp.Reference().SetPosition(point(24,10))
        if fp.GetReference()=='F1':fp.Reference().SetPosition(point(18,28))
        labels={'Q1':(31,19.2),'U2':(35,32.4),'C3':(31,25.3),'C4':(44,25.3),
                'R10':(21,30.4),'R11':(25,30.4),'R14':(24.5,31.5),
                'R12':(29,35.5),'R13':(33,35.5),'R15':(37,35.5),
                'TP1':(22.5,36.8),'TP2':(48,31.5)}
        if fp.GetReference() in labels:
            fp.Reference().SetPosition(point(*labels[fp.GetReference()]))
            fp.Reference().SetTextSize(point(.8,.8))
    for drawing in board.GetDrawings():
        if isinstance(drawing,pcbnew.PCB_TEXT):
            if 'PIN 1' in drawing.GetText():drawing.SetTextSize(point(.8,.8))
    # Header footprint courtyard encloses socket body and contact rows.
    header=next(fp for fp in board.GetFootprints() if fp.GetReference()=='J2')
    if not any(x.GetLayer()==pcbnew.F_CrtYd for x in header.GraphicalItems()):
        line=pcbnew.PCB_SHAPE(header);line.SetShape(pcbnew.SHAPE_T_RECT)
        line.SetStart(point(8.25,38.25));line.SetEnd(point(60,44.29))
        line.SetLayer(pcbnew.F_CrtYd);line.SetWidth(pcbnew.FromMM(.05));header.Add(line)
    snapshot=header.Duplicate();snapshot.SetPosition(point(0,0))
    snapshot.Reference().SetText('REF**')
    pcbnew.FootprintSave(str(OUT/'PicoPower.pretty'),snapshot)
    for hole in data['board']['mounting_holes']:
        name='MountingHole_2.7mm_M2.5'
        fp=pcbnew.FootprintLoad(str(LIB/'MountingHole.pretty'),name)
        fp.SetFPID(pcbnew.LIB_ID('PicoPower',name));fp.SetReference(hole['ref'])
        fp.SetPosition(point(*hole['position_mm']))
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY)
        fp.Value().SetVisible(False);board.Add(fp)
        snap=pcbnew.FootprintLoad(str(LIB/'MountingHole.pretty'),name)
        snap.SetFPID(pcbnew.LIB_ID('PicoPower',name))
        pcbnew.FootprintSave(str(OUT/'PicoPower.pretty'),snap)
        # Mechanical hardware is permitted; copper on both sides is not.
        zone=pcbnew.ZONE(board);zone.SetIsRuleArea(True)
        layers=pcbnew.LSET();layers.AddLayer(pcbnew.F_Cu);layers.AddLayer(pcbnew.B_Cu)
        zone.SetLayerSet(layers);zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True)
        zone.SetDoNotAllowCopperPour(True);zone.SetDoNotAllowPads(False) # Permit the NPTH mounting hole itself.
        zone.SetDoNotAllowFootprints(False)
        poly=zone.Outline();poly.NewOutline();x,y=hole['position_mm']
        radius=data['board']['mounting_keepout_diameter_mm']/2
        for i in range(64):
            angle=2*math.pi*i/64
            pos=point(x+radius*math.cos(angle),y+radius*math.sin(angle))
            poly.Append(pos.x,pos.y)
        board.Add(zone)
    pcbnew.SaveBoard(str(OUT/'interposer.kicad_pcb'),board)
    (OUT/'circuit.json').write_text(json.dumps(data,indent=2)+'\n')
    pads=[]
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNumber():
                pos=pad.GetPosition()
                pads.append(dict(reference=fp.GetReference(),pin=pad.GetNumber(),net=pad.GetNetname(),
                                 x_mm=pcbnew.ToMM(pos.x),y_mm=pcbnew.ToMM(pos.y),
                                 width_mm=pcbnew.ToMM(pad.GetSize().x),height_mm=pcbnew.ToMM(pad.GetSize().y)))
    report=ROOT/'.build/hardware/pads.json';report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(pads,indent=2)+'\n')
    print(f'Replaced provisional footprints with native KiCad footprints; {len(pads)} numbered pads.')


if __name__=='__main__':main()
