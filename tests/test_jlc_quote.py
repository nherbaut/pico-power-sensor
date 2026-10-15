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
                    if row['LCSC Part #']:
                        self.assertIn(row['LCSC Part #'], ('C1779', 'C520082', 'C94122', 'C90146', 'C5569446', 'C5912397', 'C269742'), 'only owner-chosen parts may fill the LCSC column')
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

    def test_only_owner_chosen_parts_fill_the_lcsc_column(self):
        with (self.out / 'carrier/carrier-BOM-quote-only.csv').open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        filled = {r['Designator']: r['LCSC Part #'] for r in rows if r['LCSC Part #']}
        self.assertEqual(filled, {'C_SDIN,C_SDOUT': 'C1779', 'C1,C_PM,C_SDSOCKET': 'C520082', 'C2': 'C94122', 'C_SDBULK': 'C90146',
                          'D1,D2,D3,D4,D5': 'C5569446', 'J_SD': 'C5912397',
                          'R_ALERT,R_SDP1,R_SDP2,R_SDP3,R_SDP4,R_SDP5': 'C269742'})
        with (self.out / 'interposer/interposer-BOM-quote-only.csv').open(newline='') as handle:
            filled = {r['Designator']: r['LCSC Part #'] for r in csv.DictReader(handle) if r['LCSC Part #']}
        self.assertEqual(filled, {'C3,C4': 'C520082', 'D1': 'C5569446'})
        with (self.out / 'carrier/carrier-parts-to-map.csv').open(newline='') as handle:
            parts = {r['designators']: r for r in csv.DictReader(handle)}
        chosen = next(r for d, r in parts.items() if 'R_SDP1' in d)
        self.assertEqual(chosen['lcsc_part'], 'C269742')
        self.assertTrue(chosen['selection_status'].startswith('chosen'))

    def test_a_candidate_never_fills_the_bom(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('quote', ROOT / 'scripts/prepare-jlc-quote.py')
        quote = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quote)
        row = dict(lcsc_part='C1', selected_mpn='X', jlcpcb_type='Extended', differences='', open_checks='')
        quote.selections = lambda board: ({}, {'R1': row})
        parts = {'R1': dict(value='10k', footprint='R_0805', mpn='M1')}
        text, _ = quote.jlc_bom('carrier', ['R1'], parts)
        self.assertEqual(text.splitlines()[1], '10k,R1,R_0805,')

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
