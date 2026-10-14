# PCB implementation review, 2026-10-14

Scope: local draft maintenance using the pcb and kicad-design skills. No supplier uploads, purchases, fabrication release or hardware activation. KiCad 9.0.9, CLI and SWIG pcbnew were used. The visual capability probe passed in this session (512479); the KEMET page-12 drawing was inspected with the image viewer. That establishes access to the drawing, not physical fit.

## Independent one-pass review

A fresh reviewer performed a read-only, nonvisual consistency review. Its termination criterion was fixed before starting: one pass, ranked findings, checked-correct items and unresolved concerns, no iteration or edits. It regenerated into a scratch directory and reported:

| Finding | Evidence | Resolution |
|---|---|---|
| R1: native PCB metadata disappeared on regeneration | Zero populated MPN/Datasheet fields on generated boards versus 29 interposer and 32 carrier component fields in the saved design | Shared native-field helper plus direct-generator properties; scratch regeneration test reads both boards and checks fields against the selected parts |
| R2: carrier generator restored an obsolete blank socket selection | Extra "Pico socket strips" BOM row said to select a part although SSW-120-01-G-S was already selected | Removed the duplicate purchasing row from the logical board BOM; the physical assembly list contains the two selected strips |

The reviewer also confirmed selected MPN consistency, owned Pico quantity zero, two socket strips, separate fuse/holder, zero purchased test pads, and exclusion of logical off-board J5. It independently reproduced divider equations and the 96.625 mV resistance subtotal. It did not review solderability, visual layout, electrical suitability or physical fit. Parent verification covers the corrections; there was no second independent review pass.

## Diagnostic copper model

The [copper screen](copper-screen.json) uses the saved board and is reproducible with `make copper-screen`. It requires the kicad-design solver and numpy/scipy/shapely in addition to the normal project tools. This is an optional diagnostic, not part of website generation or a fabrication gate.

The first unadapted solver call incorrectly reported disconnected copper because its name-based parser omitted KiCad 9 tracks carrying numeric net IDs. Native DRC reported zero unconnected items. That result was rejected as a tool-input incompatibility. The wrapper expands net names only in an analysis text file, then checks all 154 pad coordinates/nets, 1,980 track records and 138 vias against pcbnew. KiCad 9.0.9 lacks the newer CLI refill/save options, so a complete scratch project is refilled and saved with pcbnew before native DRC. The live PCB is untouched.

A 20 × 2 mm rectangle at 70 µm copper gives 2.464 mΩ versus 2.463 mΩ analytically. A deliberately broken rectangle must report disconnected. For the actual shunt-to-Pi positive branch, ideal tying of both 5 V contacts gives 4.335 mΩ on a 0.10 mm grid and 4.238 mΩ on a 0.05 mm grid: about **21.2 mV at 5 A** at the finer grid. The grid change is about 2.3%; this is a diagnostic estimate, not a guaranteed bound.

Adding this branch estimate to the 96.625 mV mixed component reference subtotal gives about **117.8 mV**, before upstream/return copper, fuse-holder and header contact losses or further heating. The present design does not demonstrate the 100 mV target. The tool approximates pad shapes and uses a fixed interlayer resistance; it does not simulate heating or dynamic behavior. No physical result is implied.

## Open review scope

The remaining gates include exact MOSFET/socket/microSD and other footprint comparisons, power-path redesign/budget, startup SOA, transient limits, SD sequencing and mechanical evidence. Existing schematics use generic component boxes; their conversion to conventional electrical symbols and a page-by-page readability review remain open. ERC does not close that task. Effective KiCad default rule severities also require a complete version-specific release audit; empty project exclusions alone do not establish it.
