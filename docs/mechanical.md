# Mechanical compatibility

The design is a GPIO-edge interposer with an outward side wing. The header strip is component-free; populated parts, fuse access and power plug remain outside the Pi footprint. A long-tail stacking socket preserves all 40 contacts.

## Mounting holes

The KiCad PCB includes H1 and H2 beside the GPIO connector ends: two 2.7 mm non-plated holes, 58 mm apart, for M2.5 hardware. A 6 mm diameter copper keepout is enforced on both sides. H2 has a small outward board extension; the full envelope is 67.13 x 46 mm. Positions are provisional and must be checked against the physical Pi 5, not just the nominal spacing.

Use lower standoffs to support the interposer and upper spacers to support a HAT on the same columns. Choose lengths after measuring the fully seated stacking connector and checking cooler/PCIe clearance; tightening must not flex either board. Check that actual hardware fits the 6 mm reserved diameter and does not contact the socket body. The board remains a cantilever, so secure the power cable separately.

## Mandatory physical checks

| Check | Acceptance |
|---|---|
| H1/H2 alignment | Both screws enter freely with the GPIO connector fully seated; no forcing |
| Mounting hardware | Spacer/head/washer diameter fits keepout; no copper or socket contact |
| Lower mating connector | Correct pin-1 orientation and full engagement on Pi 5 |
| Upper tails | Adequate engagement in the actual AI HAT socket without bottoming |
| Active Cooler | No contact with board, solder joints, support or leads; fan air path clear |
| AI HAT+ | Standoffs match actual height; no bent header or loaded PCB |
| AI HAT+ 2 | Heatsink and its push pins clear; fuse remains accessible |
| PCIe ribbon | Correct reach and routing without tension or excessive folds |
| Side wing | Supported independently; power lead forces do not load the Pi header |
| Case | Bench use is assumed; no compatibility with an existing case is claimed |

Create a nonconductive 1:1 mock-up and check these items before PCB ordering. Manufacturer drawings are starting references; the Pi mechanical drawing explicitly warns against using approximate dimensions as production data.

Samtec's family drawing (rev. BH) gives, for the SSQ-120-03-G-D, a 10.01 mm tail below the insulator, an 8.51 mm high and 4.95 mm wide insulator and a 51.31 mm length (20 positions), with up to 2 degrees of tail sway and a row spacing at the tails of 2.54 mm +0.25/-0.31 mm for lead style -03. Seated on a 1.6 mm board, the tails protrude about 8.4 mm. The drawing does not give the PCB hole size or the mating depth; both still need confirming with the Samtec layout recommendation and a test-fit.

Sources: [Pi 5 mechanical drawing](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf), [AI HAT mounting instructions](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html), [Samtec connector](https://www.samtec.com/products/ssq-120-03-g-d).
