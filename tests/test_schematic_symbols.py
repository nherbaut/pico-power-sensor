"""Schematic symbols must match each part's electrical class, never a generic box."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SchematicSymbolTests(unittest.TestCase):
    def test_symbols_follow_electrical_class(self):
        program = r'''
import importlib.util, json, re
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
spec = importlib.util.spec_from_file_location('generate_interposer', 'scripts/generate-interposer.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)

def expected(ref, kind):
    if kind == 'shunt': return 'shunt'
    for prefix, cls in [('TP', 'testpoint'), ('R', 'resistor'), ('C', 'capacitor'), ('D', 'led'),
                        ('F', 'fuse'), ('Q', 'nmos'), ('U', 'ic'), ('J', 'connector')]:
        if ref.startswith(prefix): return cls
    raise AssertionError(ref)

for board in ('interposer', 'carrier'):
    data = json.loads(Path('hardware/pcb/%s/circuit.json' % board).read_text())
    for part in data['parts']:
        ref = part['ref']
        cls = h.symbol_class(part)
        assert cls == expected(ref, part.get('kind')), (board, ref, cls)
        text = h.symbol_definition(part)
        assert '(property "SymbolClass" "%s"' % cls in text, (board, ref)
        coords, height = h.pin_layout(part)
        generic = '(rectangle (start -7.62 %s) (end 7.62 %s)' % (height, -height)
        assert (generic in text) == (cls in ('ic', 'connector')), (board, ref, cls, 'generic box misuse')
        numbers = {c[0] for c in coords}
        assert numbers == set(part['pins']), (board, ref, 'pin numbers changed')
        if cls == 'led':
            assert '(xy 1.905 1.905) (xy 1.905 -1.905) (xy -1.905 0)' in text, (board, ref, 'LED polarity')
            assert [c for c in coords if c[0] == '1'][0][1] == -12.7, (board, ref, 'cathode side')
            assert h.pin_name(part, '1') == 'K' and h.pin_name(part, '2') == 'A', (board, ref)
        if cls == 'nmos':
            pin = {c[0]: c for c in coords}
            assert pin['4'][1:3] == (-12.7, 0), (board, ref, 'gate left')
            assert pin['5'][2] > 0, (board, ref, 'drain above')
            assert all(pin[n][2] < 0 for n in ('1', '2', '3')), (board, ref, 'sources below')

# Unknown reference families fail closed instead of falling back to a box.
for bad in ('L1', 'X9', 'Y1'):
    try:
        h.symbol_class({'ref': bad, 'kind': 'passive', 'pins': {'1': 'A', '2': 'B'}})
    except ValueError:
        continue
    raise AssertionError('unknown class accepted: ' + bad)
print('ok')
'''
        result = subprocess.run(['/usr/bin/python3', '-c', program], cwd=ROOT,
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('ok', result.stdout)


if __name__ == '__main__':
    unittest.main()
