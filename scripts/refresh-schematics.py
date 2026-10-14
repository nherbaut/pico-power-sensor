#!/usr/bin/python3
"""Regenerate both boards' schematics and symbol libraries from circuit.json.

Schematic and symbol files only: PCBs, routing, BOMs and reports are not touched, so
this is safe on a routed design. Run native ERC and DRC (parity) afterwards.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    interposer = load('generate-interposer')
    folder = ROOT / 'hardware/pcb/interposer'
    data = json.loads((folder / 'circuit.json').read_text())
    (folder / 'interposer.kicad_sch').write_text(interposer.schematic(data))
    (folder / 'PicoPower.kicad_sym').write_text(
        '(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n' +
        '\n'.join(interposer.symbol_definition(p, True) for p in data['parts']) + '''
    (symbol "SupplyFlag" (pin_names (offset 0)) (in_bom no) (on_board no)
      (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)) hide))
      (property "Value" "PWR_FLAG" (at 0 2.54 0) (effects (font (size 1 1))))
      (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0)
        (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1))))))
    )
)
''')
    carrier = load('generate-carrier')
    data = json.loads((ROOT / 'hardware/pcb/carrier/circuit.json').read_text())
    carrier.schematic(data)
    print('Refreshed interposer and carrier schematics and symbol libraries; PCBs untouched.')


if __name__ == '__main__':
    main()
