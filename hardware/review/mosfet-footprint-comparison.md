# MOSFET footprint comparison (Q1, Q2)

Date: 2026-10-15. Source: Infineon BSC010N04LS6 datasheet, Rev. 2.3 (2022-07-21), page 11, Figure 2 "Outline Boardpads (PG-TDSON-8-FL)". Compared with the local `SuperSO8_Draft` footprint, which is the KiCad `Package_TO_SOT_SMD:TDSON-8-1` snapshot. This is a dimensional comparison of drawings. The values from the figure were read from its printed dimensions and cross-checked by measuring the rendered page; confirm them against the original PDF before changing CAD. No PCB file was changed.

Coordinates below follow the pin axis: distances run from the package centre toward the lead side, in mm.

| Feature | Infineon recommended | Local footprint | Difference |
|---|---|---|---|
| Drain pad width (across the leads) | 4.41 | 4.41 | none |
| Drain pad outer edge | 3.325 from centre | 3.325 | none |
| Drain pad edge nearest the leads | 1.13 from centre | 1.225 | local pad stops 0.095 short |
| Lead pads: width | 0.5 | 0.5 | none |
| Lead pads: pitch | 1.27 | 1.27 | none |
| Lead pads: outer edge | 3.325 | 3.325 | none |
| Lead pads: inner edge | 2.27 | 2.475 | local pads 0.205 shorter (0.85 against 1.055 long) |
| Gate pad position | 1.905 from the pad-row centre line | 1.905 (pad 4) | none |
| Source pads | one merged pad 3.19 wide under the three source leads | three separate 0.5 mm pads | different copper shape |
| Gap between drain pad and lead pads | about 1.14 | 1.25 | local gap larger by about 0.1 |
| Stencil | drain: four apertures of 1.7 x 1.4; leads: separate small apertures | four 1.5 x 1.5 paste pads on the drain; one aperture per lead pad | different apertures |
| Solder mask | a larger opening that covers the pad group | per-pad openings | not compared in detail |

## Reading

- Pin numbering, the gate position and the drain width match, so the device connects correctly: pads 1 to 3 are the source, pad 4 the gate and pad 5 the drain.
- The local pads are shorter than recommended and the three source pads are not merged. For a path that carries up to 5 A through two MOSFETs in series, Infineon's merged source pad has more copper under the leads and is the safer layout.
- These differences were not found to be an electrical fault. They are departures from the manufacturer's recommended land pattern, and their effect on solder joints and on voltage drop has not been measured.

## Proposed change (not applied)

Adopt the Infineon pattern: a 3.19 x 1.055 source pad, a 0.5 x 1.055 gate pad, a drain pad edge 1.13 from the centre, and the manufacturer stencil apertures. Because it changes copper in the high-current path of the routed interposer, it needs a deliberate edit of both footprints, native DRC, a recheck of the source-to-source and drain connections, and a recalculation of the copper drop. The assembler's own stencil and mask rules still apply.
