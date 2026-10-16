# Sense-cable protection and filtering

Date: 2026-10-16. Status: **owner-approved prototype choice; qualification partial**. The owner accepted this option with "ok" on 2026-10-16. The three Vishay PR01000108209JR500 resistors and one KEMET C315C104K5R5TA capacitor are now in the provisional BOM. This continues parts selection for the MikroE MIKROE-4810 qualification; it does not select the monitor finally or authorize schematic capture.

## Selected prototype circuit

Use **three 82 Ω, 5%, 1 W axial resistors**, one on each positive observation lead at its interposer source, before the exposed cable. Use **one 100 nF radial ceramic capacitor across the Kelvin pair on the carrier**, close to the monitor's input terminals. All four parts are through-hole.

```text
Interposer                               Carrier / MikroE module
Separate shunt + pickup -- 82 Ω -- cable --+-- IN+ (IN1 top)
                                          |
                                        100 nF
                                          |
Separate shunt - pickup -- 82 Ω -- cable --+-- IN- (IN1 bottom)
DUT 5 V header pickup ---- 82 Ω -- cable ----- VBUS (IN2 top)
Measurement reference ----------- cable ----- GND  (IN2 bottom)
```

These resistors carry observation currents, not the Pi's main supply current. Preserve separate Kelvin pickups at the shunt pads. Keep both sense wires coupled and their carrier connections short. Put neither resistor in a shared high-current pad-to-shunt segment. Do not add capacitors from either Kelvin input to ground in this proposal. No VBUS capacitor is proposed.

The retained [MikroE v100 schematic](../hardware/evidence/power-monitor/mikroe-power-monitor-v100.pdf) was visually traced: its analog terminals connect directly to INA228 IN+, IN− and VBUS. Its existing 100 nF capacitor bypasses VCC; it is not a differential input filter. The added parts can therefore sit on our two boards without modifying fine-pitch parts on the module. Physical module revision and terminal orientation still need checking.

## Value comparison and fault calculation

TI requires each input filter resistor to stay at or below 100 Ω; larger values degrade gain and linearity. Its application circuit places a ceramic capacitor across the inputs. Our source-side resistors protect the exposed run, while the capacitor remains near the monitor; the intervening cable makes this a topology to qualify, not a reproduced reference layout. [INA228 datasheet, sections 8.1.4–8.2](https://www.ti.com/lit/ds/symlink/ina228.pdf).

| Resistance option | Ground-short current at 5.1 V | Resistor dissipation at 5.1 V | Initial maximum resistance | Assessment |
|---|---:|---:|---:|---|
| 10 Ω, 1% | 515 mA | 2.627 W | 10.1 Ω | Poor continuous cable-short limiting with a small resistor |
| **82 Ω, 5%, 1 W** | **65.5 mA** | **0.334 W** | **86.1 Ω** | Owner-selected prototype value |
| 91 Ω, 5%, 1 W | 59.0 mA | 0.301 W | 95.55 Ω | Less allowance for temperature, ageing and connection resistance |
| 100 Ω, 1% | 51.5 mA | 0.263 W | 101 Ω | Exceeds TI's limit at initial positive tolerance |
| 1 kΩ, 1% | 5.15 mA | 0.0263 W | 1010 Ω | Incompatible with the shunt-input recommendation |

Calculated using minimum initial resistance and an ideal 5.1 V source, one observation lead shorted to the intended reference. These are not maximum-credible-fault bounds: the supply's actual voltage envelope is unknown. With **6 V as an illustrative scenario only**, the 82 Ω candidate dissipates 0.462 W and limits current to 77.0 mA. A preliminary half-rated-power screen at 6 V gives a nominal interval of 75.79–95.24 Ω, combining 0.5 W dissipation and the 100 Ω ceiling with ±5% initial tolerance. It excludes drift and temperature; it is an engineering screen, not a new requirement or adopted 6 V supply limit.

The recommended Vishay PR01 is rated 1 W at 70 °C, with ±250 ppm/K TCR. Its derating plot falls to zero at 200 °C; its PR01 hot-spot limit is 205 °C. The drawing gives 6.5 mm maximum body length, 8 mm coated length, 2.5 mm diameter and 0.58 ±0.05 mm leads. Soldering and endurance can change resistance. The 82 Ω choice leaves 13.9 Ω initial headroom for these effects and connection resistance; full environmental/lifetime qualification remains open. Do not use its flameproof coating or fusing characteristics as a substitute for the cartridge fuse. [Vishay PR01 family datasheet](https://www.vishay.com/docs/28729/pr010203.pdf).

## Measurement consequences

INA228 specifies **92 kΩ typical differential input impedance** in active mode below 164 mV differential. Therefore two nominal 82 Ω resistors produce a calculated **0.178% current-reading attenuation** in a simple resistive model. At 5 A this corresponds to about 8.90 mA. The 2.5 nA input-bias specification is at zero differential under the table's conditions; it cannot replace the finite-impedance calculation at a loaded shunt. The 92 kΩ figure has no stated min/max here: neither this attenuation nor its stability is guaranteed. Use installed-channel calibration over current and temperature, not a fixed correction derived solely from a typical impedance.

The nominal 100 nF differential filter has an approximately **9.72 kHz pole** and **113 µs settling to 0.1%** in the lumped linear model, including 92 kΩ loading. These are calculations, not achieved acquisition bandwidth or ADC settling validation. Capacitor tolerance, temperature, ageing, cable coupling, ADC behavior and conversion timing remain to be included.

For VBUS, 86.1 Ω in series with the datasheet's 0.8 MΩ minimum active input impedance gives about **0.0108% attenuation**, or 0.549 mV at 5.1 V, under the table's conditions. Nominal input draw is about 6.37 µA in that model. It is measurement loading to include in the boundary/error budget. No auxiliary instrument power is drawn through the cable and no new measurement-boundary exception is proposed. The separate current, voltage, shunt, calibration and timing errors still need a combined energy-error budget.

## Parts and assembly screen

| Quantity and role | Selected prototype code | Status |
|---|---|---|
| 3 interposer observation resistors | Vishay **PR01000108209JR500** | Axial Cu-lead PR01, 82 Ω, 5%, 1 W; selected, qualification partial |
| 1 carrier differential capacitor | KEMET **C315C104K5R5TA** | Radial 100 nF, 10%, 50 V X7R; same candidate code as UART decoupling, separate quantity |

The [candidate CSV](../hardware/sense-interface-candidates.csv) records quantities and sources. The exact resistor code is listed by [DigiKey UK](https://www.digikey.co.uk/en/products/detail/vishay-beyschlag-draloric-bc-components/PR01000108209JR500/596096): observed £0.20 each excluding VAT at quantity one, before delivery, on 2026-10-16. This is a sourcing indication, not a French delivered quote. Manufacturer exact-code lifecycle declarations for these candidates remain open; distributor “Active” is not equivalent evidence.

Propose resistor 15.24 mm mounting pitch, body at least 1 mm above the board, 0.9 mm nominal finished holes with an assumed ±0.05 mm tolerance, and pads at least 1.8 mm. The minimum hole leaves 0.22 mm diametral clearance against the resistor's maximum lead. The capacitor's retained exact drawing gives 2.54 ±0.78 mm lead pitch and 0.61 mm maximum lead diameter: the same hole proposal leaves 0.24 mm clearance. Lead forming, actual footprint, solder-tip access, thermal spacing, HAT clearance and fabricator tolerance remain to be reviewed. No footprint or mechanical baseline has changed.

## Unclosed cases and next action

The [fault and power-state review](../hardware/review/sense-interface-qualification.csv) explicitly leaves grounding, reverse wiring, transients, connector sequencing and powered-off loading open. In particular, resistor-limited external short current is **not** an allowable INA228 pin-injection current. A short between sense wires, or an open sense wire, also makes measurements invalid even if nothing is damaged. Software must flag implausible/absent readings; some wiring faults can give plausible values and need continuity checks before use.

The reference conductor and UART ground can form parallel return paths. This proposal does not make either safe as a replacement for the Pi's main ground. The module's USB-independent analog input capability alone does not qualify the complete unpowered module or a lost-ground fault. No clamp or arbitrary resistor in the reference conductor is selected here.

The owner approved this three-resistor / one-capacitor prototype option with "ok". Continue qualification and the remaining carrier-part review. The [ground-reference review](ground-reference-review.md) now records the owner-confirmed separate USB charger, Wi-Fi-only Pi and optional AI HAT configuration; the existing shared-ground architecture is retained. Source hashes and calculation expressions are retained in the [review receipt](../hardware/review/sense-interface-review-inputs.json). No schematic, ERC, DRC, parity, physical measurement or release pass is claimed.
