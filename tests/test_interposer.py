"""Regression checks for wiring mistakes that could damage hardware or bias energy."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('check_interposer',ROOT/'scripts/check-interposer.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


class InterposerSafetyInvariants(unittest.TestCase):
    def setUp(self):
        self.design=json.loads((ROOT/'hardware/pcb/interposer/circuit.json').read_text())

    def part(self,ref):
        return next(p for p in self.design['parts'] if p['ref']==ref)

    def test_nominal_design_and_energy_loss_arithmetic(self):
        report=checker.check_circuit(self.design)
        self.assertAlmostEqual(report['shunt_at_max_current']['power_W'],.125)
        self.assertAlmostEqual(report['shunt_at_max_current']['voltage_drop_V'],.025)

    def test_normal_input_window_does_not_imply_ov_recovery(self):
        report=checker.check_circuit(self.design)
        protection=report['protection_input_thresholds_V']
        self.assertLess(self.design['load']['nominal_volts'], protection['ov_trip_resistor_comparator_range'][0])
        self.assertFalse(protection['ov_recovery_at_nominal_guaranteed'])
        self.assertLess(protection['ov_restart_range'][0], self.design['load']['nominal_volts'])

    def test_controller_cannot_draw_measured_load_current(self):
        self.part('U1')['pins']['7']='PI_5V'
        with self.assertRaisesRegex(ValueError,'upstream'):checker.check_circuit(self.design)

    def test_reversed_input_is_detected(self):
        self.part('J1')['pins']={'1':'GND','2':'VIN_RAW'}
        with self.assertRaisesRegex(ValueError,'polarity'):checker.check_circuit(self.design)

    def test_missing_header_ground_is_detected(self):
        self.part('J2')['pins']['39']='GPIO21'
        with self.assertRaisesRegex(ValueError,'ground'):checker.check_circuit(self.design)

    def test_added_downstream_capacitor_is_rejected(self):
        self.design['parts'].append(dict(ref='C99',pins={'1':'PI_5V','2':'GND'},position_mm=[10,10],body_mm=[2,2],kind='passive'))
        with self.assertRaisesRegex(ValueError,'downstream'):checker.check_circuit(self.design)

    def test_power_indicator_cannot_be_counted_as_dut_load(self):
        self.part('R9')['pins']['1']='PI_5V'
        with self.assertRaisesRegex(ValueError,'downstream'):checker.check_circuit(self.design)

    def test_direct_uart_connector_bypass_is_rejected(self):
        self.part('J4')['pins']['2']='GPIO14'
        with self.assertRaisesRegex(ValueError,'buffered'):checker.check_circuit(self.design)

    def test_joined_buffer_supply_rails_are_rejected(self):
        self.design['parts'].append(dict(ref='R99',pins={'1':'PI_3V3','2':'PICO_3V3'},
                                        position_mm=[10,10],body_mm=[2,2],kind='passive'))
        with self.assertRaisesRegex(ValueError,'supplies'):checker.check_circuit(self.design)

    def test_wrong_direction_is_rejected(self):
        self.part('U2')['pins']['2']='PICO_3V3'
        with self.assertRaisesRegex(ValueError,'direction'):checker.check_circuit(self.design)

    def test_crossed_marker_and_uart_channels_are_rejected(self):
        self.part('U2')['pins']['4']='PICO_MARK'
        with self.assertRaisesRegex(ValueError,'channel'):checker.check_circuit(self.design)

    def test_bias_to_foreign_supply_is_rejected(self):
        self.part('R11')['pins']['1']='PICO_3V3'
        with self.assertRaisesRegex(ValueError,'power domain'):checker.check_circuit(self.design)

    def test_signal_bridge_around_buffer_is_rejected(self):
        self.design['parts'].append(dict(ref='R99',pins={'1':'GPIO15','2':'PICO_TX'},
                                        position_mm=[10,10],body_mm=[2,2],kind='passive'))
        with self.assertRaisesRegex(ValueError,'signal bypass'):checker.check_circuit(self.design)

    def test_bad_threshold_cannot_accept_wrong_supply(self):
        self.design['protection']['top_ohms']=20000
        with self.assertRaisesRegex(ValueError,'operating window'):checker.check_circuit(self.design)


if __name__=='__main__':unittest.main()
