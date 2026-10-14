"""Native metadata, selected lands and physical assembly survive regeneration."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ComponentSelectionTests(unittest.TestCase):
    def test_native_and_scratch_regeneration(self):
        program = r'''
import csv, importlib.util, json, sys, tempfile
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path.cwd()/'scripts'))
from component_selections import selections

def load(name):
    spec = importlib.util.spec_from_file_location(name, Path('scripts')/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify(name, folder):
    data = json.loads((folder/'circuit.json').read_text())
    board = pcbnew.LoadBoard(str(folder/(name+'.kicad_pcb')))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    parts = {p['ref']: p for p in data['parts'] if p.get('on_board', True)}
    assert set(parts) <= set(fps)
    for ref, p in parts.items():
        for key, value in [('MPN', p['mpn']), ('Datasheet', p['documentation_url'])]:
            field = fps[ref].GetFieldByName(key)
            assert field is not None and field.GetText() == value, (name, ref, key)
    bom = {row['reference']: row for row in csv.DictReader((folder/'board-bom.csv').open())}
    for ref, selection in selections(name).items():
        assert parts[ref]['mpn'] == selection['manufacturer_reference']
        assert bom[ref]['manufacturer_reference'] == parts[ref]['mpn']
    assert 'Pico socket strips' not in bom, 'Sockets belong to physical assembly list'
    # KEMET table 3 density B, not the generator's constants as the oracle.
    if name == 'interposer':
        c1 = fps['C1']
        assert c1.GetFPID().GetLibItemName() == 'C_0805_KEMET'
        for pad in c1.Pads():
            assert abs(pcbnew.ToMM(pad.GetSize().x)-1.15) < 1e-6
            assert abs(pcbnew.ToMM(pad.GetSize().y)-1.45) < 1e-6
            assert abs(abs(pcbnew.ToMM(pad.GetFPRelativePosition().x))-.9) < 1e-6
    assembly = load('export-assembly-review').rows_for(name, data, board)
    rows = {r['reference']: r for r in assembly}
    assert all(r['quantity'] == 0 for ref, r in rows.items() if ref.startswith('TP'))
    if name == 'carrier':
        assert rows['J_PICO']['quantity'] == 0
        assert rows['J_PICO socket strips']['quantity'] == 2
        assert rows['J_PICO socket strips']['manufacturer_reference'] == 'SSW-120-01-G-S'
        assert rows['J_SD']['assembly'] == 'factory SMT'
    else:
        assert 'J5' not in rows
        assert rows['F1']['manufacturer_reference'] == '0031.8201'
        assert rows['F1 cartridge']['manufacturer_reference'] == '021706.3MXP'

for name in ('interposer', 'carrier'):
    verify(name, Path('hardware/pcb')/name)
    with tempfile.TemporaryDirectory(prefix='picopower-regeneration-') as scratch:
        folder = Path(scratch)
        generator = load('generate-'+name)
        generator.OUT = folder
        generator.main()
        verify(name, folder)
        if name == 'interposer':
            layout = load('layout-interposer')
            layout.OUT = folder
            layout.main()
            verify(name, folder)
'''
        result = subprocess.run(['/usr/bin/python3', '-c', program], cwd=ROOT,
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
