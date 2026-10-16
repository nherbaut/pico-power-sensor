# Carrier schematic, revision 1

Date: 2026-10-16. Status: **captured, ERC clean, technical review by Claude only** (AGENTS.md step 7). The owner asked to continue without a technical sign-off of his own (see the review record in [interposer schematic](interposer-schematic.md)). Not a layout, footprint review or release.

## Files

| File | Role |
|---|---|
| `hardware/kicad/gen_carrier_sch.py` | Source of truth; regenerate with `python3 -I hardware/kicad/gen_carrier_sch.py` |
| `hardware/kicad/carrier/carrier.kicad_sch`, `carrier.pdf`, `carrier.net`, `carrier.pinmap.tsv`, `erc.rpt` | Generated schematic, render, netlist, intended pin map, ERC report |

## Reference designators

| Ref | Role (BOM) | Part | Function |
|---|---|---|---|
| J1, J2 | J_PICO_LEFT, J_PICO_RIGHT | Harwin M20-7822042 | Pico 2 WH socket; J1 pin k = Pico pin k, J2 pin k = Pico pin 20+k |
| J3, J4 | J_PM_LEFT, J_PM_RIGHT | Harwin M20-7820842 | MIKROE-4810 socket; J3 = mikroBUS 1–8, J4 pin k = mikroBUS 8+k |
| J5 | J_SD | Harwin M20-7820942 | Adafruit 4682 socket, pins 1–9 |
| J6 | J_PM_ANALOG (**new, no part**) | Three plated wire pads | Short wires to the MikroE IN1+, IN1− and IN2 VBUS screw terminals |
| C1 | C_SENSE_DIFF | KEMET C315C104K5R5TA | 100 nF across the Kelvin pair, near J6 |
| J7 | J_SENSE | JST B4B-XH-A | 1 SHUNT_KELVIN_PLUS, 2 SHUNT_KELVIN_MINUS, 3 DUT_VBUS_SENSE, 4 INSTR_GND |
| U1 | U_UART (socket X_UART) | TI SN74LV125AN in TE 1-2199298-3 | Units A–C used, D parked, E power |
| C2 | C_UART | KEMET C315C104K5R5TA | U1 bypass |
| R1 | R_PICO_TX | 470 Ω | U1 3Y → PI_RX_CABLE |
| R2, R3 | R_PI_TX_PD, R_PI_MARK_PD | 100 kΩ | Pull-downs on the Pi-driven cable inputs |
| R4, R5 | R_UART_OE_PU, R_PICO_TX_PU | 10 kΩ | Buffer disabled by default; Pico TX idles high |
| J8 | J_UART | JST B5B-XH-A | 1 INSTR_GND, 2 PI_TX_CABLE, 3 PI_RX_CABLE, 4 PI_MARK_CABLE, 5 empty |
| R6–R10, D1–D5 | R_LED1–5, LED1–5 | 1.8 kΩ, TLLR4401 | GP7–GP11 → resistor → LED → ground |

U1 uses the stock `74xx:74LS125` symbol: its pin numbering (1OE 1, 1A 2, 1Y 3 … VCC 14, GND 7) matches the SN74LV125A N-package table recorded in `hardware/review/uart-buffer-pin-contract.csv`. Only the graphic is borrowed; the value and BOM part are SN74LV125AN.

## Cable mapping between the boards

| Cable pin | Interposer net | Carrier net |
|---|---|---|
| Sense 1–3 | SHUNT_KELVIN_PLUS, SHUNT_KELVIN_MINUS, DUT_VBUS_SENSE | same names |
| Sense 4 | MEAS_GND_REF | INSTR_GND |
| UART 1 | SIGNAL_GND | INSTR_GND |
| UART 2 | PI_TX_TO_PICO | PI_TX_CABLE |
| UART 3 | PI_GPIO15_RXD | PI_RX_CABLE |
| UART 4 | PI_TASK_MARKER | PI_MARK_CABLE |
| UART 5 | empty | empty |

## Deviations from the earlier contracts, decided at capture

- **Carrier ground is one net, INSTR_GND.** The buffer contract named U1 pins 7/12 and the UART ground `SIGNAL_GND`; the connector contract says the carrier side is "common instrument ground". On the carrier both cable grounds land on INSTR_GND; the single-point separation is done on the interposer (NT1/NT2).
- **J6 wire pads added.** The monitor's analog inputs are screw terminals on the module, not mikroBUS pins, so the carrier needs a place to start three short wires. No part is bought; it is three pads.
- **MikroE IN2 GND terminal left unwired.** The module ground already reaches INSTR_GND through mikroBUS pins 8/9; a fourth wire would form a parallel ground loop next to the module.

## Verification performed

| Check | Result | Scope |
|---|---|---|
| ERC, kicad-cli 9.0.9, `--severity-all --exit-code-violations` | 0 violations | Default severities (no `.kicad_pro` yet); PWR_FLAGs on INSTR_3V3/INSTR_GND mark the Pico as the source |
| Netlist vs intended pin map | 26 components, 60 nets, all 125 board pins match | The map was transcribed from the Pico, module and buffer contracts listed above |
| Render review | Visually inspected by Claude (vision check passed this session) | One A3 page |
| Footprints, DRC, parity | Not performed | Step 8–9 |

## Open items

- Pico 2 WH factory header, MIKROE-4810 headers and Adafruit header mating (see [socket options](carrier-socket-options.md)).
- Physical order of the MikroE IN1/IN2 screw terminals must be read off the delivered module before wiring J6.
- 3.3 V budget with the actual card; INA228 I2C address check at bring-up (0x4A expected).
- All earlier qualification gaps remain.
