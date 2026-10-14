"""The enable rules must hold for every ordering of supply, fault and reset events."""
import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from protection_logic import INA300_VS_MIN_V, ProtectionLogic


def powered_up(**kw):
    p = ProtectionLogic(**kw)
    p.set_pico(3.3)
    p.tick(p.release_delay_ms)
    return p


class ProtectionLogicTests(unittest.TestCase):
    def test_supervisor_below_detector_minimum_is_rejected(self):
        with self.assertRaises(ValueError):
            ProtectionLogic(supervisor_fall_v=INA300_VS_MIN_V)

    def test_off_until_arming_delay_has_elapsed(self):
        p = ProtectionLogic()
        p.set_pico(3.3)
        p.tick(p.release_delay_ms - 1)
        self.assertFalse(p.enabled)
        p.tick(1)
        self.assertTrue(p.enabled)

    def test_pico_collapse_disables_before_detector_loses_supply(self):
        p = powered_up()
        for v in (3.0, 2.95, 2.85):
            p.set_pico(v)
            if p.pico_v < p.supervisor_fall_v:
                self.assertFalse(p.enabled)
        self.assertFalse(p.enabled)

    def test_brief_dip_restarts_the_arming_delay(self):
        p = powered_up()
        p.set_pico(2.0)
        p.set_pico(3.3)
        self.assertFalse(p.enabled)

    def test_fault_latches_until_deliberate_reset(self):
        p = powered_up()
        p.set_overcurrent(True)
        self.assertFalse(p.enabled)
        p.set_overcurrent(False)
        self.assertFalse(p.enabled)
        p.press_reset()
        self.assertTrue(p.enabled)

    def test_reset_while_overcurrent_persists_does_not_reenable(self):
        p = powered_up()
        p.set_overcurrent(True)
        p.press_reset()
        self.assertFalse(p.enabled)

    def test_power_cycle_of_the_pico_alone_does_not_hide_a_pending_condition(self):
        p = powered_up()
        p.set_overcurrent(True)
        p.set_pico(0.0)
        p.set_pico(3.3)
        p.tick(p.release_delay_ms)
        self.assertFalse(p.enabled)

    def test_random_event_orders_never_enable_unsafely(self):
        rng = random.Random(4367)
        for _ in range(300):
            p = ProtectionLogic()
            was_latched_pending = False
            for _ in range(200):
                event = rng.choice(('v', 'tick', 'oc', 'reset'))
                if event == 'v':
                    p.set_pico(rng.choice((0.0, 0.8, 1.5, 2.5, 2.8, 3.0, 3.3)))
                elif event == 'tick':
                    p.tick(rng.choice((1, 10, 60, 150)))
                elif event == 'oc':
                    p.set_overcurrent(rng.random() < .4)
                else:
                    p.press_reset()
                if p.enabled:
                    self.assertGreaterEqual(p.pico_v, p.supervisor_fall_v)
                    self.assertGreaterEqual(p.pico_v, INA300_VS_MIN_V)
                    self.assertTrue(p.supervisor_released)
                    self.assertFalse(p.latched)
                    self.assertFalse(p.overcurrent)


if __name__ == '__main__':
    unittest.main()
