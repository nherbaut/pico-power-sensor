#!/usr/bin/python3
"""Generate the independent carrier review project (overwrites carrier CAD only)."""
import csv
import importlib.util
import json
import os
import shutil
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
# Left strip added for the INA229 group; everything else keeps its layout, shifted right.
SHIFT = 12
MEASUREMENT_GROUP = {'J_SENSE', 'U_PM', 'R_ALERT', 'C_PM'}
OUT = ROOT / 'hardware/pcb/carrier'
LIB = Path('/usr/share/kicad/footprints')
for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
    target = ROOT / '.build/kicad' / name
    target.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(target)
import pcbnew
from footprint_corrections import led, selected_passive, part_fields
from component_selections import apply_selections, constraints


def uid(name):
    return str(uuid5(NAMESPACE_URL, 'picopower/carrier/rev-a/' + name))


def point(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def write(name, content):
    (OUT / name).write_text(content, encoding='utf-8')


def circuit():
    parts = []
    def add(ref, value, footprint, pins, pos, mpn='', url='', kind='passive', rotation=0):
        pos = list(pos) if ref in MEASUREMENT_GROUP else [pos[0] + SHIFT, pos[1]]
        parts.append(dict(ref=ref, value=value, footprint=footprint,
                          pins={str(n): net for n, net in pins.items()}, position_mm=pos,
                          mpn=mpn, documentation_url=url, kind=kind, rotation_deg=rotation))
    pico = {n: None for n in range(1, 41)}
    pico.update({1:'PICO_TX', 2:'PICO_RX', 4:'PICO_MARK', 5:'ALERT', 6:'MISO', 7:'CS', 9:'SCLK', 10:'MOSI',
                 32:'LED1_GPIO', 31:'LED2_GPIO', 29:'LED3_GPIO', 27:'LED4_GPIO', 26:'LED5_GPIO',
                 16:'SD_MISO',17:'SD_CS',19:'SD_SCLK',20:'SD_MOSI',
                 36:'PICO_3V3',40:'USB_5V'})
    pico.update({n:'GND' for n in [3,8,13,18,23,28,33,38]})
    add('J_PICO', 'Pico 2 W / socketed', 'Pico_Socketed', pico, [32,3], 'Pico 2 W',
        'https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf')
    add('J_UART', 'INTERPOSER / JST-XH-5', 'XH5',
        {1:'GND',2:'PICO_RX',3:'PICO_TX',4:'PICO_MARK',5:'PICO_3V3'}, [15,10],
        'B5B-XH-A(LF)(SN)', 'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf')
    # Measurement cable from interposer J3: straight through, same numbering.
    add('J_SENSE', 'INTERPOSER SENSE / JST-XH-4', 'XH4',
        {1:'SENSE_PLUS',2:'SENSE_MINUS',3:'SENSE_VBUS',4:'GND'}, [5.2,27],
        'B4B-XH-A(LF)(SN)', 'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf', rotation=90)
    # INA229 DGS (VSSOP-10), SLYS023A Table 5-1. Kelvin pair arrives by cable.
    add('U_PM', 'INA229 power monitor', 'VSSOP10',
        {1:'CS',2:'MOSI',3:'ALERT',4:'MISO',5:'SCLK',6:'PICO_3V3',7:'GND',
         8:'SENSE_VBUS',9:'SENSE_MINUS',10:'SENSE_PLUS'}, [12.5,23.2],
        'INA229AIDGSR', 'https://www.ti.com/lit/ds/symlink/ina229.pdf', rotation=180)
    for n, y in enumerate([13,20,27,34,41],1):
        add(f'D{n}',f'LED{n} GREEN','LED_0805',{1:'GND',2:f'LED{n}_A'},[60,y],
            'APT2012LZGCK','https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf','led')
        add(f'R_LED{n}','1k 1%','R_0805',{1:f'LED{n}_GPIO',2:f'LED{n}_A'},[60,y+2.3])
        add(f'R_PD{n}','100k 1%','R_0805',{1:f'LED{n}_GPIO',2:'GND'},[60,y+4.6])
    add('R_CS','100k 1%','R_0805',{1:'PICO_3V3',2:'CS'},[19,23])
    add('R_ALERT','10k 1%','R_0805',{1:'PICO_3V3',2:'ALERT'},[12.5,29.2])
    add('C_PM','100nF X7R 16V','C_0805',{1:'PICO_3V3',2:'GND'},[12.5,19.4])
    add('C1','100nF X7R 16V','C_0805',{1:'PICO_3V3',2:'GND'},[19,27])
    add('C2','1uF X7R 16V','C_0805',{1:'PICO_3V3',2:'GND'},[19,31])
    add('TP1','PICO 3V3','TestPoint',{1:'PICO_3V3'},[24,35])
    add('TP2','GND','TestPoint',{1:'GND'},[18,35])
    add('J_SD','microSD / hinge','microSD_Wuerth',
        {1:'SD_DAT2',2:'SD_CS',3:'SD_MOSI',4:'SD_3V3',5:'SD_SCLK',6:'GND',
         7:'SD_MISO',8:'SD_DAT1',9:'GND'},[20,45], '693072010801',
        'https://www.we-online.com/components/products/datasheet/693072010801.pdf', rotation=180)
    add('U_SD','3.3V / dedicated SD LDO','SOT23_5',
        {1:'USB_5V',2:'GND',3:'PICO_3V3',4:None,5:'SD_3V3'},[25,20],
        'TLV75533PDBVR','https://www.ti.com/lit/gpn/TLV755P')
    for n,(signal,y) in enumerate(zip(['SD_DAT2','SD_CS','SD_MOSI','SD_MISO','SD_DAT1'],[16,20,24,28,32]),1):
        add(f'R_SDP{n}','10k 1%','R_0805',{1:'SD_3V3',2:signal},[15,y])
    add('C_SDIN','4.7uF X7R 16V','C_0805',{1:'USB_5V',2:'GND'},[25,16])
    add('C_SDOUT','4.7uF X7R 16V','C_0805',{1:'SD_3V3',2:'GND'},[25,24])
    add('C_SDBULK','22uF X7R 16V','C_1206',{1:'SD_3V3',2:'GND'},[9,39])
    add('C_SDSOCKET','100nF X7R 16V','C_0805',{1:'SD_3V3',2:'GND'},[10,43])
    apply_selections('carrier', parts)
    return dict(revision='A-draft',release_status='not-for-manufacture',
                design_constraints=constraints(),
                physical_validation='not performed',
                board=dict(width_mm=66+SHIFT,height_mm=54,thickness_mm=1.6,copper_um=35,layers=2,
                           routing_status='unrouted', mounting_drill_mm=2.7,
                           mounting_keepout_diameter_mm=6,
                           mounting_holes=[dict(ref=f'H{i}',position_mm=pos) for i,pos in
                                           enumerate([[4,4],[62+SHIFT,4],[4,50],[62+SHIFT,50]],1)],
                           antenna_keepout_mm=[33.79+SHIFT,44.13,48+SHIFT,54]),
                gpio=dict(uart_rx=1,uart_tx=0,marker=2,alert=3,sclk=6,mosi=7,miso=4,cs=5,
                          leds=[27,26,22,21,20],sd_spi=1,sd_miso=12,sd_cs=13,sd_sclk=14,sd_mosi=15),
                storage=dict(interface='SPI1',voltage=3.3,regulator='TLV75533PDBVR',
                             supply='USB_5V',card_detect=False,firmware_status='not implemented',
                             logging='buffered acquisition; SD stalls must not block sampling'),
                parts=parts)


def helper():
    # Reuse only the established symbol-block renderer, never its interposer main.
    spec=importlib.util.spec_from_file_location('interposer_symbols', ROOT/'scripts/generate-interposer.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FLAG_SYMBOL = '''    (symbol "Carrier:SupplyFlag" (pin_names (offset 0)) (in_bom no) (on_board no)
      (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)) hide))
      (property "Value" "PWR_FLAG" (at 0 2.54 0) (effects (font (size 1 1))))
      (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1))))))
    )'''


def schematic(data):
    h=helper()
    definitions=[h.symbol_definition(p).replace('PicoPower:', 'Carrier:') for p in data['parts']]
    lines=['(kicad_sch (version 20231120) (generator "eeschema")',
           f'(uuid "{uid("sheet")}") (paper "A2")',
           '(title_block (title "PicoPower instrument carrier") (date "2026-10-14") (rev "A DRAFT")',
           '(comment 1 "Independent USB power; INA229 SPI0; microSD SPI1; five programmable LEDs"))',
           '(lib_symbols',*definitions,FLAG_SYMBOL,')']
    placements={'J_PICO':(65,100),'J_UART':(145,65),'J_SENSE':(145,115),'U_PM':(145,137),'R_ALERT':(145,187),'C_PM':(145,232),
                'R_CS':(145,165),'C1':(145,210),'C2':(145,255),'TP1':(65,205),'TP2':(65,255),
                'J_SD':(240,225),'U_SD':(310,225),'C_SDIN':(380,225),'C_SDOUT':(450,225),
                'C_SDBULK':(380,270),'C_SDSOCKET':(450,270)}
    for n in range(1,6):
        x=235+(n-1)*70
        placements[f'R_LED{n}']=(x,65)
        placements[f'D{n}']=(x,115)
        placements[f'R_PD{n}']=(x,165)
        placements[f'R_SDP{n}']=(x,335)
    for p in data['parts']:
        ref=p['ref']; x,y=[round(v/1.27)*1.27 for v in placements[ref]]
        coords,height=h.pin_layout(p)
        lines += [f'(symbol (lib_id "Carrier:{ref}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("symbol/"+ref)}")',
                  f'(property "Reference" {json.dumps(ref)} (at {x} {y-height-3} 0) (effects (font (size 1.27 1.27))))',
                  f'(property "Value" {json.dumps(p["value"])} (at {x} {y+height+3} 0) (effects (font (size 1 1))))',
                  f'(property "Footprint" "Carrier:{p["footprint"]}" (at {x} {y} 0) (effects (font (size 1 1)) hide))',
                  f'(property "Datasheet" {json.dumps(p["documentation_url"])} (at {x} {y} 0) (effects (font (size 1 1)) hide))',
                  f'(property "MPN" {json.dumps(p["mpn"])} (at {x} {y} 0) (effects (font (size 1 1)) hide))',
                  *[f'(pin "{n}" (uuid "{uid("pin/"+ref+"/"+n)}"))' for n in p['pins']],
                  f'(instances (project "carrier" (path "/{uid("sheet")}" (reference "{ref}") (unit 1))))',')']
        for n,px,py,angle in coords:
            net=p['pins'][n]; dx,dy=x+px,y-py
            if net:
                lines.append(f'(label "{net}" (at {dx} {dy} {angle}) (effects (font (size .9 .9)) (justify {"right" if angle==0 else "left"} bottom)) (uuid "{uid("label/"+ref+"/"+n)}"))')
            else:
                lines.append(f'(no_connect (at {dx} {dy}) (uuid "{uid("nc/"+ref+"/"+n)}"))')
    # Power flags: PICO_3V3 and GND are driven by passive Pico module pins.
    for i,net in enumerate(['PICO_3V3','GND']):
        fx,fy=[round(v/1.27)*1.27 for v in (30+35*i,385)];ref=f'#FLG0{i+1}'
        lines += [f'(symbol (lib_id "Carrier:SupplyFlag") (at {fx} {fy} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref)}")',
                  f'(property "Reference" "{ref}" (at {fx} {fy} 0) (effects (font (size 1 1)) hide))',
                  f'(property "Value" "PWR_FLAG" (at {fx} {fy-2.54} 0) (effects (font (size 1 1))))',
                  f'(instances (project "carrier" (path "/{uid("sheet")}" (reference "{ref}") (unit 1))))',')',
                  f'(label "{net}" (at {fx} {fy} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(ref+"/label")}"))']
    notes='Independent USB power only. INA229 U_PM measures the interposer shunt via J_SENSE. No DUT supply on carrier.\\nLED1-5 GP27/26/22/21/20. INA229 SPI0 GP4-7. SD SPI1 GP12-15.\\nU_SD input: USB VBUS (physical 40). EN: Pico 3V3. SD_3V3 is separate.\\nCard CMD and DAT0-3 have 10k pull-ups to SD_3V3; CLK has no pull-up.\\nNo card-detect switch. Buffered logger firmware is a separate milestone.\\nInterposer cables straight-through. Bench validation pending.'
    lines += [f'(text "{notes}" (at 220 385 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid "{uid("notes")}"))',')']
    write('carrier.kicad_sch','\n'.join(lines)+'\n')
    write('Carrier.kicad_sym','(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+
          '\n'.join(h.symbol_definition(p,True).replace('PicoPower:', 'Carrier:') for p in data['parts'])+'\n'+
          FLAG_SYMBOL.replace('"Carrier:SupplyFlag"','"SupplyFlag"')+'\n)\n')


def rule_area(board, name, coords, footprints=False):
    zone=pcbnew.ZONE(board);zone.SetIsRuleArea(True);zone.SetZoneName(name)
    layers=pcbnew.LSET();layers.AddLayer(pcbnew.F_Cu);layers.AddLayer(pcbnew.B_Cu)
    zone.SetLayerSet(layers);zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True)
    zone.SetDoNotAllowCopperPour(True);zone.SetDoNotAllowPads('antenna' in name.lower())
    zone.SetDoNotAllowFootprints(footprints)
    poly=zone.Outline();poly.NewOutline()
    for x,y in coords:
        pos=point(x,y);poly.Append(pos.x,pos.y)
    board.Add(zone)


def board(data):
    library=OUT/'Carrier.pretty';library.mkdir(exist_ok=True)
    # KiCad only recognises a .pretty folder that already holds a footprint; seed it
    # with the mounting-hole footprint, which is saved again below.
    seed=library/'MountingHole_2.7mm_M2.5.kicad_mod'
    if not seed.exists():shutil.copyfile(LIB/'MountingHole.pretty'/seed.name,seed)
    sources={'Pico_Socketed':('Module','RaspberryPi_Pico_Common_THT'),
             'XH5':('Connector_JST','JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical'),
             'XH4':('Connector_JST','JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'),
             'VSSOP10':('Package_SO','VSSOP-10_3x3mm_P0.5mm'),
             'R_0805':('Resistor_SMD','R_0805_2012Metric'),
             'C_0805':('Capacitor_SMD','C_0805_2012Metric'),
             'C_0805_Murata':('Capacitor_SMD','C_0805_2012Metric'),
             'C_1206':('Capacitor_SMD','C_1206_3216Metric'),
             'microSD_Wuerth':('Connector_Card','microSD_HC_Wuerth_693072010801'),
             'SOT23_5':('Package_TO_SOT_SMD','SOT-23-5'),
             'LED_0805':('LED_SMD','LED_0805_2012Metric'),
             'TestPoint':('TestPoint','TestPoint_Pad_D2.0mm')}
    b=pcbnew.BOARD();b.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.6))
    names=sorted({net for p in data['parts'] for net in p['pins'].values() if net})
    # NC nets must match eeschema's names for schematic parity.
    names += [f'unconnected-({p["ref"]}-NC-Pad{n})' for p in data['parts'] for n,net in p['pins'].items() if net is None]
    nets={}
    for name in names:
        net=pcbnew.NETINFO_ITEM(b,name if name.startswith('unconnected-') else '/'+name);b.Add(net);nets[name]=net
    for p in data['parts']:
        name=p['footprint']
        if name in sources:
            lib,original=sources[name]
            fp=pcbnew.FootprintLoad(str(LIB/(lib+'.pretty')),original)
            if name=='LED_0805':led(fp)
            selected_passive(fp, name)
            fp.SetFPID(pcbnew.LIB_ID('Carrier',name))
            snap=fp.Duplicate();snap.SetValue(p['value']);pcbnew.FootprintSave(str(library),snap)
            if name != 'C_0805_Murata':p['footprint_source']=lib+':'+original
            if name=='LED_0805':p['footprint_source']+='; pads corrected to Kingbright APT2012LZGCK datasheet page 1'
        else:
            raise ValueError('No footprint source for '+name)
        fp.SetReference(p['ref']);fp.SetValue(p['value'])
        part_fields(fp, p)
        fp.SetOrientationDegrees(p.get('rotation_deg',0))
        fp.SetPosition(point(*p['position_mm']))
        fp.SetPath(pcbnew.KIID_PATH('/'+uid('sheet')+'/'+uid('symbol/'+p['ref'])))
        fp.Value().SetVisible(False)
        fp.SetAttributes(fp.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
        fp.Reference().SetTextSize(point(.8,.8));fp.Reference().SetTextThickness(pcbnew.FromMM(.12))
        if p['ref'].startswith(('R_LED','R_PD')):
            fp.Reference().SetPosition(point(55.5+SHIFT,p['position_mm'][1]))
        if p['ref'].startswith('D') or p['ref']=='J_PICO':
            # Visible LED1-LED5 labels replace redundant D1-D5 silk labels.
            fp.Reference().SetLayer(pcbnew.F_Fab)
        if p['ref']=='J_SENSE':fp.Reference().SetPosition(point(5.2,32.4))
        if p['ref']=='J_SD':fp.Reference().SetPosition(point(28.5+SHIFT,37))
        if p['ref']=='C_SDSOCKET':
            fp.Reference().SetPosition(point(6+SHIFT,44));fp.Reference().SetTextAngle(pcbnew.EDA_ANGLE(90,pcbnew.DEGREES_T))
        for pad in fp.Pads():
            n=pad.GetNumber()
            if not n:continue
            if n not in p['pins']:raise ValueError(f'Unexpected pad {p["ref"]}.{n}')
            net=p['pins'][n]
            pad.SetNet(nets[net if net else f'unconnected-({p["ref"]}-NC-Pad{n})'])
        b.Add(fp)
    # Board-only mounting holes use native reviewed drill footprints.
    hole_name='MountingHole_2.7mm_M2.5'
    snap=pcbnew.FootprintLoad(str(LIB/'MountingHole.pretty'),hole_name)
    snap.SetFPID(pcbnew.LIB_ID('Carrier',hole_name));pcbnew.FootprintSave(str(library),snap)
    import math
    for hole in data['board']['mounting_holes']:
        fp=pcbnew.FootprintLoad(str(library),hole_name);fp.SetReference(hole['ref'])
        fp.SetFPID(pcbnew.LIB_ID('Carrier',hole_name));fp.SetPosition(point(*hole['position_mm']))
        fp.SetAttributes(fp.GetAttributes()|pcbnew.FP_BOARD_ONLY);fp.Value().SetVisible(False);b.Add(fp)
        x,y=hole['position_mm']
        fp.Reference().SetPosition(point(x,8.2 if y==4 else 53))
        fp.Reference().SetTextSize(point(.8,.8));fp.Reference().SetTextThickness(pcbnew.FromMM(.12))
        rule_area(b,hole['ref']+' hardware clearance',[(x+3*math.cos(i*math.pi/32),y+3*math.sin(i*math.pi/32)) for i in range(64)])
    x0,y0,x1,y1=data['board']['antenna_keepout_mm']
    rule_area(b,'Pico antenna / no copper or components',[(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
    width,height=data['board']['width_mm'],data['board']['height_mm']
    corners=[(0,0),(width,0),(width,height),(0,height)]
    for a,c in zip(corners,corners[1:]+corners[:1]):
        line=pcbnew.PCB_SHAPE(b);line.SetShape(pcbnew.SHAPE_T_SEGMENT);line.SetStart(point(*a));line.SetEnd(point(*c))
        line.SetWidth(pcbnew.FromMM(.05));line.SetLayer(pcbnew.Edge_Cuts);b.Add(line)
    def text(content,x,y,layer=pcbnew.F_SilkS,size=.8):
        t=pcbnew.PCB_TEXT(b);t.SetText(content);t.SetPosition(point(x,y));t.SetLayer(layer)
        t.SetTextSize(point(size,size));t.SetTextThickness(pcbnew.FromMM(.12));b.Add(t)
        if layer==pcbnew.B_SilkS:t.SetMirrored(True)
    text('PICOPOWER CARRIER A',19+SHIFT,1.8,size=.8)
    text('INTERPOSER',20+SHIFT,4.5);text('GND',10+SHIFT,10);text('3V3',29+SHIFT,10);text('OUT',29+SHIFT,11.5)
    text('SENSE',2.6,16);text('USB POWER',41+SHIFT,8,pcbnew.Dwgs_User)
    text('NOT FOR MANUFACTURE',18+SHIFT,49,pcbnew.B_SilkS,size=.8)
    text('microSD',20+SHIFT,36.8)
    text('ANTENNA / KEEP CLEAR',41+SHIFT,51,pcbnew.Dwgs_User,size=.7)
    for n,y in enumerate([13,20,27,34,41],1):text('LED'+str(n),63.4+SHIFT,y)
    pcbnew.SaveBoard(str(OUT/'carrier.kicad_pcb'),b)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=circuit();schematic(data);board(data)
    write('circuit.json',json.dumps(data,indent=2)+'\n')
    write('carrier.kicad_pro',json.dumps({'meta':{'filename':'carrier.kicad_pro','version':1},
        'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.2,
                                           'min_via_diameter':.6,'min_through_hole_diameter':.3}}},
        'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,
                                   'via_diameter':.6,'via_drill':.3}]}},indent=2)+'\n')
    write('fp-lib-table','(fp_lib_table (lib (name "Carrier") (type "KiCad") (uri "${KIPRJMOD}/Carrier.pretty") (options "") (descr "Local carrier footprints")))\n')
    write('sym-lib-table','(sym_lib_table (lib (name "Carrier") (type "KiCad") (uri "${KIPRJMOD}/Carrier.kicad_sym") (options "") (descr "Carrier review symbols")))\n')
    with (OUT/'pinout.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['reference','pin','net'])
        for p in data['parts']:
            for n,net in p['pins'].items():writer.writerow([p['ref'],n,net or 'NC'])
    with (OUT/'board-bom.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['reference','value','manufacturer_reference','footprint','documentation_url','status'])
        for p in data['parts']:
            writer.writerow([p['ref'],p['value'],p['mpn'],'Carrier:'+p['footprint'],p['documentation_url'],'CAD draft; footprint and bench review pending'])
    write('Carrier.pretty/LICENSE.md','Native footprint snapshots: KiCad libraries, CC-BY-SA 4.0 with footprint exception.\n')
    print('Generated independent carrier schematic, UNROUTED PCB, BOM and local libraries.')


if __name__=='__main__':
    main()
