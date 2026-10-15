"""The quote package must place exactly the factory-SMT parts and never claim to be a release."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class JlcQuotePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='picopower-jlc-')
        cls.out = Path(cls.tmp.name)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/prepare-jlc-quote.py'), '--output', str(cls.out)],
                                cwd=ROOT, capture_output=True, text=True, timeout=240)
        assert result.returncode == 0, result.stdout + result.stderr

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def smt_refs(self, board):
        with (ROOT / 'hardware/assembly-review.csv').open(newline='') as handle:
            return {r['reference'] for r in csv.DictReader(handle)
                    if r['board'] == board and r['assembly'] == 'factory SMT'}

    def test_bom_and_cpl_cover_exactly_the_factory_smt_parts(self):
        for board in ('interposer', 'carrier'):
            folder = self.out / board
            bom_refs = set()
            with (folder / f'{board}-BOM-quote-only.csv').open(newline='') as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, ['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
                for row in reader:
                    self.assertEqual(row['LCSC Part #'], '', 'LCSC numbers must be left for the owner')
                    bom_refs |= set(row['Designator'].split(','))
            with (folder / f'{board}-CPL-quote-only.csv').open(newline='') as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
                cpl_refs = {row['Designator'] for row in reader}
            self.assertEqual(bom_refs, self.smt_refs(board))
            self.assertEqual(cpl_refs, self.smt_refs(board))

    def test_through_hole_and_owned_parts_are_excluded(self):
        for board, excluded in (('interposer', {'J1', 'J2', 'J3', 'J4', 'F1', 'TP1'}),
                                ('carrier', {'J_PICO', 'J_UART', 'J_SENSE', 'TP1'})):
            text = (self.out / board / f'{board}-CPL-quote-only.csv').read_text()
            for ref in excluded:
                self.assertNotIn(f'\n{ref},', '\n' + text, (board, ref))

    def test_package_is_labelled_quote_only(self):
        for board in ('interposer', 'carrier'):
            self.assertIn('NOT FOR FABRICATION', (self.out / board / 'QUOTE-ONLY.txt').read_text())
            with zipfile.ZipFile(self.out / board / f'{board}-gerbers-QUOTE-ONLY.zip') as z:
                names = z.namelist()
                self.assertIn('QUOTE-ONLY.txt', names)
                self.assertTrue(any(n.endswith('.gtl') for n in names) and any(n.endswith('.gbl') for n in names))
                self.assertTrue(any(n.endswith('PTH.drl') for n in names))
                self.assertTrue(any(n.endswith('.gm1') for n in names), 'board outline missing')

    def test_specialised_parts_are_flagged_for_checking(self):
        with (self.out / 'carrier/carrier-parts-to-map.csv').open(newline='') as handle:
            rows = {r['manufacturer_reference']: r for r in csv.DictReader(handle)}
        self.assertEqual(rows['INA229AIDGSR']['check_first'], 'yes')
        with (self.out / 'interposer/interposer-parts-to-map.csv').open(newline='') as handle:
            rows = {r['manufacturer_reference']: r for r in csv.DictReader(handle)}
        self.assertEqual(rows['LTC4367IMS8#PBF']['check_first'], 'yes')
        self.assertIn('precision', rows['TNPW080595K3BEEA']['note'])


if __name__ == '__main__':
    unittest.main()
