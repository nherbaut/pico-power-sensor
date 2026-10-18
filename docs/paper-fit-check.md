# Paper fit check (1:1 prints)

Files: `hardware/print/*-1to1*.pdf`, one A4 landscape page per board side, **printed at 100 % scale** (no "fit to page"). Measured from the PDF: carrier 78.0 × 54.0 mm, interposer 67.1 × 46.0 mm, matching the board outlines.

- `*-top-1to1.pdf`: top side, black and white, with pads, silkscreen and part outlines.
- `*-bottom-1to1-mirrored.pdf`: bottom side, mirrored as seen from below.

Check with a ruler first: the 78 mm carrier edge must measure 78 mm. Then, for each part, with the real component in hand:

1. Put each lead through the printed pad (pierce the paper with the lead). The lead must fall inside the pad and the hole circle.
2. Compare the part body with its printed outline (fuse holder, terminal J1, shunt R1, JST connectors, sockets, LEDs, DIP-14).
3. For the SO-8 (Q1): lay the chip on the printed pads; each leg tip must sit on a pad, pin 1 (dot) at the top-left pad.
4. Record anything that does not fit in `docs/footprint-review.md` and in `hardware/release-checklist.csv` (row FP) before ordering boards.

Does not replace a test with the real boards.
