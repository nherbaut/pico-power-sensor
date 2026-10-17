# Interposer soldering guide (revision 1)

Tools: temperature-controlled iron (about 330 °C; up to 370 °C for the ground pins of J2, the shunt and the fuse holder), 0.7–1 mm leaded or lead-free solder, flush cutters, multimeter. No hot air needed. **Do not power the board until the release checklist is complete and you have decided to energize it.**

## Before you start

- Check the bare board for shorts: J1 "+" to J1 "−" must read open.
- **Q1 (Vishay Si4143DY-T1-GE3) is an SO-8 chip with 1.27 mm pin pitch.** Use a fine chisel tip, flux and solder braid. Tin one corner pad, place the chip with its pin-1 dot at the top-left pad of the Q1 outline (the small triangle on the silkscreen marks that corner), tack that pin, check that all eight pins sit on their pads, then solder the other pins one by one; clear any bridge with braid and flux. Pins 1-3 (left column, top to bottom) are source, pin 4 (bottom left) is the gate, pins 5-8 (right column) are drain. Do this early, with nothing tall nearby.

## Assembly order (lowest parts first)

| Step | Part | Where | Check while fitting |
|---|---|---|---|
| 1 | R2, R3, R4 — 82 Ω 1 W (PR01) | Centre, three horizontal rows | Not polarized. Keep bodies about 1 mm above the board |
| 2 | R5, R6 — 470 Ω; R7 — 100 kΩ (MRS25) | Above the Pi header | Not polarized. Read the colour bands: 470 Ω = yellow-violet-black-black, 100 kΩ = brown-black-black-orange |
| 3 | R1 — shunt MSR1 5 mΩ | Left column, standing | Not polarized. Push fully down; form the leads only as needed for the 11.4 mm holes. Do not resolder it after calibration |
| 4 | J5 (4-pin JST) and J6 (5-pin JST) | Right of centre | Latch/key orientation as printed on the silkscreen outline |
| 5 | Q1 — Si4143DY SO-8; R8 — 10 kΩ standing, below Q1 | Right side, under J1 | Q1: pin-1 dot at the top-left pad (triangle marker on the silkscreen); see the note above. R8: brown-black-black-red |
| 6 | F1 — fuse holder | Top centre | Seat flat; heat each large pad well |
| 7 | J1 — bench terminal | Top right, wire entry facing the right edge | "+" = square pad |
| 8 | J2 — Adafruit 2223 stacking socket | **Body on the BOTTOM side**, long pins pointing up through the board; solder on the top side | Pin 1 = left end of the row nearest the bottom board edge (next to H1), at the "PI 40-PIN" label side. Solder 2 corner pins, check it is square, then the rest. Do not trim the long pins: they carry the HAT. The eight ground pins have no thermal relief and need more heat |
| 9 | Insert the 6.3 A F 5×20 fuse in F1 | — | — |

Clip resistor and connector tails on the bottom side to about 1 mm (except J2): the bottom faces the Pi and its cooler.

## Continuity checks before first power (module and fuse fitted, no Pi)

| From | To | Expected |
|---|---|---|
| J1 + | Q1 pins 5-8 (right-hand column, drain) | ≈ 0 Ω |
| Q1 pins 1-3 (left-hand column, source) | F1 right-hand clip | ≈ 0 Ω |
| Q1 pin 4 (gate) | ground | ≈ 10 kΩ |
| J1 + | J1 − | open (no short) |
| F1 left-hand clip | R1 upper pad | ≈ 0 Ω |
| R1 lower pad | J2 pins 2 and 4 | ≈ 0 Ω |
| J1 − | J2 pins 6, 9, 14, 20, 25, 30, 34, 39 | ≈ 0 Ω each |
| J2 pin 2 | any ground pin; J2 pin 1 or 17 | open |
| J5 pin 1 / pin 2 | R1 upper / lower pad | ≈ 82 Ω each |
| J5 pin 3 | J2 pin 4 | ≈ 82 Ω |
| J5 pin 4, J6 pin 1 | ground | ≈ 0 Ω |
| J6 pin 2 / pin 4 | J2 pin 8 / pin 16 | ≈ 470 Ω |
| J6 pin 3 | J2 pin 10 | ≈ 0 Ω; to ground ≈ 100 kΩ |
| J6 pin 5 | anything | open |
| Every other J2 pin | anything on the board | open |
