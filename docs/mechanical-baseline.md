# Inherited PCB geometry

Recorded: 2026-10-15. The owner reports checking the earlier project's hole and pin fit with the Pi/Pico hardware and authorizes retaining the PCB dimensions. Reuse the earlier outlines, mounting-hole positions and header geometry rather than redesigning that geometry from scratch.

This is owner-reported physical fit evidence. The dimensions below were separately extracted from the existing KiCad board files; they are CAD dimensions, not new physical measurements. The owner did not identify the exact revision used for the earlier check, so this record does not claim that every feature of the latest source files was physically tested.

## Source snapshots and geometry

Sources are read-only inputs in `/home/nherbaut/workspace/picopower/hardware/pcb/`. KiCad 9's `pcbnew.LoadBoard` was used to inspect them without saving or regenerating either board. Dimensions use Edge.Cuts segment coordinates, excluding graphic stroke width. Coordinates below are in millimetres in each source board's existing coordinate system, with outline top-left at (0, 0).

| Feature | Interposer | Carrier |
|---|---|---|
| Source file | `interposer/interposer.kicad_pcb` | `carrier/carrier.kicad_pcb` |
| Outline | Main body 66 × 46; local right extension gives 67.13 × 46 overall | 78 × 54 rectangle |
| Mounting holes | H1 (5.13, 41.27); H2 (63.13, 41.27); 58 centre spacing | H1 (4, 4); H2 (74, 4); H3 (4, 50); H4 (74, 50) |
| Mounting-hole drills | 2.7, non-plated | 2.7, non-plated |
| Module/header reference | J2, 40 pads | J_PICO, 40 pads |
| Header pad 1 | (10, 42.54) | (44, 3) |
| Header pad 2 | (10, 40) | (44, 5.54) |
| Header pad 20 | (32.86, 40) | (44, 51.26) |
| Header pad 21 | (35.4, 42.54) | (61.78, 51.26) |
| Header pad 39 | (58.26, 42.54) | (61.78, 5.54) |
| Header pad 40 | (58.26, 40) | (61.78, 3) |
| Header geometry | 2 rows of 20; 2.54 pitch and row spacing | 2 rows of 20; 2.54 pitch, 17.78 row spacing |
| Header drills | 1.0 | 1.0 |

Interposer outline vertices, in sequence, are (0, 0), (66, 0), (66, 37), (67.13, 37), (67.13, 46), (0, 46), closing at (0, 0). Preserve the actual stepped outline rather than replacing it with its bounding rectangle.

Source SHA-256 values at extraction:

```text
interposer/interposer.kicad_pcb
cd8e2543feea22bc887833a3ac588761d97749ec2df5c10eb1f2cf6ba587820c

carrier/carrier.kicad_pcb
be058611111f173023c39e1187417429d09f40d7b959f5a8bae823f64e744cac
```

## Reuse and remaining checks

Owner-approved change (2026-10-16), not yet implemented in CAD: the selected Adafruit 2223 square-pin Pi stacking socket may use 1.10 mm nominal finished plated holes (±0.05 mm) and 2.00 mm pads for all 40 leads. This is a scoped change from the source's 1.00 mm header drills, preserving every pad centre, the stepped outline and both mounting holes. The source dimensions and hashes above remain the historical extraction. This exception does not cover other 40-pin or carrier sockets. Actual connector revision, insertion, mating depth and changed assembly heights remain unverified; see the [Pi/harness review](pi-harness-connector-options.md).

- Preserve the source outline shape, mounting positions and complete header pad pattern when implementing the new boards. Compare transferred geometry with the source; the selected pad coordinates above are reference points, not a replacement for all 40 pad positions.
- Preserve mechanical header numbering and orientation. Assign and verify the new electrical nets separately; the earlier electrical circuitry and signal assignments are not approved by this mechanical reuse decision.
- Source drills and pad geometry still require comparison with the final purchased connector or socket. Geometry reuse does not select an exact connector, prove its solderability or complete its manufacturer-footprint review.
- Place new through-hole parts and assembled modules within the inherited outlines. If a suitable module or assembly clearance does not fit, report the conflict and proposed change before enlarging the board or moving its holes/header.
- The owner has supplied prior hole/pin fit evidence. Do not request a repeat of unchanged geometry merely to restart the design process. Check new or changed component heights, sockets, soldered leads, support hardware, cooler airflow and HAT clearance where those changes affect fit.
- Earlier paper-fit records in the sibling project predate a carrier-outline change. The 78 × 54 carrier above is the current saved CAD baseline; this document does not relabel those older photographs as evidence of that exact revision.
- Case compatibility, support heights, connector engagement, populated cooler/HAT clearance and electrical release remain separate checks. No new physical test, ERC, DRC or release approval is claimed here.
