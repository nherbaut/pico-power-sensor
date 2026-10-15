# JLCPCB quote package

This page describes how to get a price from JLCPCB for the two boards, with factory placement of the surface-mount parts. It does not authorise an order: both boards are still **not released** (see the [release procedure](release.md)), so the package is for a quote only and is labelled that way.

## What is generated

`make jlc-quote` writes, for each board, a folder under `.build/jlc-quote/<board>/` (ignored by git):

| File | Use |
|---|---|
| `<board>-gerbers-QUOTE-ONLY.zip` | Copper, mask, silkscreen, outline and drill files from the saved KiCad board |
| `<board>-BOM-quote-only.csv` | Bill of materials in JLCPCB's columns: Comment, Designator, Footprint, LCSC Part # |
| `<board>-CPL-quote-only.csv` | Placement file: Designator, Mid X, Mid Y, Layer, Rotation |
| `<board>-parts-to-map.csv` | Each part with its manufacturer reference, specification and a flag for the parts to check first |
| `QUOTE-ONLY.txt` | The notice that these files are not a release |

The BOM and the placement file cover only the parts the factory is meant to place (24 on the interposer, 32 on the carrier, from the [assembly planning list](../hardware/assembly-review.csv)). A test checks that they match that list exactly. Through-hole parts, the owned Pico and the bare test pads are left out.

## What you still have to do

1. **Map each part to a JLCPCB part number.** The LCSC column is empty on purpose. JLCPCB's upload tool tries to match parts and reports the ones it cannot find. Start with the rows flagged `check_first` in the parts file. A substitute must keep the specification; the precision divider resistors (0.1 %, 25 ppm/K) and the C0G capacitor are not interchangeable with looser parts.
2. **Check stock and the extra fee for each distinct part** on JLCPCB's site; both change over time and are not recorded here.
3. **Check every placement in JLCPCB's viewer.** Rotations are KiCad's and are not corrected for JLCPCB's package conventions.
4. **Choose the options** on their order page: copper weight (the interposer is designed for 70 µm, the carrier for 35 µm; confirm that JLCPCB offers 70 µm on two layers and that its minimum track and spacing rules accept 0.2 mm tracks and the 0.65 mm pitch parts), surface finish, quantities, which side is assembled (all factory-placed parts are on the top side) and shipping to France, including VAT and customs.
5. **Hand-solder the rest:** the power header, the 40-pin stacking socket, the fuse holder and the JST connectors on the interposer; the Pico socket strips and the JST connectors on the carrier. The fuse is inserted last.

## Limits

- The interposer has no paste Gerber (the carrier does); JLCPCB should build the stencil from the pads, which should be confirmed in their review.
- The package comes from the saved boards as they are today. The open items in the [release checklist](../hardware/release-checklist.csv) (the remaining footprint comparisons, the physical mock-ups, the assembler's own rules, the measured voltage-drop budget) must be closed before an order is placed.
- Nothing here uploads files or places an order. Sending the files to JLCPCB shares the design with a third party and is done by the project owner.
