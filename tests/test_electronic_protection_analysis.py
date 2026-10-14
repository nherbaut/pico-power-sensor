"""The study must not claim a qualified design from reference arithmetic."""
import sys
import copy
import importlib
import json
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from electronic_protection_analysis import analyze
validate_copper = importlib.import_module('export-electronic-protection-study').validate_copper


class ElectronicProtectionAnalysisTests(unittest.TestCase):
    def test_stale_copper_evidence_is_rejected(self):
        copper = json.loads((Path(__file__).resolve().parents[1]/'hardware/review/copper-screen.json').read_text())
        validate_copper(copper, copper['source_board_sha256'])
        with self.assertRaisesRegex(ValueError, 'stale'):
            validate_copper(copper, '0' * 64)

    def test_inconsistent_copper_branch_budget_is_rejected(self):
        copper = json.loads((Path(__file__).resolve().parents[1]/'hardware/review/copper-screen.json').read_text())
        mutated = copy.deepcopy(copper)
        mutated['branches'][0]['copper_resistance_mohm'] += 1
        with self.assertRaisesRegex(ValueError, 'branch sum'):
            validate_copper(mutated, copper['source_board_sha256'])

    def test_reference_drops_keep_missing_contributions_open(self):
        r=analyze(7.231500919843118)
        self.assertAlmostEqual(r['accounting_comparison']['cartridge_reference_mV'],132.7825045992156)
        self.assertAlmostEqual(r['accounting_comparison']['shared_shunt_comparator_reference_mV'],85.2825045992156)
        self.assertFalse(r['release']['complete_loss_bound'])
        self.assertFalse(r['release']['design_selected'])

    def test_threshold_screen_is_not_qualification(self):
        r=analyze(7.2)
        self.assertGreater(r['comparator']['screening_trip_A'][0],5)
        self.assertLess(r['comparator']['screening_trip_A'][1],6.3)
        self.assertFalse(r['comparator']['qualified_trip_interval'])
        changed=analyze(7.2,limit_ohm=1000)
        self.assertLess(changed['comparator']['screening_trip_A'][0],5)

    def test_zero_logic_margin_is_not_accepted_and_power_states_remain_open(self):
        r=analyze(7.2)
        self.assertEqual(r['logic']['direct_alert_to_shdn_margin_V'],0)
        self.assertFalse(r['logic']['direct_connection_qualified'])
        self.assertTrue(r['logic']['brownout_interlock_required'])
        self.assertTrue(r['release']['korad_current_limit_remains_primary'])
