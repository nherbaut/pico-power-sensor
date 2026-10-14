# Electronic protection: control design

Status: **design proposal, not integrated.** No schematic, PCB, BOM or release-checklist row changes. This follows the [electronic-protection study](electronic-protection.md) and covers its first open requirement: arming, reset and the brownout interlock. It is a control-logic definition, not a qualified circuit.

## In plain words

Today the Pi switch (LTC4367 and two MOSFETs) turns on by itself whenever the Korad voltage is acceptable. The proposal adds a second guard, a small current detector that watches the same shunt as the measurement chip. Three rules follow:

1. **Too much current: the switch turns off and stays off** until someone presses a reset button. It must not restart by itself, because a restart would hide the fault from the run.
2. **No healthy instrument, no Pi power.** If the Pico supply is missing, dropping or still starting, the switch stays off. The guard cannot work without its own supply, so the Pi must not be powered without it.
3. **Wait before trusting it.** After the Pico supply becomes good, the switch waits about 100 ms (a supervisor chip provides this) before it may turn on.

## Block structure

| Block | Role | Supply |
|---|---|---|
| INA300 (U3) | Compares shunt voltage with a limit; open-drain ALERT, active low; latch mode | PICO_3V3 |
| Supervisor (U4, to select) | Holds its open-drain output low while PICO_3V3 is below a threshold and for a delay after it recovers | PICO_3V3 |
| SN74AUP1G17 buffer (U5) | Turns the combined ALERT/supervisor line into a clean level for SHDN | PICO_3V3 |
| Reset button (SW1) | Pulls INA300 LATCH low for at least 20 µs | none |
| Fault LED | Shows the latched state | PICO_3V3, outside DUT |
| LTC4367 SHDN pin | Existing switch controller; low turns the switch off | its own upstream supply |

ALERT and the supervisor output are wired together (open-drain, so either one pulling low wins) with one pull-up to PICO_3V3. That line drives the buffer, the buffer drives SHDN, and a pull-down on SHDN keeps the switch off whenever PICO_3V3 is absent. This **replaces the present R5 pull-up that enables the switch with no Pico connected**.

All of U3, U4, U5, the LED and the pull-ups are on PICO_3V3, outside the DUT measurement. The only added measured-side current is the INA300 IN- input bias, tracked in the study.

## Intended states

| Situation | Pico 3V3 | Supervisor | Latch | Switch |
|---|---|---|---|---|
| Pico absent or unplugged | 0 V | not valid | n/a | **off** |
| Pico starting | below threshold | holding low | cleared | **off** |
| Pico good for 100 ms | good | released | cleared | on |
| Overcurrent | good | released | set | **off** |
| Current gone, no reset | good | released | set | **off** |
| Reset pressed, current gone | good | released | cleared | on |
| Reset pressed, overcurrent still present | good | released | stays set | **off** |
| Pico supply collapses | falling | low before 2.7 V | n/a | **off** |

`scripts/protection_logic.py` models these rules and `tests/test_protection_logic.py` runs them against random orderings of supply, fault and reset events. It also fails if the supervisor threshold is not above the INA300 minimum supply. It checks the intended rules only. It says nothing about real timing, thresholds or part behavior.

## Facts taken from the INA300 datasheet (SBOS613C)

- ALERT is open-drain and active low, with VOL up to 400 mV at 3 mA.
- Latch mode is selected with LATCH high. The latch clears when LATCH is held low for at least 20 µs, and only if the input is below the limit.
- Supply is 2.7 V to 5.5 V. Common-mode input range is 0 V to 36 V.

## Risks and open items

1. **Back-powering through the sense inputs (highest risk).** With PICO_3V3 off and about 5 V on IN+/IN-, the INA300's input structure could feed current into its own supply, partly powering the Pico-side rail from the DUT supply. The datasheet reviewed does not say. This needs a bench test before any layout, and it could rule the part out.
2. **The Pi cannot run without the instrument.** That is intended, but the bench tests in the electrical acceptance plan then need a 3.3 V source on J4 pin 5 as a stand-in. A shared bypass jumper is not proposed.
3. **Supervisor not selected.** Required: open-drain output, falling threshold above 2.7 V and below the lowest Pico 3V3, a delay of roughly 100 ms or more, and a very low leakage when unpowered. Candidates must be checked against their datasheets; none is verified here.
4. **LTC4367 SHDN thresholds not re-verified.** The datasheet download timed out. The existing study cites the SHDN falling threshold and the slow gate-discharge path. Check logic levels and the restart delay before accepting the buffer interface.
5. **Fault visibility.** The Pico cannot see a latched fault because J4 has no free pin. The first prototype can rely on the LED and the operator. A sixth wire needs a carrier change.
6. **DELAY setting.** 10 µs responds fastest but may trip on Pi or HAT current spikes. Choose after measuring real peaks.
7. **Limits unchanged.** With the Korad limited to 5 A, a 5.6 A trip never sees a short held at 5 A. The Korad limit stays primary. Voltage faults (UV/OV) are not latched by this circuit.
8. **Existing OV recovery conflict** (see [footprint corrections](../hardware/review/footprint-corrections.md)) is separate and still open.

## Next steps

1. Bench-test INA300 back-powering with the sense inputs at 5 V and the supply at 0 V, using a current-limited source.
2. Select the supervisor from datasheets and re-read the LTC4367 SHDN section.
3. Capture a conventional-symbol schematic and independently check its netlist.
4. Only then change `circuit.json`, the generators, the BOM and the routing, and recompute the drop budget.
