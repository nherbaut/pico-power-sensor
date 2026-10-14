# Hardware review evidence

Review date: 2026-10-14. Both boards remain **not released for fabrication or DUT connection**. The user-authorized LED/shunt/socket corrections are integrated into native CAD and generators; board placement, outlines and routing are retained, with copper zones refilled. An [initial paper mock-up photograph](../../tests/mechanical/paper-mockup-2026-10-14.md) is recorded as partial mechanical evidence; no assembled-board bench validation has been performed.

## Records

The [follow-up review and integrated CAD corrections](footprint-corrections.md) document the corrected LED/shunt/socket geometry, verified fuse DC rating, tighter drop budget and explicit bulk-capacitor alternative. Historical candidate archives remain available for comparison; main board packages contain current CAD.

| Record | Purpose |
|---|---|
| [Release checklist](../release-checklist.csv) | Separate prototype fabrication and assembled-board connection gates |
| [Passive proposals](../passive-proposals.csv) | Exact prototype selections integrated into CAD/BOM; not purchases or release approval |
| [Footprint review](footprint-review.csv) | Library provenance, partial dimensional checks and remaining manufacturer review |
| [Power-path budget](power-path-budget.csv) | Datasheet reference resistances and explicit unknowns; no measured total |
| [Design analysis](design-analysis.json) | Reproducible threshold and resistance calculations |
| [Implementation review](implementation-review.md) | Independent generator review, corrected metadata and diagnostic copper loss calculation |
| [Copper screen](copper-screen.json) | Approximate shunt-to-header copper resistance; explicitly not physical measurements |
| [Interposer pad geometry](interposer-geometry.json) | Actual native pad positions, drills, numbering and nets |
| [Carrier pad geometry](carrier-geometry.json) | Actual native pad positions, drills, numbering and nets |

Fresh automated evidence: interposer [source checks](interposer-source-check.json), [ERC](interposer-erc.rpt), [DRC](interposer-drc.rpt); carrier [source checks](carrier-source-check.json), [ERC](carrier-erc.rpt), [DRC](carrier-drc.rpt). Both native checks report zero violations, zero unconnected pads and zero parity issues; project DRC exclusions are empty. The regression suite covers component integration and engineering calculations, with passing tests, including integrated footprint/generator checks, release-record rejection tests and OV-recovery reporting. These findings do not establish mechanical fit or electrical performance.

## Printable mock-ups

Download the [interposer full-size PCB plot](interposer-mockup.pdf) and [carrier full-size PCB plot](carrier-mockup.pdf). These are front views of actual CAD pads, fabrication outlines and board edges, not manufacturing files. Each has a 50 mm print-calibration ruler. Run `make hardware-review` to refresh them and the geometry/calculation JSON after changes. This requires KiCad 9 CLI, the distribution Python `pcbnew` module, and `pypdf`/`reportlab` in the `python3` environment; it does not modify either board or run bench tests. Normal website builds do not require these tools.

Print at **100% / actual size**, without fit-to-page or mirroring. Before cutting, measure the interposer H1-to-H2 spacing: **58 mm centre to centre**. The carrier's mounting holes also have **58 mm horizontal spacing** and **46 mm vertical spacing**. A correctly scaled print checks locations; it cannot prove installed heights, engagement or electrical polarity. Do not insert conductive substitutes into a powered Pi.

Follow [mechanical acceptance](../../tests/mechanical/README.md). Photograph the unpowered Pi/Active Cooler/HAT assembly, record the exact connector and spacer parts, and leave absent HATs marked not tested. Both AI HAT versions require fit evidence before a compatibility claim or this project's fabrication gate can pass.

## Design findings

The [LTC4367 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf), page 4, supports boosted gate drive at a 5 V input/output. This supports the selected logic-level MOSFET's steady-state drive; it does not settle startup SOA or transients. Initial-tolerance calculations give OV trip 5.250–5.430 V and OV recovery 4.909–5.216 V. Recovery at the normal 5.10 V setting is therefore **not guaranteed after an OV trip**. The source checker now reports that limitation explicitly. Review a validated recovery procedure or revise the circuit before release; do not assume returning the supply to 5.10 V reconnects it. Adding independent 25 ppm/K resistor drift over the assumed -40..85 C range widens these calculated intervals. Leakage, ageing, dynamics and the applicability of the specified hysteresis conditions remain open.

The 100 mV loop-drop target at 5 A allows **20 mOhm total** between the input connector and the Pi's powered rail/return through its mating header. The component reference subtotal, including input contacts, is **19.325 mOhm / 96.625 mV**. The subsequent shunt-to-header copper calculation adds about **21.2 mV**, before other missing contributions. The resulting approximately **117.8 mV** subtotal does not demonstrate the target. This is an incomplete calculation, not a measured or guaranteed bound. External Korad leads add losses outside that board-level target. Read the [current diagnostic and limitations](implementation-review.md).

The [TI EVM guide](https://www.ti.com/lit/ug/sbou241e/sbou241e.pdf), page 31, lists R1 with quantity zero. The external Kelvin arrangement is consistent with that revision. Inspect the actual received EVM: a fitted R1 would create a parallel path across the interposer shunt. Connector orientation, EVM revision and CS-switch configuration still require confirmation.

The footprint names containing “Draft” do not imply that all present geometry is hand-drawn: several are snapshots of native KiCad library parts. The geometry inventory records their source. Library provenance and matching pitch alone do not approve the exact manufacturer's copper, mask, paste, drill, package or installed orientation. Interposer C1 now uses a capacitor footprint and C2 uses the selected Murata land pattern; remaining component-specific reviews are recorded separately. The microSD manufacturer's current PDF could not be retrieved during this review, so that review remains open.

## Remaining work

Before **prototype fabrication**: finish remaining footprint and selected-component reviews; verify selected Pico socket strips and choose remaining hardware; close power/circuit/routing reviews and complete the remaining rigid physical checks; confirm fabrication capabilities and inspect the final manufacturing package. The fuse's DC interrupting specification is now reviewed; its assembled drop remains open. The carrier now explicitly uses the selected 22 uF X5R part. Capacitor effective values, the operating temperature envelope and SD supply sequencing/thermal capability need review. Source regeneration must not overwrite future manual CAD edits.

Before **DUT connection**: assemble a released prototype, perform continuity checks, validate faults/startup with a dummy load, measure 5 A voltage drop and temperature, validate power-off UART behaviour, and calibrate sensing. Independently validate carrier power, LEDs, SPI and SD writes with the actual card. Firmware/test fixtures for those exercises remain a separate milestone. The supplied checklist is the record of these requirements, not permission to energize hardware.

See the [current design review](../../docs/design-review.md), [assembly sourcing comparison](../../docs/assembly-sourcing.md) and [fablab procedure](../../docs/fablab-validation.md). Fablab equipment access is confirmed; physical measurements remain pending.

## Full-loop follow-up

The [electronic protection study](../../docs/electronic-protection.md) now includes all six copper branches, giving an approximately **132.8 mV** mixed reference subtotal at 5 A. This supersedes the earlier 117.8 mV calculation, which included only the shunt-to-header copper. The [copper comparison](power-path-candidate-copper.json) gains about **4.0 mV** over the full loop; it does not meet the 100 mV requirement. The [isolated candidate](power-path-candidate.zip) is not promoted. The shared-shunt comparator architecture remains a study with explicit power-state/timing/measurement gates.
