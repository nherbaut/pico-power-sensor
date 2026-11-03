# Interposer layout, revision 1

Date: 2026-10-16. Status: **completed PCB implementation candidate, not a fabrication release.** DRC, parity and the copper checks below were run by Claude; no physical fit, footprint sign-off against delivered parts or bench test has been done.

Source of truth: `hardware/kicad/gen_interposer_pcb.py` (placement and all copper), using `hardware/kicad/pcblib.py` and the project library built by `hardware/kicad/gen_footprints.py`. Do not edit `interposer.kicad_pcb` in the GUI; regenerate.

## Fixed geometry (inherited, unchanged)

Stepped outline (0,0)–(66,0)–(66,37)–(67.13,37)–(67.13,46)–(0,46); NPTH M2.5 holes at (5.13, 41.27) and (63.13, 41.27); Pi stacking header pad 1 at (10, 42.54), pad 2 at (10, 40). The generator places these from `docs/mechanical-baseline.md`; the header now uses the approved 1.10 mm holes / 2.00 mm pads.

## Floorplan and rationale

| Area | Parts | Why |
|---|---|---|
| Right edge and top, right to left | J1 bench terminal (wire entry at the right edge), Q1 Si4143DY (SO-8) below J1 with source pads on the left and drain pads on the right, R8 gate resistor below Q1, F1 fuse holder | Order J1 → Q1 → F1 → R1. The 5 A path is carried by two copper pours: J1 pin 1 to the four drain pads, and the three source pads to F1 pin 1. Fuse and terminal stay at the board edge for access |
| Left column | R1 shunt, standing vertically | Shortest path from the fuse output to Pi pins 2/4; Kelvin pickups at the inner edge of each lead pad, current enters/leaves from the outer side |
| Centre | R2/R3 (Kelvin 82 Ω), R4 (VBUS 82 Ω), J5 sense connector | Observation resistors sit at the source, before the cable. Kelvin pair routed side by side to J5 |
| Above the header | R5/R6 (470 Ω), R7 (100 kΩ), J6 UART connector | Short runs from Pi pins 8, 10, 16 |
| Next to header pins 30 and 34 | NT2 (SIGNAL_GND), NT1 (MEAS_GND_REF) | The two cable grounds join bench ground at one point beside the Pi ground pins |
| Bottom layer | Bench ground plane | Return path for the 5 A load from the Pi ground pins to J1 pin 2 |

VBUS for the monitor is picked up at Pi header pin 4 itself, on a thin bottom-layer trace, so the copper drop between shunt and header is included in the measured bus voltage.

## Copper

- 5 A positive path on the top layer: 2.5 mm tracks (2.0 mm where a neighbouring pad forces it) plus copper pours for each segment (raw, fused, protected, DUT 5 V).
- Signals 0.3 mm. Stackup assumed: 2 layers, 1.6 mm FR-4, 1 oz (35 µm) copper both sides. This is an assumption to confirm with the chosen fabricator.
- Ground: bottom-layer pour; the eight Pi ground pins use solid (not thermal) connections because the 2.54 mm pitch leaves no room for thermal spokes. Expect to need more iron heat on those joints.

A top-layer bench-ground fill (lowest priority) covers all free top copper and adds return paths to the Pi ground pins.

**DC copper resistance, `copper_guards.py resistance` (calculation from the saved, filled board; not a measurement).** 1 oz, 20 °C, 0.05 mm grid, 0.2 mΩ per plated-hole site. Bounds: 2 mΩ per positive segment (10 mV at 5 A) and 3 mΩ per ground branch, chosen against the provisional 100 mV whole-path budget before running.

| Path | Result |
|---|---|
| J1+ → Q1 drain | 1.76 mΩ |
| Q1 source → F1 | 0.85 mΩ |
| F1 → R1 | 1.58 mΩ |
| R1 → J2 pin 2 / pin 4 | 0.96 / 1.20 mΩ |
| J1− → Pi ground pins 6, 9, 14, 20, 25, 30, 34, 39 | 1.40, 2.85, 1.26, 1.09, 2.62, 0.88, 0.80, 1.02 mΩ |

All pass (revision with the Si4143DY, 2026-10-17; raw output in `hardware/kicad/interposer/copper-resistance.txt`). Positive copper ≈ 5.0 mΩ, about 25 mV at 5 A, plus Q1's own on-resistance: Vishay datasheet maximum 9.2 mΩ at −4.5 V and 5 A (46 mV, 0.23 W at 25 °C; calculation, not measured, and higher when warm). Two branches have little margin: Pi ground pin 9 (0.15 mΩ, an inner-row pin hemmed in by neighbouring pads) and J1+ → Q1 drain (0.24 mΩ, the strip between J1's ground pin and the board edge). Ground stitching vias and a 0.25 mm ground-pour clearance were added to reach this. Run note: the guard reads KiCad 10 net syntax, so it was run on a scratch copy made with `hardware/kicad/tools/netnames_for_guard.py` (same geometry), in the venv `~/.venvs/kicad-tools`, at 0.05 mm grid (the default 0.2 mm grid rasterizes thin tracks as disconnected).

## Verification

| Check | Result |
|---|---|
| `kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations` | 0 violations, 0 unconnected, parity: 4 `footprint_filters_mismatch` warnings only (project library names do not match the stock symbols' filter patterns; expected) |
| Severity map | The generator promotes `pth_inside_courtyard`, `npth_inside_courtyard`, `missing_courtyard` to error and the footprint filter/type checks to warning; KiCad's stock project ignores them |
| Copper collision audit (`kicad_copper_collisions.py`) | 2 contacts, both intended: R1 pad 1↔2 and pad 3↔4, the Kelvin pickups declared as net-tie pad groups in the shunt footprint |
| Render review | Front copper/silk and back copper rendered and inspected by Claude |
| DC copper resistance guard | PASS on all 13 power branches (table above) |

## Stacking height: blocking finding for the AI HAT case

The interposer plugs onto the Pi with the Adafruit 2223 stacking socket underneath it; a HAT plugged onto the protruding pins sits roughly one HAT-socket height (about 8.5 mm, estimated, not measured) above the interposer's top face. Several selected parts are taller (nominal or drawing values, not measured):

| Part | Height above the interposer |
|---|---|
| Q1 (SO-8) | about 1.75 mm (package maximum) |
| Schurter fuse holder with cover | about 12.7 mm |
| Würth bench terminal | about 11.5 mm (drawing) |
| JST XH header with mated housing | about 9–10 mm (estimate) |
| MSR1 shunt | up to 7.6 mm (datasheet 5.1 ± 2.5 mm) |

So the board works without a HAT, but an AI HAT cannot sit directly on it. **Owner decision 2026-10-17 ("yes"): raise the HAT.** Plug a second Adafruit 2223 onto the interposer's J2 pins as an extender and mount the HAT on it with longer M2.5 stand-offs. Estimated HAT gap becomes about 17 mm (two socket heights) against about 12.7 mm for the tallest part (fuse holder), a margin of about 4 mm. These are drawing estimates; the stack and stand-off lengths must be measured after first assembly. No board change is needed. Both items are in the BOM.

## Open items

- Active Cooler clearance under the interposer, including solder tails on the bottom face: not checked.
- Footprints are derived from drawings, not from delivered parts; see `docs/footprint-review.md`.
- Fabricator finished-hole tolerance for the scoped hole exceptions.
