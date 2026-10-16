# Interposer layout, revision 1

Date: 2026-10-16. Status: **completed PCB implementation candidate, not a fabrication release.** DRC, parity and the copper checks below were run by Claude; no physical fit, footprint sign-off against delivered parts or bench test has been done.

Source of truth: `hardware/kicad/gen_interposer_pcb.py` (placement and all copper), using `hardware/kicad/pcblib.py` and the project library built by `hardware/kicad/gen_footprints.py`. Do not edit `interposer.kicad_pcb` in the GUI; regenerate.

## Fixed geometry (inherited, unchanged)

Stepped outline (0,0)–(66,0)–(66,37)–(67.13,37)–(67.13,46)–(0,46); NPTH M2.5 holes at (5.13, 41.27) and (63.13, 41.27); Pi stacking header pad 1 at (10, 42.54), pad 2 at (10, 40). The generator places these from `docs/mechanical-baseline.md`; the header now uses the approved 1.10 mm holes / 2.00 mm pads.

## Floorplan and rationale

| Area | Parts | Why |
|---|---|---|
| Top edge, right to left | J1 bench terminal (wire entry at the right edge), F1 fuse holder, Pololu module sockets J3 (VIN) / J4 (VOUT) | The 5 A path runs right to left along the top so it ends near Pi header pins 2/4, which are at the left end of the header. Fuse and terminal are at the board edge for access |
| Left column | R1 shunt, standing vertically | Shortest path from the Pololu output to Pi pins 2/4; Kelvin pickups at the inner edge of each lead pad, current enters/leaves from the outer side |
| Centre | R2/R3 (Kelvin 82 Ω), R4 (VBUS 82 Ω), J5 sense connector | Observation resistors sit at the source, before the cable. Kelvin pair routed side by side to J5 |
| Above the header | R5/R6 (470 Ω), R7 (100 kΩ), J6 UART connector | Short runs from Pi pins 8, 10, 16 |
| Next to header pins 30 and 34 | NT2 (SIGNAL_GND), NT1 (MEAS_GND_REF) | The two cable grounds join bench ground at one point beside the Pi ground pins |
| Bottom layer | Bench ground plane | Return path for the 5 A load from the Pi ground pins to J1 pin 2 |

VBUS for the monitor is picked up at Pi header pin 4 itself, on a thin bottom-layer trace, so the copper drop between shunt and header is included in the measured bus voltage.

## Copper

- 5 A positive path on the top layer: 2.5 mm tracks (2.0 mm where a neighbouring pad forces it) plus copper pours for each segment (raw, fused, protected, DUT 5 V).
- Signals 0.3 mm. Stackup assumed: 2 layers, 1.6 mm FR-4, 1 oz (35 µm) copper both sides. This is an assumption to confirm with the chosen fabricator.
- Ground: bottom-layer pour; the eight Pi ground pins use solid (not thermal) connections because the 2.54 mm pitch leaves no room for thermal spokes. Expect to need more iron heat on those joints.

**Calculated track resistance, tracks only (pours add parallel copper, not counted):** raw 1.5 mΩ, fused 1.7 mΩ, protected 2.4 mΩ, DUT 5 V 3.6 mΩ; sum 9.2 mΩ, i.e. about 46 mV and 0.23 W at 5 A. Basis: ρ = 1.72×10⁻⁸ Ω·m, 35 µm, 20 °C, length/width of each saved track; this is a calculation, not a measurement, and the pours should lower it. The skill's copper-resistance guard (`copper_guards.py resistance`) could not run: it needs `shapely` and `scipy` in KiCad's Python, which are not installed. That gate is **open**.

## Verification

| Check | Result |
|---|---|
| `kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations` | 0 violations, 0 unconnected, parity: 6 `footprint_filters_mismatch` warnings only (project library names do not match the stock symbols' filter patterns; expected) |
| Severity map | The generator promotes `pth_inside_courtyard`, `npth_inside_courtyard`, `missing_courtyard` to error and the footprint filter/type checks to warning; KiCad's stock project ignores them |
| Copper collision audit (`kicad_copper_collisions.py`) | 2 contacts, both intended: R1 pad 1↔2 and pad 3↔4, the Kelvin pickups declared as net-tie pad groups in the shunt footprint |
| Render review | Front copper/silk and back copper rendered and inspected by Claude |
| DC copper resistance guard | Not run (missing Python packages) |

## Stacking height: blocking finding for the AI HAT case

The interposer plugs onto the Pi with the Adafruit 2223 stacking socket underneath it; a HAT plugged onto the protruding pins sits roughly one HAT-socket height (about 8.5 mm, estimated, not measured) above the interposer's top face. Several selected parts are taller (nominal or drawing values, not measured):

| Part | Height above the interposer |
|---|---|
| Pololu 5383 on SSQ sockets | about 13.5 mm (docs/power-connector-options.md stack model) |
| Schurter fuse holder with cover | about 12.7 mm |
| Würth bench terminal | about 11.5 mm (drawing) |
| JST XH header with mated housing | about 9–10 mm (estimate) |
| MSR1 shunt | up to 7.6 mm (datasheet 5.1 ± 2.5 mm) |

So the board works without a HAT, but an AI HAT cannot sit directly on it. This needs an owner decision (raise the HAT with an extra 2×20 extender and longer stand-offs, or change the stack order); see the thread. Not resolved in this revision.

## Open items

- Active Cooler clearance under the interposer, including solder tails on the bottom face: not checked.
- Footprints are derived from drawings, not from delivered parts; see `docs/footprint-review.md`.
- Fabricator finished-hole tolerance for the scoped hole exceptions.
