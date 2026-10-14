"""Regression checks for hazardous connector/supply and indicator changes."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('carrier_checks',ROOT/'scripts/check-carrier.py')
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)


class CarrierBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'hardware/pcb/carrier/circuit.json').read_text())

    def part(self,ref):
        return next(p for p in self.data['parts'] if p['ref']==ref)

    def test_agreed_design_passes(self):
        self.assertEqual(checks.check_circuit(self.data)['source_checks'],'passed')

    def test_swapped_ina229_supply_and_ground_rejected(self):
        pins=self.part('U_PM')['pins'];pins['6'],pins['7']=pins['7'],pins['6']
        with self.assertRaisesRegex(ValueError,'INA229 pin mapping'):checks.check_circuit(self.data)

    def test_swapped_sense_polarity_rejected(self):
        pins=self.part('U_PM')['pins'];pins['9'],pins['10']=pins['10'],pins['9']
        with self.assertRaisesRegex(ValueError,'INA229 pin mapping'):checks.check_circuit(self.data)

    def test_sense_cable_crossover_rejected(self):
        pins=self.part('J_SENSE')['pins'];pins['1'],pins['2']=pins['2'],pins['1']
        with self.assertRaisesRegex(ValueError,'Sense connector'):checks.check_circuit(self.data)

    def test_sense_nets_cannot_reach_other_parts(self):
        self.part('R_CS')['pins']['2']='SENSE_PLUS'
        with self.assertRaisesRegex(ValueError,'measurement boundary'):checks.check_circuit(self.data)

    def test_alert_pullup_required(self):
        self.part('R_ALERT')['pins']['1']='GND'
        with self.assertRaisesRegex(ValueError,'ALERT needs a pull-up'):checks.check_circuit(self.data)

    def test_cable_crossover_rejected(self):
        pins=self.part('J_UART')['pins'];pins['2'],pins['3']=pins['3'],pins['2']
        with self.assertRaisesRegex(ValueError,'without cable crossover'):checks.check_circuit(self.data)

    def test_indicator_supply_cannot_enter_measured_domain(self):
        self.data['parts'].append(dict(ref='C_BAD',pins={'1':'PI_5V','2':'GND'}))
        with self.assertRaisesRegex(ValueError,'measurement boundary'):checks.check_circuit(self.data)

    def test_led_cannot_take_uart_or_spi_pin(self):
        self.data['gpio']['leds'][0]=5
        with self.assertRaisesRegex(ValueError,'GPIO allocation'):checks.check_circuit(self.data)

    def test_reversed_led_rejected(self):
        self.part('D1')['pins']={'1':'LED1_A','2':'GND'}
        with self.assertRaisesRegex(ValueError,'LED polarity'):checks.check_circuit(self.data)

    def test_sd_regulator_cannot_power_sensor_rail(self):
        self.part('U_SD')['pins']['5']='PICO_3V3'
        with self.assertRaisesRegex(ValueError,'SD regulator'):checks.check_circuit(self.data)

    def test_sd_pullups_cannot_use_sensor_supply(self):
        self.part('R_SDP1')['pins']['1']='PICO_3V3'
        with self.assertRaisesRegex(ValueError,'SD CMD'):checks.check_circuit(self.data)

    def test_sd_clock_cannot_take_ina_spi(self):
        self.data['gpio']['sd_sclk']=18
        with self.assertRaisesRegex(ValueError,'dedicated SPI1'):checks.check_circuit(self.data)

    def test_sd_ldo_missing_output_capacitance_rejected(self):
        self.part('C_SDOUT')['value']='100nF'
        with self.assertRaisesRegex(ValueError,'specified input/output capacitors'):checks.check_circuit(self.data)


if __name__=='__main__':unittest.main()
