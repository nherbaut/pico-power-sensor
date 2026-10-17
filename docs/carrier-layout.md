# Carrier layout, revision 1

Date: 2026-10-17. Status: **completed PCB implementation candidate, not a fabrication release.** Checks by Claude; no physical fit or bench test.

Source of truth: `hardware/kicad/gen_carrier_pcb.py`, which places every part and produces all signal copper with `hardware/kicad/gridroute.py`, a small deterministic two-layer grid router that is part of the generator (no external autorouter). Do not edit `carrier.kicad_pcb` in the GUI; regenerate. A full regeneration takes about two minutes.

## Fixed geometry (inherited, unchanged)

78 × 54 mm rectangle; NPTH M2.5 holes at (4,4), (74,4), (4,50), (74,50); Pico sockets with pad 1 at (44, 3), pad 20 at (44, 51.26), pad 21 at (61.78, 51.26), pad 40 at (61.78, 3). The generator asserts these pad positions, plus the MikroE and microSD header positions from `docs/carrier-module-fit.md`, every run.

## Floorplan

| Area | Parts | Notes |
|---|---|---|
| Pico sockets J1/J2 (front) | Pico 2 WH | J2 is rotated 180° so its pin 1 is Pico pin 21 at the bottom |
| Front, left of the Pico | MikroE sockets J3/J4 | Module sits about 11 mm above the board |
| Back, under the lower half of the MikroE position | U1 (DIP-14 socket), C2 | Moved from the front at the owner's request (2026-10-17) so nothing sits under the MikroE module. Pins 1–7 at x = 20.62 mm, pins 8–14 at x = 13 mm, y = 26–41.24 mm. Lateral gap to the microSD module envelope (y ≤ 23.9 mm) about 0.5 mm at courtyard level; check with the delivered module |
| Back, under the MikroE area | microSD socket J5 | Header row at y = 21.32 mm, pin 1 at x = 31.36 mm; card slot faces the top edge |
| Top edge | J6 wire pads, C1 | Short wires from J6 to the MikroE IN1+, IN1−, IN2 VBUS screw terminals; C1 across the Kelvin pair right there |
| Left edge | J7 sense, J8 UART | Cables leave to the left toward the interposer |
| Strip between MikroE and Pico | R1–R5 standing resistors | Pull-ups, pull-downs, 470 Ω |
| Right edge | R6–R10 and LED1–LED5 | LEDs at the edge for visibility |

## Copper

Signals 0.25 mm, INSTR_3V3 and routed ground 0.4 mm, vias 0.6 / 0.3 mm. Instrument ground is routed and also poured on both layers. Three ground pads (U1 pin 7, J1 pin 8, R2 pin 2) use solid pour connections because thermal spokes cannot form there; they are also tied by routed copper. Stackup assumption: 2 layers, 1.6 mm, 1 oz.

## Verification

| Check | Result |
|---|---|
| `kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations` | 0 violations, 0 unconnected; parity: 8 `footprint_filters_mismatch` warnings only (library naming, expected) |
| Severity map | Courtyard checks promoted to error by the generator |
| Copper collision audit | 0 collisions (637 copper items) |
| Render review | Front and back copper/silk rendered and inspected by Claude |

## Open items

- Stand-off height must exceed the back-mounted microSD stack (socket 8.5 mm plus module) when the carrier sits on the bench.
- Actual MikroE screw-terminal order before wiring J6; header mating checks from `docs/carrier-socket-options.md`.
- Back side now carries the microSD module and U1/C2: standoffs must clear both (socket + IC about 8 mm; microSD stack about 8.5 mm plus module).
