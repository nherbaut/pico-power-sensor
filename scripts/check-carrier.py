#!/usr/bin/python3
"""Check the carrier's metrology boundary, connector mappings and native CAD."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/pcb/carrier'


def require(condition,message):
    if not condition:raise ValueError(message)


def check_circuit(data):
    parts={p['ref']:p for p in data['parts']}
    require(len(parts)==len(data['parts']),'Duplicate component reference')
    pins={ref:p['pins'] for ref,p in parts.items()}
    require(pins['J_UART']=={'1':'GND','2':'PICO_RX','3':'PICO_TX','4':'PICO_MARK','5':'PICO_3V3'},
            'Carrier connector must match interposer J4 without cable crossover')
    require(pins['J_SENSE']=={'1':'SENSE_PLUS','2':'SENSE_MINUS','3':'SENSE_VBUS','4':'GND'},
            'Sense connector must match interposer J3 without cable crossover')
    # INA229 DGS VSSOP-10 pinout, TI SLYS023A table 5-1.
    require(pins['U_PM']=={'1':'CS','2':'MOSI','3':'ALERT','4':'MISO','5':'SCLK','6':'PICO_3V3',
                           '7':'GND','8':'SENSE_VBUS','9':'SENSE_MINUS','10':'SENSE_PLUS'},
            'INA229 pin mapping, SPI, supply or sense polarity changed')
    require(parts['U_PM']['mpn']=='INA229AIDGSR','Power monitor must be the INA229 VSSOP-10')
    pico=pins['J_PICO']
    require(len(pico)==40,'Pico header must preserve all 40 physical pins')
    for n,net in {'1':'PICO_TX','2':'PICO_RX','4':'PICO_MARK','5':'ALERT','6':'MISO',
                  '7':'CS','9':'SCLK','10':'MOSI','36':'PICO_3V3'}.items():
        require(pico[n]==net,f'Pico physical pin {n} must connect to {net}')
    require(all(pico[n] is None for n in ['37','39']) and pico['40']=='USB_5V',
            '3V3_EN and VSYS must be NC; VBUS powers only the SD regulator')
    require([n for n,net in pico.items() if net=='GND']==['3','8','13','18','23','28','33','38'],
            'Pico ground pins changed')
    reserved={0,1,2,3,4,5,6,7,12,13,14,15}
    require(data['gpio']['leds']==[27,26,22,21,20] and not set(data['gpio']['leds'])&reserved,
            'LED GPIO allocation conflicts with another instrument interface')
    for n,physical in enumerate([32,31,29,27,26],1):
        signal=f'LED{n}_GPIO';anode=f'LED{n}_A'
        require(pico[str(physical)]==signal,'LED connected to wrong Pico pin')
        require(pins[f'D{n}']=={'1':'GND','2':anode},'LED polarity or return changed')
        require(pins[f'R_LED{n}']=={'1':signal,'2':anode} and parts[f'R_LED{n}']['value']=='1k 1%',
                'Each LED needs its own 1k current-limiting resistor')
        require(pins[f'R_PD{n}']=={'1':signal,'2':'GND'} and parts[f'R_PD{n}']['value']=='100k 1%',
                'Each indicator GPIO needs its reset pull-down')
    forbidden={'PI_5V','PI_3V3','VIN_RAW','PROTECTED'}
    require(not forbidden&{net for p in parts.values() for net in p['pins'].values()},
            'DUT power connection on carrier violates measurement boundary')
    # Analog sense nets belong only on the sense connector and the INA229 inputs.
    sense={'SENSE_PLUS','SENSE_MINUS','SENSE_VBUS'}
    for ref,p in parts.items():
        require(ref in ('J_SENSE','U_PM') or not sense&set(p['pins'].values()),
                'Analog sense connection reaches a part other than J_SENSE or U_PM (measurement boundary)')
    require(pins['C1']==pins['C2']=={'1':'PICO_3V3','2':'GND'},'Sensor 3V3 decoupling changed')
    require(pins['C_PM']=={'1':'PICO_3V3','2':'GND'},'INA229 supply bypass changed')
    require(pins['R_ALERT']=={'1':'PICO_3V3','2':'ALERT'},'INA229 open-drain ALERT needs a pull-up')
    require(pins['R_CS']=={'1':'PICO_3V3','2':'CS'},'Chip select must idle high')
    require(pins['J_SD']=={'1':'SD_DAT2','2':'SD_CS','3':'SD_MOSI','4':'SD_3V3',
                          '5':'SD_SCLK','6':'GND','7':'SD_MISO','8':'SD_DAT1','9':'GND'},
            'SD socket pinout, voltage or shield ground changed')
    require(pins['U_SD']=={'1':'USB_5V','2':'GND','3':'PICO_3V3','4':None,'5':'SD_3V3'},
            'SD regulator must use USB 5V with separate 3V3 output and Pico-powered enable')
    for n,net in {'16':'SD_MISO','17':'SD_CS','19':'SD_SCLK','20':'SD_MOSI'}.items():
        require(pico[n]==net,'SD SPI1 allocation changed')
    require({key:data['gpio'][key] for key in ['sd_spi','sd_miso','sd_cs','sd_sclk','sd_mosi']}==
            dict(sd_spi=1,sd_miso=12,sd_cs=13,sd_sclk=14,sd_mosi=15),'SD must use dedicated SPI1')
    for n,signal in enumerate(['SD_DAT2','SD_CS','SD_MOSI','SD_MISO','SD_DAT1'],1):
        require(pins[f'R_SDP{n}']=={'1':'SD_3V3','2':signal} and parts[f'R_SDP{n}']['value']=='10k 1%',
                'SD CMD and DAT0-3 require pull-ups on the SD supply domain')
    for p in parts.values():
        nets=set(p['pins'].values())
        require(p['ref']=='U_SD' or not {'SD_3V3','PICO_3V3'}<=nets,
                'SD and sensor 3V3 rails must not be bridged')
        if 'USB_5V' in nets:
            require(p['ref'] in ['J_PICO','U_SD','C_SDIN'],'Unexpected USB 5V load or bypass')
    require(pins['C_SDIN']=={'1':'USB_5V','2':'GND'},'SD LDO input decoupling changed')
    for ref in ['C_SDOUT','C_SDBULK','C_SDSOCKET']:
        require(pins[ref]=={'1':'SD_3V3','2':'GND'},'SD output decoupling changed')
    require(parts['C_SDIN']['value']==parts['C_SDOUT']['value']=='4.7uF X7R 16V',
            'SD LDO requires its specified input/output capacitors; verify effective capacitance')
    require(len(data['board']['mounting_holes'])==4,'Four mounting holes required')
    return {'source_checks':'passed','physical_validation':'not performed',
            'routing_status':data['board']['routing_status'],
            'led_current_estimate_mA':{
                'reference_per_led_at_assumed_Vf_2_65V':.65,
                'reference_five_leds_plus_pulldowns':3.415,
                'resistor_only_per_gpio_upper_bound_at_3_3V_1percent':3.3/.99,
                'basis':'Kingbright specifies typical Vf 2.65V at 2mA; using it at another current is a reference calculation, not an operating-point prediction'},
            'release_status':'not-for-manufacture',
            'pending':['INA229 footprint, Kelvin routing and sense-cable mating','LED polarity / brightness',
                       'USB and antenna clearance','3V3 stability during Wi-Fi and all LEDs on',
                       'SPI identification / UART / marker bench tests',
                       'SD regulator transient and thermal behavior; card write/read verification',
                       'SD write stalls / buffer sizing / error handling in future firmware']}


def check_board(data):
    import pcbnew
    board=pcbnew.LoadBoard(str(OUT/'carrier.kicad_pcb'))
    footprints={fp.GetReference():fp for fp in board.GetFootprints()}
    for p in data['parts']:
        require(p['ref'] in footprints,'Missing PCB component '+p['ref'])
        actual={pad.GetNumber():pad.GetNetname() for pad in footprints[p['ref']].Pads() if pad.GetNumber()}
        require(set(actual)==set(p['pins']),'PCB pad numbering differs from circuit '+p['ref'])
        for n,net in p['pins'].items():
            require(actual[n]==('/'+net if net else f'unconnected-({p["ref"]}-NC-Pad{n})'),
                    f'PCB connection differs from circuit: {p["ref"]}.{n}')
    for hole in data['board']['mounting_holes']:
        fp=footprints[hole['ref']];pos=fp.GetPosition()
        require([round(pcbnew.ToMM(pos.x),3),round(pcbnew.ToMM(pos.y),3)]==hole['position_mm'],
                'Mounting hole position differs from drawing')
        require(any(abs(pcbnew.ToMM(pad.GetDrillSize().x)-2.7)<.001 for pad in fp.Pads()),
                'Mounting drill must be 2.7mm')
    zones=list(board.Zones())
    require(any(z.GetIsRuleArea() and z.GetZoneName()=='Pico antenna / no copper or components' for z in zones),
            'Missing antenna rule area')
    require(bool(list(board.GetTracks())),'PCB not routed')


def env():
    result=os.environ.copy()
    for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
        target=ROOT/'.build/kicad'/name;target.mkdir(parents=True,exist_ok=True);result[key]=str(target)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--kicad',choices=['erc','drc']);args=parser.parse_args()
    reports=OUT/'checks';reports.mkdir(exist_ok=True)
    if args.kicad:
        command=['kicad-cli','sch','erc'] if args.kicad=='erc' else ['kicad-cli','pcb','drc','--schematic-parity']
        suffix='sch' if args.kicad=='erc' else 'pcb'
        command+=['--severity-all','--exit-code-violations','-o',str(reports/(args.kicad+'.rpt')),str(OUT/('carrier.kicad_'+suffix))]
        raise SystemExit(subprocess.run(command,env=env(),check=False).returncode)
    data=json.loads((OUT/'circuit.json').read_text());report=check_circuit(data);check_board(data)
    (reports/'source-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Carrier source and PCB mapping checks passed; physical validation pending.')


if __name__=='__main__':main()
