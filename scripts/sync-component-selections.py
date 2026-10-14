#!/usr/bin/python3
"""Synchronize selected parts and reviewed passive lands without rerouting boards.

Explicit mutation tool. Backs up each project once, updates native metadata and
regenerates schematics from circuit.json; never generates fabrication files.
"""
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import pcbnew
from component_selections import apply_selections, constraints, selections
from footprint_corrections import selected_passive, part_fields

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows, fields=None):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def sync(name):
    folder = ROOT/'hardware/pcb'/name
    backup = ROOT/'.build/pre-component-selection'/name
    if not backup.exists():
        shutil.copytree(folder, backup)
    data = json.loads((folder/'circuit.json').read_text())
    apply_selections(name, data['parts'])
    data['design_constraints'] = constraints()
    prefix = 'PicoPower' if name == 'interposer' else 'Carrier'
    library = folder/(prefix+'.pretty')
    board = pcbnew.LoadBoard(str(folder/(name+'.kicad_pcb')))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for p in data['parts']:
        if not p.get('on_board', True):
            continue
        fp = footprints[p['ref']]
        if str(fp.GetFPID().GetLibItemName()) != p['footprint']:
            base = 'Capacitor_SMD' if p['ref'].startswith('C') else 'Resistor_SMD'
            stock = 'C_0805_2012Metric' if base == 'Capacitor_SMD' else 'R_0805_2012Metric'
            fresh = pcbnew.FootprintLoad('/usr/share/kicad/footprints/'+base+'.pretty', stock)
            selected_passive(fresh, p['footprint'])
            fresh.SetFPID(pcbnew.LIB_ID(prefix, p['footprint']))
            pcbnew.FootprintSave(str(library), fresh)
            fresh.SetReference(p['ref']); fresh.SetPath(fp.GetPath())
            fresh.SetOrientation(fp.GetOrientation()); fresh.SetPosition(fp.GetPosition())
            for pad in fresh.Pads():
                old = next(x for x in fp.Pads() if x.GetNumber() == pad.GetNumber())
                pad.SetNet(old.GetNet())
            fresh.Reference().SetPosition(fp.Reference().GetPosition())
            fresh.Reference().SetTextSize(fp.Reference().GetTextSize())
            fresh.Reference().SetTextThickness(fp.Reference().GetTextThickness())
            fresh.Reference().SetTextAngle(fp.Reference().GetTextAngle())
            fresh.Reference().SetLayer(fp.Reference().GetLayer())
            fresh.Value().SetVisible(False)
            board.Remove(fp); board.Add(fresh); fp = fresh
        fp.SetValue(p['value'])
        part_fields(fp, p)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(folder/(name+'.kicad_pcb')), board)
    (folder/'circuit.json').write_text(json.dumps(data, indent=2)+'\n')
    spec = importlib.util.spec_from_file_location('generator_'+name, ROOT/'scripts'/('generate-'+name+'.py'))
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    if name == 'interposer':
        (folder/'interposer.kicad_sch').write_text(generator.schematic(data))
        (folder/'PicoPower.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+
            '\n'.join(generator.symbol_definition(p, True) for p in data['parts'])+'''
    (symbol "SupplyFlag" (pin_names (offset 0)) (in_bom no) (on_board no)
      (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)) hide))
      (property "Value" "PWR_FLAG" (at 0 2.54 0) (effects (font (size 1 1))))
      (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0)
        (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1))))))
    )
)
''')
    else:
        generator.schematic(data)
    write_csv(folder/'board-bom.csv', [dict(reference=p['ref'], value=p['value'],
        manufacturer_reference=p['mpn'], footprint=prefix+':'+p['footprint'],
        documentation_url=p['documentation_url'], status='prototype selection; release reviews pending')
        for p in data['parts'] if p.get('in_bom', True)])
    return data


def main():
    designs = {name: sync(name) for name in ('interposer', 'carrier')}
    path = ROOT/'hardware/bom.csv'
    rows = list(csv.DictReader(path.open()))
    by_id = {r['component_id']: r for r in rows}
    for name, data in designs.items():
        parts = {p['ref']: p for p in data['parts']}
        for ref, proposal in selections(name).items():
            row = by_id[proposal['bom_component_id']]
            row.update(manufacturer=proposal['manufacturer'],
                       manufacturer_reference=proposal['manufacturer_reference'],
                       documentation_url=proposal['documentation_url'], model=parts[ref]['value'],
                       validation_status='selected for prototype; release reviews pending')
            row['notes']=proposal['remaining']+'; see docs/design-review.md'
    by_id['HW-042'].update(manufacturer='Samtec', manufacturer_reference='SSW-120-01-G-S',
        documentation_url='https://www.samtec.com/products/ssw-120-01-g-s',
        validation_status='selected for mechanical review; not released',
        notes='Two manually fitted 1x20 strips; combined J_PICO footprint represents owned module; verify drill, seating and Pico male-header engagement before purchase')
    write_csv(path, rows)
    print('Updated prototype selections, native schematics/PCBs and BOMs; no release granted.')


if __name__ == '__main__':
    main()
