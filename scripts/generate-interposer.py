#!/usr/bin/env python3
"""Generate a review-stage, self-contained KiCad interposer project.

This is not an autorouter or a fabrication tool. It emits an annotated placed
board with intentional ratsnest connections. Routing is performed in KiCad.
"""
import csv
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from xml.sax.saxutils import escape
from component_selections import apply_selections, constraints

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/pcb/interposer'


def uid(value):
    return str(uuid5(NAMESPACE_URL, 'picopower/interposer/rev-a/' + value))


def q(value):
    return json.dumps(str(value))


def write(name, value):
    (OUT / name).write_text(value, encoding='utf-8')


def csv_write(name, fields, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


HEADER = ['PI_3V3', 'PI_5V', 'GPIO2', 'PI_5V', 'GPIO3', 'GND',
          'GPIO4', 'GPIO14', 'GND', 'GPIO15', 'GPIO17', 'GPIO18',
          'GPIO27', 'GND', 'GPIO22', 'GPIO23', 'PI_3V3', 'GPIO24',
          'GPIO10', 'GND', 'GPIO9', 'GPIO25', 'GPIO11', 'GPIO8',
          'GND', 'GPIO7', 'ID_SD', 'ID_SC', 'GPIO5', 'GND',
          'GPIO6', 'GPIO12', 'GPIO13', 'GND', 'GPIO19', 'GPIO16',
          'GPIO26', 'GPIO20', 'GND', 'GPIO21']


def part(ref, value, mpn, footprint, pins, pos, size, url='', kind='passive'):
    return dict(ref=ref, value=value, mpn=mpn, footprint=footprint,
                pins={str(k): v for k, v in pins.items()}, position_mm=pos,
                body_mm=size, documentation_url=url, kind=kind)


def circuit():
    parts = [
        part('J1', 'POWER IN + / -', '1776508', 'Power_GF_2',
             {1: 'VIN_RAW', 2: 'GND'}, [14.08, 12], [20.32, 12],
             'https://www.phoenixcontact.com/en-us/products/pcb-header-mstb-25-2-gf-508-1776508'),
        part('F1', '6.3 A candidate / 5x20 holder', '0031.8201', 'Fuse_OGN_P22.5',
             {1: 'VIN_RAW', 2: 'VIN_FUSED'}, [6, 22], [28, 10],
             'https://at.schurter.com/en/datasheet/typ_OGN.pdf'),
        part('Q1', 'NMOS input', 'BSC010N04LS6ATMA1', 'SuperSO8_Draft',
             {1: 'COMMON_SOURCE', 2: 'COMMON_SOURCE', 3: 'COMMON_SOURCE',
              4: 'GATE_Q1', 5: 'VIN_FUSED'},
             [35, 21], [6, 5], 'https://www.infineon.com/part/BSC010N04LS6', 'mosfet'),
        part('Q2', 'NMOS output', 'BSC010N04LS6ATMA1', 'SuperSO8_Draft',
             {1: 'COMMON_SOURCE', 2: 'COMMON_SOURCE', 3: 'COMMON_SOURCE',
              4: 'GATE_Q2', 5: 'PROTECTED'},
             [45, 21], [6, 5], 'https://www.infineon.com/part/BSC010N04LS6', 'mosfet'),
        part('U1', 'LTC4367 protection switch', 'LTC4367IMS8#PBF', 'MSOP8_P0.65',
             {1: 'VIN_FUSED', 2: 'UV', 3: 'OV', 4: 'GND', 5: 'SHDN',
              6: None, 7: 'PROTECTED', 8: 'GATE_DRV'}, [39, 9], [3, 3],
             'https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf', 'ic'),
        part('RSH1', '5 mOhm / 0.5% / 1 W', 'WSK25125L000DEA', 'WSK2512_5m_Kelvin',
             {1: 'PROTECTED', 2: 'SENSE_PLUS', 3: 'SENSE_MINUS', 4: 'PI_5V'},
             [55, 30], [6.35, 3.18], 'https://www.vishay.com/docs/30108/wsk2512.pdf', 'shunt'),
        part('J2', '40-pin stacking socket', 'SSQ-120-03-G-D', 'Stack_2x20_P2.54',
             dict(enumerate(HEADER, 1)), [10, 42.54], [51, 5.1],
             'https://www.samtec.com/products/ssq-120-03-g-d', 'header'),
        part('J3', 'S+ / S- / VBUS / GND', 'B4B-XH-A(LF)(SN)', 'XH4_P2.5',
             {1: 'SENSE_PLUS', 2: 'SENSE_MINUS', 3: 'PI_5V', 4: 'GND'},
             [54, 8], [12.4, 5.8], 'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf'),
        part('J4', 'GND / PiTX / PiRX / MARK / Pico3V3', 'B5B-XH-A(LF)(SN)', 'XH5_P2.5',
             {1: 'GND', 2: 'PICO_RX', 3: 'PICO_TX', 4: 'PICO_MARK', 5:'PICO_3V3'},
             [6, 32], [14.9, 5.8], 'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf'),
    ]
    parts.append(part('U2', 'UART power-off buffer', 'SN74AXC4T245PWR', 'TSSOP16_P0.65',
                      {1:'PICO_3V3',2:'GND',3:'PICO_3V3',4:'PICO_RX',5:'PICO_MARK',
                       6:'PICO_TX',7:'GND',8:'GND',9:'GND',10:None,11:'GPIO15',
                       12:'GPIO17',13:'GPIO14',14:'GND',15:'GND',16:'PI_3V3'},
                      [35,29], [4.4,5],
                      'https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf', 'buffer'))
    parts.append(part('D1', 'GREEN POWER', 'APT2012LZGCK', 'LED_0805',
                      {1:'GND',2:'LED_A'}, [54,17], [2,1.25],
                      'https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf', 'led'))
    resistor_data = [
        ('R2', '10.0k 0.1%', 'OV', 'GND', [31, 7]),
        ('R3', '1.50k 0.1%', 'UV', 'OV', [31, 11]),
        ('R4', '95.3k 0.1%', 'VIN_FUSED', 'UV', [31, 15]),
        ('R5', '510k 1%', 'VIN_FUSED', 'SHDN', [40, 15]),
        ('R6', '10R', 'GATE_DRV', 'GATE_Q1', [35, 16]),
        ('R7', '10R', 'GATE_DRV', 'GATE_Q2', [46, 16]),
        ('R8', '5.1k', 'GATE_DRV', 'GATE_RC', [46, 10]),
        ('R9', '2.7k 1% 0.125W', 'PROTECTED', 'LED_A', [58, 17]),
        ('R10', '100k 1%', 'PI_3V3', 'GPIO14', [21,29]),
        ('R11', '100k 1%', 'PI_3V3', 'GPIO15', [25,29]),
        ('R12', '100k 1%', 'PICO_3V3', 'PICO_TX', [29,34]),
        ('R13', '100k 1%', 'PICO_3V3', 'PICO_RX', [33,34]),
        ('R14', '100k 1%', 'GPIO17', 'GND', [22,32]),
        ('R15', '100k 1%', 'PICO_MARK', 'GND', [37,34]),
    ]
    for ref, value, a, b, pos in resistor_data:
        parts.append(part(ref, value, '', 'R_0805', {1: a, 2: b}, pos, [2, 1.25]))
    parts += [
        part('C1', '12nF C0G 50V', '', 'R_0805', {1: 'GATE_RC', 2: 'GND'},
             [46, 6], [2, 1.25]),
        part('C2', '100nF X7R 63V', '', 'R_0805', {1: 'VIN_FUSED', 2: 'GND'},
             [24, 13], [2, 1.25]),
    ]
    parts += [part('C3', '100nF X7R 16V', '', 'C_0805', {1:'PICO_3V3',2:'GND'},
                   [34,25], [2,1.25]),
              part('C4', '100nF X7R 16V', '', 'C_0805', {1:'PI_3V3',2:'GND'},
                   [40,25], [2,1.25])]
    for ref, net, pos in [('TP1', 'PI_5V', [22.5, 35]), ('TP2', 'GND', [48, 33.7]),
                          ('TP3', 'PROTECTED', [46, 30]), ('TP4', 'VIN_FUSED', [24, 6])]:
        parts.append(part(ref, net, '', 'TestPoint_Pad_2mm', {1: net}, pos, [2, 2]))
    upper = part('J5', 'Logical HAT side of J2', '', 'Stack_2x20_P2.54',
                 dict(enumerate(HEADER, 1)), [10, 42.54], [51, 5.1], kind='header')
    upper['on_board'] = False
    upper['in_bom'] = False
    parts.append(upper)
    apply_selections('interposer', parts)
    return dict(revision='A-draft', release_status='not-for-manufacture',
                design_constraints=constraints(),
                protection_default='electronic-switch-before-shunt',
                board=dict(width_mm=67.13, height_mm=46, thickness_mm=1.6,
                           copper_um=70, layers=2, clearance_mm=0.2,
                           header_band_y_mm=36.5, routing_status='unrouted',
                           outline_mm=[[0,0],[66,0],[66,37],[67.13,37],[67.13,46],[0,46]],
                           mounting_holes=[dict(ref='H1',position_mm=[5.13,41.27]),
                                           dict(ref='H2',position_mm=[63.13,41.27])],
                           mounting_drill_mm=2.7, mounting_keepout_diameter_mm=6,
                           mounting_status='provisional; verify on physical Pi 5'),
                shunt=dict(ohms=0.005, tolerance=0.005, rated_watts=1),
                load=dict(nominal_volts=5.1, max_amperes=5),
                protection=dict(bottom_ohms=10000, middle_ohms=1500,
                                top_ohms=95300, resistor_tolerance=0.001,
                                threshold_min_volts=0.4925, threshold_max_volts=0.5075,
                                hysteresis_min_volts=0.02, hysteresis_max_volts=0.032,
                                pin_leakage_amperes=1e-8,
                                intended_fault_range_volts=[-30, 30]),
                interface=dict(buffer='SN74AXC4T245PWR', uart_baud=115200,
                               pi_side_overhead='included in DUT current; characterize static and switching load',
                               isolation_below_volts=0.1, physical_validation='not performed'),
                sources=dict(shunt_footprint='https://raw.githubusercontent.com/KiCad/kicad-footprints/master/Resistor_SMD.pretty/R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm.kicad_mod'),
                parts=parts)


def pads_for(name):
    """Return draft pads: number, x, y, width, height, drill (mm).

    LED and WSK pad dimensions and header pitch are sourced. Remaining outlines are
    explicitly marked draft and need matching to manufacturer drawings.
    """
    if name == 'R_0805_TNPW':
        return [('1',-.95,0,.9,1.45,0),('2',.95,0,.9,1.45,0)]
    if name == 'C_0805_Murata':
        return [('1',-.9,0,.6,1.25,0),('2',.9,0,.6,1.25,0)]
    if name == 'C_0805_KEMET':
        return [('1',-.9,0,1.15,1.45,0),('2',.9,0,1.15,1.45,0)]
    if name == 'LED_0805':
        return [('1',-1.175,0,1.25,1.1,0),('2',1.175,0,1.25,1.1,0)]
    if name == 'Stack_2x20_P2.54':
        return [(str(n), ((n - 1) // 2) * 2.54, 0 if n % 2 else -2.54,
                 1.8, 1.8, 1.0) for n in range(1, 41)]
    if name == 'WSK2512_5m_Kelvin':
        return [('1', -2.985, -0.635, 2.29, 2.03, 0),
                ('4', 2.985, 0.635, 2.29, 2.03, 0),
                ('2', -3.28, 1.27, 1.7, 0.76, 0),
                ('3', 3.28, -1.27, 1.7, 0.76, 0)]
    if name == 'TSSOP16_P0.65':
        return [(str(n),-3.1 if n<=8 else 3.1,
                 (n-4.5)*.65 if n<=8 else (12.5-n)*.65, 1.5,.45,0) for n in range(1,17)]
    if name == 'MSOP8_P0.65':
        return [(str(n), -2.15 if n <= 4 else 2.15,
                 (n - 2.5) * .65 if n <= 4 else (6.5 - n) * .65,
                 1.45, .4, 0) for n in range(1, 9)]
    if name == 'SuperSO8_Draft':
        return [(str(n), -2.6 if n <= 4 else 2.6,
                 (n - 2.5) * 1.27 if n <= 4 else (6.5 - n) * 1.27,
                 1.6, .75, 0) for n in range(1, 9)]
    if name == 'Power_GF_2':
        return [('1', 0, 0, 3.4, 3.4, 1.4), ('2', 5.08, 0, 3.4, 3.4, 1.4)]
    if name == 'Fuse_OGN_P22.5':
        return [('1', 0, 0, 3.2, 3.2, 1.3), ('2', 22.5, 0, 3.2, 3.2, 1.3)]
    if name in ['XH4_P2.5','XH5_P2.5']:
        return [(str(n), (n - 1) * 2.5, 0, 1.8, 1.8, 1) for n in range(1, 5 if name=='XH4_P2.5' else 6)]
    if name == 'TestPoint_Pad_2mm':
        return [('1', 0, 0, 2, 2, 0)]
    return [('1', -1, 0, 1.2, 1.4, 0), ('2', 1, 0, 1.2, 1.4, 0)]


def footprint(part, nets, standalone=False):
    name, ref = part['footprint'], part['ref']
    x, y = part['position_mm']
    lines = [f'(footprint {q(name if standalone else "PicoPower:" + name)}']
    if standalone:
        lines.append('  (version 20240108) (generator "pcbnew")')
    lines.append('  (layer "F.Cu")')
    if not standalone:
        lines += [f'  (at {x} {y}) (uuid "{uid(ref)}")',
                  f'  (path "/{uid("sheet")}/{uid("symbol/" + ref)}")']
    lines += [f'  (descr "PicoPower review footprint; verify manufacturer drawing before routing/release")',
              f'  (property "Reference" {q("REF**" if standalone else ref)} (at 0 -4) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
              f'  (property "Value" {q(part["value"])} (at 0 4) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))']
    if not standalone:
        lines += [f'  (property {q(key)} {q(value)} (at 0 0) (layer "F.Fab") hide (effects (font (size 1 1) (thickness .15))))'
                  for key, value in [('MPN', part['mpn']), ('Datasheet', part['documentation_url'])]]
    pads = pads_for(name)
    w, h = part['body_mm']
    if name == 'Stack_2x20_P2.54':
        xa, ya, xb, yb = -1.5, -4.04, 49.76, 1.5
    elif name in ['Fuse_OGN_P22.5', 'Power_GF_2', 'XH4_P2.5', 'XH5_P2.5']:
        center_x = (pads[0][1] + pads[-1][1]) / 2
        xa, ya, xb, yb = center_x - w/2, -h/2, center_x + w/2, h/2
    else:
        xa, ya, xb, yb = -w/2, -h/2, w/2, h/2
    lines.append(f'  (fp_rect (start {xa} {ya}) (end {xb} {yb}) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))')
    for n, px, py, pw, ph, drill in pads:
        net = part['pins'].get(n)
        typ = 'thru_hole' if drill else 'smd'
        layers = '"*.Cu" "*.Mask"' if drill else '"F.Cu" "F.Paste" "F.Mask"'
        drilling = f' (drill {drill})' if drill else ''
        netstr = f' (net {nets[net]} {q(net)})' if net and not standalone else ''
        lines.append(f'  (pad {q(n)} {typ} rect (at {px} {py}) (size {pw} {ph}){drilling} (layers {layers}){netstr})')
    lines.append(')')
    return '\n'.join(lines)


def pcb(data):
    nets = {name: i for i, name in enumerate(sorted({n for p in data['parts'] for n in p['pins'].values() if n}), 1)}
    lines = ['(kicad_pcb (version 20240108) (generator "pcbnew")',
             '  (general (thickness 1.6)) (paper "A4")',
             '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (46 "B.CrtYd" user "b.courtyard") (47 "F.CrtYd" user "f.courtyard") (48 "B.Fab" user) (49 "F.Fab" user))',
             '  (setup (pad_to_mask_clearance 0))', '  (net 0 "")']
    lines += [f'  (net {code} {q(name)})' for name, code in nets.items()]
    lines += [footprint(p, nets) for p in data['parts'] if p.get('on_board', True)]
    outline=data['board']['outline_mm']
    for a,b in zip(outline,outline[1:]+outline[:1]):
        lines.append(f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width .05) (type solid)) (layer "Edge.Cuts"))')
    lines += [
              '  (gr_text "PICOPOWER REV A DRAFT\\nNOT FOR MANUFACTURE" (at 40 30) (layer "B.SilkS") (effects (font (size .8 .8) (thickness .12)) (justify mirror)))',
              '  (gr_text "5.1V DC" (at 21 16) (layer "F.SilkS") (effects (font (size .9 .9) (thickness .15))))',
              '  (gr_text "+" (at 14.08 16) (layer "F.SilkS") (effects (font (size .9 .9) (thickness .15))))',
              '  (gr_text "-" (at 9 16) (layer "F.SilkS") (effects (font (size .9 .9) (thickness .15))))',
              '  (gr_text "POWER" (at 54 20) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))',
              '  (gr_text "PIN 1 / 3V3" (at 8 45) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12))))',
              '  (gr_text "OUTWARD WING / KEEP COOLER CLEAR" (at 43 2) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))', ')']
    return '\n'.join(lines) + '\n'


def pin_layout(part):
    pins = list(part['pins'])
    if part['kind'] == 'header':
        left, right = pins[::2], pins[1::2]
    else:
        mid = (len(pins) + 1) // 2
        left, right = pins[:mid], pins[mid:]
    rows = max(len(left), len(right))
    result = []
    for group, side in [(left, -1), (right, 1)]:
        for i, n in enumerate(group):
            result.append((n, side * 12.7, ((rows - 1)/2 - i) * 2.54, 0 if side == -1 else 180))
    return result, max(5.08, rows * 2.54 / 2 + 1.27)


def pin_name(part, n):
    if part['ref'] == 'U1':
        return {'1':'VIN', '2':'UV', '3':'OV', '4':'GND', '5':'SHDN', '6':'FAULT_N', '7':'VOUT', '8':'GATE'}[n]
    if part['ref']=='U2':
        return {'1':'VCCA','2':'1DIR','3':'2DIR','4':'1A1','5':'1A2','6':'2A1','7':'2A2',
                '8':'GND','9':'GND','10':'2B2','11':'2B1','12':'1B2','13':'1B1',
                '14':'2OE_N','15':'1OE_N','16':'VCCB'}[n]
    if part['kind'] == 'led':
        return 'K' if n=='1' else 'A'
    if part['kind'] == 'mosfet':
        return 'S' if n in ['1', '2', '3'] else 'G' if n == '4' else 'D'
    if part['kind'] == 'shunt':
        return {'1':'I+', '2':'E+', '3':'E-', '4':'I-'}[n]
    return part['pins'][n] or 'NC'


def symbol_definition(part, standalone=False):
    ref = part['ref']
    name = ref if standalone else 'PicoPower:' + ref
    coords, h = pin_layout(part)
    lines = [f'    (symbol {q(name)} (pin_names (offset .508)) (in_bom yes) (on_board yes)',
             f'      (property "Reference" {q(ref)} (at 0 {h+2.54} 0) (effects (font (size 1.27 1.27))))',
             f'      (property "Value" {q(part["value"])} (at 0 {-h-2.54} 0) (effects (font (size 1.27 1.27))))',
             f'      (property "Footprint" {q("PicoPower:" + part["footprint"])} (at 0 0 0) (effects (font (size 1 1)) hide))',
             f'      (symbol {q(ref + "_0_1")}',
             f'        (rectangle (start -7.62 {h}) (end 7.62 {-h}) (stroke (width .254) (type default)) (fill (type background))))',
             f'      (symbol {q(ref + "_1_1")}']
    for n, x, y, angle in coords:
        typ = 'passive'
        if ref == 'U2':
            typ = 'power_in' if n in ['1','8','9','16'] else 'input' if n in ['2','3','7','11','12','13','14','15'] else 'output'
        if ref == 'U1':
            typ = 'power_in' if n in ['1', '4', '7'] else 'output' if n == '8' else 'open_collector' if n == '6' else 'input'
        lines.append(f'        (pin {typ} line (at {x} {y} {angle}) (length 5.08) (name {q(pin_name(part,n))} (effects (font (size 1 1)))) (number {q(n)} (effects (font (size 1 1)))))')
    lines += ['      )', '    )']
    return '\n'.join(lines)


def schematic(data):
    lines = ['(kicad_sch (version 20231120) (generator "eeschema")',
             f'  (uuid "{uid("sheet")}") (paper "A2")',
             '  (title_block (title "PicoPower Pi 5 power-and-sensing interposer") (date "2026-10-13") (rev "A DRAFT") (comment 1 "NOT FOR MANUFACTURE: routing, footprint and mechanical review required"))',
             '  (lib_symbols']
    lines += [symbol_definition(p) for p in data['parts']]
    # Flag supplies driven externally or through passive power-path components.
    lines += ['    (symbol "PicoPower:SupplyFlag" (pin_names (offset 0)) (in_bom no) (on_board no)',
              '      (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)) hide))',
              '      (property "Value" "PWR_FLAG" (at 0 2.54 0) (effects (font (size 1 1))))',
              '      (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1))))))', '    )', '  )']
    placements = {}
    for i, p in enumerate([p for p in data['parts'] if p['kind'] != 'header']):
        placements[p['ref']] = (45 + (i % 5)*68, 40 + (i // 5)*51)
    placements['J2'] = (375, 80)
    placements['J5'] = (375, 180)
    for p in data['parts']:
        ref = p['ref']
        x, y = [round(v / 1.27) * 1.27 for v in placements[ref]]
        coords, h = pin_layout(p)
        lines += [f'  (symbol (lib_id "PicoPower:{ref}") (at {x} {y} 0) (unit 1) (in_bom {"yes" if p.get("in_bom", True) else "no"}) (on_board {"yes" if p.get("on_board", True) else "no"}) (dnp no) (uuid "{uid("symbol/" + ref)}")',
                  f'    (property "Reference" {q(ref)} (at {x} {y-h-3} 0) (effects (font (size 1.27 1.27))))',
                  f'    (property "Value" {q(p["value"])} (at {x} {y+h+3} 0) (effects (font (size 1 1))))',
                  f'    (property "Footprint" {q("PicoPower:" + p["footprint"])} (at {x} {y} 0) (effects (font (size 1 1)) hide))']
        lines += [f'    (property "MPN" {q(p["mpn"])} (at {x} {y} 0) (effects (font (size 1 1)) hide))',
                  f'    (property "Datasheet" {q(p["documentation_url"])} (at {x} {y} 0) (effects (font (size 1 1)) hide))']
        lines += [f'    (pin {q(n)} (uuid "{uid("pin/" + ref + "/" + n)}"))' for n in p['pins']]
        lines += [f'    (instances (project "interposer" (path "/{uid("sheet")}" (reference {q(ref)}) (unit 1))))', '  )']
        for n, px, py, angle in coords:
            net = p['pins'][n]
            # Symbol Y coordinates point up; schematic document Y points down.
            dx, dy = x+px, y-py
            if net:
                lines.append(f'  (label {q(net)} (at {dx} {dy} {angle}) (effects (font (size .9 .9)) (justify {"right" if angle == 0 else "left"} bottom)) (uuid "{uid("label/" + ref + "/" + n)}"))')
            else:
                lines.append(f'  (no_connect (at {dx} {dy}) (uuid "{uid("nc/" + ref + "/" + n)}"))')
    for i, net in enumerate(['VIN_FUSED', 'GND', 'PROTECTED','PI_3V3','PICO_3V3']):
        x, y = [round(v / 1.27) * 1.27 for v in (30 + 35*i, 385)]
        ref = '#FLG0' + str(i+1)
        lines += [f'  (symbol (lib_id "PicoPower:SupplyFlag") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref)}")',
                  f'    (property "Reference" {q(ref)} (at {x} {y} 0) (effects (font (size 1 1)) hide))',
                  f'    (property "Value" "PWR_FLAG" (at {x} {y-2.54} 0) (effects (font (size 1 1))))',
                  f'    (instances (project "interposer" (path "/{uid("sheet")}" (reference {q(ref)}) (unit 1))))', '  )',
                  f'  (label {q(net)} (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(ref+"/label")}"))']
    lines += ['  (text "DRAFT: no Pi connection before protection / footprint / thermal validation.\\nCurrent: shunt pads 1 -> 4. Kelvin: pads 2 (+) and 3 (-).\\nSupply: 5.1 V only. Controller and its VOUT supply remain before shunt.\\nNo bulk capacitance after shunt. Pi-side UART buffer overhead IS measured.\\nJ2 is one continuous long-tail socket with male pass-through." (at 230 375 0) (effects (font (size 1.3 1.3)) (justify left)) (uuid "'+uid('notes')+'"))', ')']
    return '\n'.join(lines) + '\n'


def previews(data):
    start = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 760"><rect width="1100" height="760" fill="#f8fafc"/><g font-family="sans-serif" fill="#172536">'
    a = [start, '<text x="35" y="40" font-size="25">PicoPower — rev A placement draft</text>',
         '<text x="35" y="68" font-size="16" fill="#b45309">Provisional geometry; routed native-footprint view: layout-front.svg</text>',
         '<g transform="translate(120 100) scale(12)">',
         '<polygon points="0,0 66,0 66,37 67.13,37 67.13,46 0,46" fill="#edf4f0" stroke="#274c41" stroke-width=".2"/>',
         '<rect x="0" y="36.5" width="66" height="9.5" fill="#e0e7ff"/>',
         '<text x="22" y="39" font-size="1">COMPONENT-FREE HEADER BAND</text>']
    for p in data['parts']:
        if not p.get('on_board', True): continue
        x, y = p['position_mm']; w, h = p['body_mm']; name=p['footprint']
        if name=='Stack_2x20_P2.54':
            cx,cy=x+24.13,y-1.27
        elif name in ['Fuse_OGN_P22.5','Power_GF_2','XH4_P2.5']:
            pads=pads_for(name);cx=x+(pads[0][1]+pads[-1][1])/2;cy=y
        else:cx,cy=x,y
        a.append(f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" fill="#ffffff" stroke="#64748b" stroke-width=".12"/>')
        a.append(f'<text x="{cx}" y="{cy-h/2-.7}" text-anchor="middle" font-size=".9">{escape(p["ref"])}</text>')
        for n,px,py,pw,ph,drill in pads_for(name):
            net=p['pins'].get(n);col='#dc2626' if net in ['PI_5V','PROTECTED','VIN_RAW','VIN_FUSED'] else '#1e293b' if net=='GND' else '#d97706'
            a.append(f'<rect x="{x+px-pw/2}" y="{y+py-ph/2}" width="{pw}" height="{ph}" fill="{col}" opacity=".7"/>')
            if drill:a.append(f'<circle cx="{x+px}" cy="{y+py}" r="{drill/2}" fill="#fff"/>')
    for hole in data['board']['mounting_holes']:
        x,y=hole['position_mm']
        a.append(f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="#b45309" stroke-width=".15" stroke-dasharray=".3 .3"/>')
        a.append(f'<circle cx="{x}" cy="{y}" r="1.35" fill="#fff" stroke="#274c41" stroke-width=".15"/>')
        a.append(f'<text x="{x}" y="{y-3.5}" text-anchor="middle" font-size=".9">{hole["ref"]}</text>')
    a += ['</g>', '<text x="120" y="688" font-size="16">Envelope: 67.13 × 46 mm. H1/H2: 2.7 mm holes, 58 mm apart; provisional fit.</text>',
          '<text x="120" y="713" font-size="16">Fit, flange holes, connector derating and copper routing require review.</text>', '</g></svg>']
    write('placement.svg','\n'.join(a))
    b = [start, '<text x="35" y="40" font-size="25">PicoPower — power and measurement boundary</text>',
         '<text x="35" y="68" font-size="16" fill="#b45309">Review diagram; editable electrical schematic is interposer.kicad_sch</text>']
    blocks=[(40,'J1 / Korad','5.1 V input'),(240,'F1','replaceable fuse'),(440,'U1 + Q1/Q2','protection switch'),(650,'RSH1','5 mΩ Kelvin shunt'),(860,'J2 / Pi + HAT','measured load')]
    for x, title, subtitle in blocks:
        b += [f'<rect x="{x}" y="150" width="180" height="100" rx="7" fill="#fff" stroke="#334155" stroke-width="2"/>',
              f'<text x="{x+90}" y="185" text-anchor="middle" font-size="17">{escape(title)}</text>',
              f'<text x="{x+90}" y="215" text-anchor="middle" font-size="14">{escape(subtitle)}</text>']
        if x<860:b.append(f'<path d="M{x+180} 200 H{x+200}" stroke="#dc2626" stroke-width="3"/>')
    b += ['<path d="M705 250 V350 H520 M770 250 V380 H520 M950 250 V410 H520" fill="none" stroke="#2563eb" stroke-width="2"/>',
          '<rect x="300" y="320" width="220" height="140" rx="7" fill="#fff" stroke="#334155" stroke-width="2"/>',
          '<text x="410" y="350" text-anchor="middle" font-size="19">INA229EVM</text>',
          '<text x="410" y="380" text-anchor="middle" font-size="15">SENSE+ / SENSE− / VBUS</text>',
          '<text x="410" y="415" text-anchor="middle" font-size="15">Powered from Pico 3.3 V</text>',
          '<rect x="40" y="320" width="180" height="140" rx="7" fill="#fff" stroke="#334155" stroke-width="2"/>',
          '<text x="130" y="365" text-anchor="middle" font-size="20">Pico 2 W</text>',
          '<text x="130" y="400" text-anchor="middle" font-size="15">Separate USB power</text>',
          '<path d="M220 390 H300" stroke="#334155" stroke-width="2"/>',
          '<text x="260" y="380" text-anchor="middle" font-size="14">SPI</text>',
          '<text x="45" y="530" font-size="17">Protection supply currents and capacitor are before the shunt.</text>',
          '<text x="45" y="565" font-size="17">Energy = integral of header-bus voltage × shunt current.</text>',
          '<text x="45" y="600" font-size="17">Header-contact / return-path losses require characterization.</text>',
          '<text x="45" y="635" font-size="17">No converter or LED load on measured rail; Pi-side UART buffer overhead IS included.</text>',
          '</g></svg>']
    write('schematic.svg','\n'.join(b))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data = circuit()
    write('circuit.json',json.dumps(data,indent=2)+'\n')
    write('interposer.kicad_pcb',pcb(data))
    write('interposer.kicad_sch',schematic(data))
    write('interposer.kicad_pro',json.dumps({
        'meta':{'filename':'interposer.kicad_pro','version':1},
        'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.2}}},
        'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.3,
                                   'via_diameter':.8,'via_drill':.4,
                                   'microvia_diameter':.3,'microvia_drill':.1}]}
    },indent=2)+'\n')
    lib = OUT / 'PicoPower.pretty';lib.mkdir(exist_ok=True)
    for p in data['parts']:
        (lib/(p['footprint']+'.kicad_mod')).write_text(footprint(p,{},True)+'\n')
    write('PicoPower.kicad_sym','(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+
          '\n'.join(symbol_definition(p,True) for p in data['parts'])+'''
    (symbol "SupplyFlag" (pin_names (offset 0)) (in_bom no) (on_board no)
      (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)) hide))
      (property "Value" "PWR_FLAG" (at 0 2.54 0) (effects (font (size 1 1))))
      (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0)
        (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1))))))
    )
)
''')
    write('fp-lib-table','(fp_lib_table (lib (name "PicoPower") (type "KiCad") (uri "${KIPRJMOD}/PicoPower.pretty") (options "") (descr "Review-stage footprints")))\n')
    write('sym-lib-table','(sym_lib_table (lib (name "PicoPower") (type "KiCad") (uri "${KIPRJMOD}/PicoPower.kicad_sym") (options "") (descr "Self-contained review symbols")))\n')
    csv_write('pinout.csv',['connector','pin','net'],[
        {'connector':p['ref'],'pin':n,'net':net or 'NC'}
        for p in data['parts'] if p['ref'].startswith('J') for n,net in p['pins'].items()])
    csv_write('board-bom.csv',['reference','value','manufacturer_reference','footprint','documentation_url','status'],[
        {'reference':p['ref'],'value':p['value'],'manufacturer_reference':p['mpn'],
         'footprint':'PicoPower:'+p['footprint'],'documentation_url':p['documentation_url'],
         'status':'draft; footprint review required'} for p in data['parts'] if p.get('in_bom', True)])
    previews(data)
    print('Generated circuit, editable schematic, UNROUTED board, libraries, BOM and previews.')
    print('No Gerbers generated. Complete routing and all release checks before fabrication.')


if __name__=='__main__':
    main()
