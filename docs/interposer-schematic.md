# Interposer schematic, revision 1 (draft for owner review)

Date: 2026-10-16. Status: **captured, ERC clean, awaiting owner review** (AGENTS.md step 6). Not a layout, footprint review or release.

## Files

| File | Role |
|---|---|
| `hardware/kicad/gen_interposer_sch.py` | Source of truth. Regenerate with `python3 -I hardware/kicad/gen_interposer_sch.py`; do not edit the schematic in the GUI |
| `hardware/kicad/interposer/interposer.kicad_sch` | Generated KiCad 9 schematic |
| `hardware/kicad/interposer/interposer.pdf` | Rendered schematic |
| `hardware/kicad/interposer/interposer.net` | Exported netlist (KiCad s-expression) |
| `hardware/kicad/interposer/interposer.pinmap.tsv` | Intended pin-to-net map emitted by the generator |
| `hardware/kicad/interposer/erc.rpt` | ERC report |

## Reference designators

KiCad requires numbered references, so the schematic uses conventional designators and carries the project role name in a visible `Role` field.

| Ref | Role (BOM) | Part | Nets |
|---|---|---|---|
| J1 | J_POWER | Würth 691137710002 | 1 BENCH_5V1_RAW, 2 BENCH_GND |
| F1 | F1 + FH1 | Littelfuse 021706.3MXP in Schurter 0031.8201.G | BENCH_5V1_RAW → FUSED_5V1 |
| J3 | J_RPIN | Samtec SSQ-102-01-G-S (Pololu 5383 VIN side) | 1 FUSED_5V1, 2 BENCH_GND |
| J4 | J_RPOUT | Samtec SSQ-102-01-G-S (Pololu 5383 VOUT side) | 1 PROTECTED_5V1, 2 BENCH_GND |
| R1 | RSH1 | Bourns MSR1-0R005F1 (`Device:R_Shunt`, 4-pin) | 1 PROTECTED_5V1, 4 DUT_5V_POST_SHUNT; Kelvin 2 KELVIN_PLUS_SRC, 3 KELVIN_MINUS_SRC |
| R2, R3 | R_SENSE_PLUS, R_SENSE_MINUS | Vishay PR01000108209JR500, 82 Ω | Kelvin source → SHUNT_KELVIN_PLUS / MINUS |
| R4 | R_VBUS | Vishay PR01000108209JR500, 82 Ω | DUT_5V_POST_SHUNT → DUT_VBUS_SENSE |
| J5 | J_SENSE | JST B4B-XH-A | 1 SHUNT_KELVIN_PLUS, 2 SHUNT_KELVIN_MINUS, 3 DUT_VBUS_SENSE, 4 MEAS_GND_REF |
| R5, R6 | R_PI_TX, R_PI_MARK | Vishay MRS25000C4700FCT00, 470 Ω | Pi GPIO14 → PI_TX_TO_PICO; Pi GPIO23 → PI_TASK_MARKER |
| R7 | R_PI_RX_PD | Vishay MRS25000C1003FCT00, 100 kΩ | PI_GPIO15_RXD → BENCH_GND |
| J6 | J_UART | JST B5B-XH-A | 1 SIGNAL_GND, 2 PI_TX_TO_PICO, 3 PI_GPIO15_RXD, 4 PI_TASK_MARKER, 5 no-connect |
| NT1, NT2 | NT_MEAS, NT_SIG | KiCad net ties | BENCH_GND ↔ MEAS_GND_REF; BENCH_GND ↔ SIGNAL_GND |
| J2 | J2 | Adafruit 2223 stacking socket | 2/4 DUT_5V_POST_SHUNT; 6/9/14/20/25/30/34/39 BENCH_GND; 8, 10, 16 UART/marker; all other pins pass straight through (no-connect on this board) |

The Pololu 5383 module itself is not a board component; it plugs into J3/J4 on its own TSW-102-07-G-S headers.

## Design choices made in capture

- **Pi-side UART/marker pins (default, owner may change):** Pi GPIO14 / pin 8 TX, GPIO15 / pin 10 RX (the Pi's standard UART0 pins), GPIO23 / pin 16 task marker. This was an open item; it is a one-line change in the generator.
- **Ground pickups as net ties:** MEAS_GND_REF and SIGNAL_GND are separate nets joined to BENCH_GND by NT1/NT2, so the layout can force a single tie point next to the Pi-header ground pins, as the connector contract requires.
- **Pins that only pass through** (all J2 nets not used on this board, including PI_3V3 pins 1/17 now that the Pi-RX pull-up is omitted) are drawn as no-connects with their contract name as text. The interposer does not join pins 1 and 17.
- Pico→Pi 470 Ω and the two Pi-output 100 kΩ pull-downs are on the carrier, per the UART qualification.

## Verification performed

| Check | Result | Scope |
|---|---|---|
| ERC, `kicad-cli 9.0.9 sch erc --severity-all --exit-code-violations` | 0 violations, exit 0 | No `.kicad_pro` yet, so KiCad default severities apply |
| Netlist export and pin comparison | 16 components, 45 nets; all 77 pins match the generator's intended map (by script) | Compares against the generator's own map; the map was transcribed from the contract CSVs listed above |
| Render review | PDF rendered and visually inspected by Claude (vision check passed this session): symbol classes, pin numbers, labels and J2 pinout against the Raspberry Pi header contract | One A3 page |
| Symbol/footprint mapping, DRC, parity | Not performed | Footprints are not assigned yet; that is AGENTS.md step 9 |

## Open items carried forward

- Owner confirmation of the Pi GPIO choice against the AI HAT+ / AI HAT+ 2 pin usage.
- Footprints, including the custom shunt footprint with separate Kelvin pads and the scoped hole exceptions, are not assigned.
- INA228 input currents on the downstream Kelvin and VBUS taps (a few µA) are inside the DUT boundary as measurement loading, as already recorded in the sense review.
- All qualification gaps recorded in the BOM and review documents remain open.

## Review record

On 2026-10-16 the owner stated that he does not have the skills to approve schematics. The technical review above was performed by Claude, not by the owner, and is the only schematic review to date. An independent human review has not been performed; that remains a release-checklist item. The owner's role at this gate is limited to plain-language decisions (pin use, proceeding to the next step).
