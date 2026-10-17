# Carrier soldering guide (revision 1)

Tools as for the interposer (about 330 °C). **Do not plug in the Pico's USB until the release checklist is complete and you have decided to energize it.**

## Before you start

- Solder the header strip supplied with the Adafruit 4682 microSD module onto the module (pins on the side opposite the card slot components, as in Adafruit's guide).
- The Pico 2 WH and MikroE module arrive with headers; nothing to solder on them.

## Assembly order

| Step | Part | Where | Check while fitting |
|---|---|---|---|
| 1 | R1 470 Ω, R2/R3 100 kΩ, R4/R5 10 kΩ — standing | Strip between the MikroE and Pico sockets, labels R1–R5 | Body over the round silkscreen circle, other lead bent back. 10 kΩ = brown-black-black-red |
| 2 | R6–R10 1.8 kΩ — standing | Right edge, next to the LEDs | brown-grey-black-brown |
| 3 | LED1–LED5 (TLLR4401) | Right edge | **Cathode (short lead, flat side) in the square pad, toward the board edge** |
| 4 | C1, C2 — 100 nF | C1 top edge (front); **C2 on the BACK** beside U1, soldered on the front | Not polarized |
| 5 | U1 — DIP-14 socket | **BACK side**, below the microSD position: insert from the back, solder on the front | Notch toward the top edge; pin 1 is the square pad, top-left when viewed from the back. Do not insert the IC yet |
| 6 | J7 (4-pin) and J8 (5-pin JST) | Left edge | Square pad = pin 1, at the bottom of each connector |
| 7 | J5 — 9-pin socket | **BACK side**: insert from the back, solder on the front | Pin 1 = square pad at the right end of the row (x ≈ 31 mm). Do this before J3/J4, because the MikroE module later covers these joints |
| 8 | J3, J4 — 8-pin sockets; J1, J2 — 20-pin sockets | Front | Solder two end pins, check they stand straight, then the rest. A spare module plugged in while soldering keeps them aligned |
| 9 | Insert SN74LV125AN into U1 (back side) after the continuity checks below | — | Notch to the top edge, matching the socket |
| 10 | Wires J6 → MikroE terminals | Top edge | J6 "IN+" to IN1+, "IN−" to IN1−, "VBUS" to IN2 VBUS. Read the terminal labels on the delivered module first |

Plug the modules in last: microSD module on the back (card slot toward the top edge), MikroE on J3/J4, Pico on J1/J2 (USB connector toward the top edge, pin 1 at the J1 square pad). Support the board under the sockets when pressing modules in.

## Continuity checks before first power (all modules and the U1 chip removed)

| From | To | Expected |
|---|---|---|
| J2 pin 16 (Pico pin 36, 3V3) | J3 pin 7, J5 pin 1, U1 pin 14, U1 pin 13 | ≈ 0 Ω |
| 3V3 (as above) | ground (J1 pin 3) | open |
| J1 pins 3, 8, 13, 18; J2 pins 3, 8, 18 (J2 pin 13 is Pico AGND, left open) | each other, J3 pin 8, J4 pin 1, J5 pin 2, U1 pin 7 | ≈ 0 Ω |
| J2 pin 19 and pin 20 (Pico VSYS, VBUS) | anything | open |
| J7 pin 1 / 2 / 3 | J6 pad 1 / 2 / 3 | ≈ 0 Ω; J7 pin 1 to pin 2 open (100 nF) |
| J7 pin 4, J8 pin 1 | ground | ≈ 0 Ω |
| J8 pin 2 | U1 pin 2; to ground | ≈ 0 Ω; ≈ 100 kΩ |
| J8 pin 4 | U1 pin 5 | ≈ 0 Ω |
| J8 pin 3 | U1 pin 8 | ≈ 470 Ω |
| J2 pin 14, 12, 11, 9, 7 (Pico pins 34, 32, 31, 29, 27) | LED1…LED5 anode | ≈ 1.8 kΩ each |
