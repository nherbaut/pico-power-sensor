import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from design_analysis import threshold_corners, supplemental_analysis


class DesignAnalysisTests(unittest.TestCase):
    def test_zero_error_matches_divider_equations(self):
        c = threshold_corners(tolerance=0, tcr=0, leakage_A=0)
        self.assertAlmostEqual(c['ov_trip'][0], .4925*10.68)
        self.assertAlmostEqual(c['uv_trip'][1], .5075*106800/11500)

    def test_uncertainty_expands_not_shrinks_corners(self):
        nominal = threshold_corners(tolerance=0, tcr=0, leakage_A=0)
        corners = threshold_corners()
        for key in nominal:
            self.assertLess(corners[key][0], nominal[key][0])
            self.assertGreater(corners[key][1], nominal[key][1])

    def test_limits_are_not_silently_approved(self):
        report = supplemental_analysis()
        self.assertFalse(report['inrush']['soa_verified'])
        self.assertFalse(report['sd_ldo']['continuous_500mA_approved'])
        self.assertFalse(report['fault_policy']['hardware_latch'])
        self.assertGreater(report['inrush']['loads'][-1]['charging_current_reference_A'], 5)
