#!/usr/bin/env python3
"""Check circuit invariants and component arithmetic, not physical safety."""
import argparse
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'hardware/pcb/interposer'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_circuit(data):
    parts = {p['ref']: p for p in data['parts']}
    require(len(parts) == len(data['parts']), 'Duplicate reference')
    pins = {ref: p['pins'] for ref, p in parts.items()}
    require(pins['J1'] == {'1':'VIN_RAW','2':'GND'}, 'Input polarity mapping changed')
    require(pins['F1'] == {'1':'VIN_RAW','2':'VIN_FUSED'}, 'Fuse must precede protection and shunt')
    require(pins['RSH1'] == {'1':'PROTECTED','2':'SENSE_PLUS','3':'SENSE_MINUS','4':'PI_5V'},
            'Shunt must have distinct current and Kelvin nets, correct polarity')
    require(pins['U1']['1'] == 'VIN_FUSED' and pins['U1']['7'] == 'PROTECTED',
            'Controller VIN and VOUT currents must both remain upstream of shunt')
    require(pins['Q1']['1'] == pins['Q2']['1'] == 'COMMON_SOURCE', 'MOSFETs must be source-to-source')
    require(pins['Q1']['5']=='VIN_FUSED' and pins['Q2']['5']=='PROTECTED',
            'MOSFET drain orientation changed')
    require(pins['J2']['2'] == pins['J2']['4'] == 'PI_5V', 'Both Pi 5 V pins must be powered')
    ground_pins = ['6','9','14','20','25','30','34','39']
    require([n for n in pins['J2'] if pins['J2'][n]=='GND'] == ground_pins, 'Pi ground pin mapping changed')
    require(len(pins['J2']) == 40 and set(pins['J2']) == {str(n) for n in range(1,41)}, 'Header incomplete')
    require(pins['J2']['1'] == pins['J2']['17'] == 'PI_3V3', '3V3 must not be driven from input power')
    for p in parts.values():
        if p['ref'] not in ['RSH1','J2','J3','J5','TP1']:
            require('PI_5V' not in p['pins'].values(), f'{p["ref"]} adds an unintended downstream load/bypass')
        require(not (p['ref'].startswith('C') and 'PI_5V' in p['pins'].values()), 'Downstream capacitor shifts task energy')
    require(pins['J3'] == {'1':'SENSE_PLUS','2':'SENSE_MINUS','3':'PI_5V','4':'GND'}, 'Sense cable mapping changed')
    require(pins['J4'] == {'1':'GND','2':'PICO_RX','3':'PICO_TX','4':'PICO_MARK','5':'PICO_3V3'},
            'UART connector must expose buffered signals and separate Pico supply')
    expected_buffer={'1':'PICO_3V3','2':'GND','3':'PICO_3V3','4':'PICO_RX','5':'PICO_MARK',
                     '6':'PICO_TX','7':'GND','8':'GND','9':'GND','10':None,'11':'GPIO15',
                     '12':'GPIO17','13':'GPIO14','14':'GND','15':'GND','16':'PI_3V3'}
    require(pins['U2']==expected_buffer, 'Buffer rail, direction, channel or enable mapping changed')
    bias={'R10':('PI_3V3','GPIO14'),'R11':('PI_3V3','GPIO15'),
          'R12':('PICO_3V3','PICO_TX'),'R13':('PICO_3V3','PICO_RX'),
          'R14':('GPIO17','GND'),'R15':('PICO_MARK','GND')}
    for ref,(a,b) in bias.items():
        require(pins[ref]=={'1':a,'2':b} and parts[ref]['value']=='100k 1%',
                f'{ref} must bias its signal on its own power domain')
    require(pins['C3']=={'1':'PICO_3V3','2':'GND'} and pins['C4']=={'1':'PI_3V3','2':'GND'},
            'Buffer decoupling must remain on separate power domains')
    for p in parts.values():
        nets=set(p['pins'].values())
        if p['ref']!='U2':
            require(not {'PI_3V3','PICO_3V3'}<=nets, 'Independent buffer supplies are bridged')
            require(not (nets & {'GPIO14','GPIO15','GPIO17'} and nets & {'PICO_RX','PICO_TX','PICO_MARK'}),
                    'Direct signal bypass around power-off buffer')
    # A passive part may not join the load bus to any upstream supply except RSH1.
    upstream = {'VIN_RAW','VIN_FUSED','PROTECTED','COMMON_SOURCE'}
    for p in parts.values():
        nets = set(p['pins'].values())
        require(p['ref']=='RSH1' or not ('PI_5V' in nets and nets & upstream), f'Shunt bypass through {p["ref"]}')
    require(pins['D1']=={'1':'GND','2':'LED_A'}, 'LED polarity/return changed')
    require(pins['R9']=={'1':'PROTECTED','2':'LED_A'}, 'Power LED must remain upstream of shunt')
    b = data['board']
    for p in parts.values():
        x,y = p['position_mm']
        require(0 < x < b['width_mm'] and 0 < y < b['height_mm'], f'{p["ref"]} origin outside board')
        require(p['kind']=='header' or y+p['body_mm'][1]/2 < b['header_band_y_mm'],
                f'{p["ref"]} body obstructs component-free header band')
    shunt = data['shunt'];current=data['load']['max_amperes']
    require(current**2*shunt['ohms'] < shunt['rated_watts']/2, 'Insufficient nominal shunt power margin')
    pr=data['protection'];values=[pr['bottom_ohms'],pr['middle_ohms'],pr['top_ohms']]
    total=sum(values);uv=.5*total/sum(values[:2]);ov=.5*total/values[0]
    uv_trips=[];ov_trips=[];uv_restarts=[];ov_restarts=[]
    for signs in itertools.product([-1,1],repeat=3):
        r=[v*(1+s*pr['resistor_tolerance']) for v,s in zip(values,signs)]
        for threshold in [pr['threshold_min_volts'],pr['threshold_max_volts']]:
            uv_trips.append(threshold*sum(r)/sum(r[:2]))
            ov_trips.append(threshold*sum(r)/r[0])
            for hyst in [pr['hysteresis_min_volts'],pr['hysteresis_max_volts']]:
                uv_restarts.append((threshold+hyst)*sum(r)/sum(r[:2]))
                ov_restarts.append((threshold-hyst)*sum(r)/r[0])
    require(max(uv_restarts) < data['load']['nominal_volts'] < min(ov_trips),
            'Normal input not inside worst-case operating window')
    report = dict(source_checks='passed',physical_validation='not performed',
                  routing_status=b['routing_status'],
                  interface=dict(pi_side_overhead='included; physical characterization pending',
                                 power_off_validation='not performed',uart_baud=115200),
                  shunt_at_max_current=dict(voltage_drop_V=current*shunt['ohms'],power_W=current**2*shunt['ohms']),
                  protection_input_thresholds_V=dict(uv_nominal=uv,ov_nominal=ov,
                      uv_trip_resistor_comparator_range=[min(uv_trips),max(uv_trips)],
                      ov_trip_resistor_comparator_range=[min(ov_trips),max(ov_trips)],
                      uv_restart_range=[min(uv_restarts),max(uv_restarts)],
                      ov_restart_range=[min(ov_restarts),max(ov_restarts)]),
                  limitations=['Threshold ranges exclude leakage and transient response.',
                               'OV cutoff does not establish a Pi-safe output maximum.',
                               'ERC/DRC do not validate footprints, mechanics, transient behavior or load temperature.'])
    return report


def check_balanced(path):
    """Catch truncated/invalidly quoted S-expressions; not a KiCad parser."""
    s=path.read_text();quoted=False;escaped=False;depth=0
    for c in s:
        if quoted:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='(':depth+=1
        elif c==')':
            depth-=1
            require(depth>=0,f'{path.name}: unbalanced close')
    require(not quoted and depth==0,f'{path.name}: truncated S-expression')


def kicad_check(mode):
    cli=shutil.which('kicad-cli')
    if not cli:
        raise SystemExit('KiCad CLI is unavailable. Install KiCad 9; this check has NOT passed.')
    out=ROOT/'.build/hardware';out.mkdir(parents=True,exist_ok=True)
    if mode=='erc':
        cmd=[cli,'sch','erc','--exit-code-violations','-o',str(out/'erc.rpt'),str(DESIGN/'interposer.kicad_sch')]
    else:
        cmd=[cli,'pcb','drc','--schematic-parity','--exit-code-violations','-o',str(out/'drc.rpt'),str(DESIGN/'interposer.kicad_pcb')]
    env=os.environ.copy()
    for key,subdir in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
        target=ROOT/'.build/kicad'/subdir;target.mkdir(parents=True,exist_ok=True)
        env[key]=str(target)
    result=subprocess.run(cmd,check=False,env=env)
    raise SystemExit(result.returncode)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--kicad',choices=['erc','drc']);args=parser.parse_args()
    if args.kicad:kicad_check(args.kicad)
    data=json.loads((DESIGN/'circuit.json').read_text())
    report=check_circuit(data)
    for suffix in ['.kicad_pcb','.kicad_sch','.kicad_sym']:
        for path in DESIGN.glob('*'+suffix):check_balanced(path)
    for path in (DESIGN/'PicoPower.pretty').glob('*.kicad_mod'):check_balanced(path)
    pcb=(DESIGN/'interposer.kicad_pcb').read_text()
    # All 40 pass-through pins must exist, even when they have no branch.
    require(all(f'(pad "{n}" thru_hole' in pcb for n in range(1,41)), 'PCB lacks header pads')
    for part in data['parts']:
        if part.get('on_board', True):
            require(f'(property "Reference" "{part["ref"]}"' in pcb,f'Missing PCB part {part["ref"]}')
        require(f'(lib_id "PicoPower:{part["ref"]}")' in (DESIGN/'interposer.kicad_sch').read_text(),
                f'Missing schematic part {part["ref"]}')
    out=ROOT/'.build/hardware';out.mkdir(parents=True,exist_ok=True)
    (out/'source-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
