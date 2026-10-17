# Bench test list (revision 1)

Status: **plan only — nothing here has been performed.** Energizing hardware requires the completed release checklist (`hardware/release-checklist.csv`) and the owner's explicit decision. Record every reading with date, instrument and conditions; a reading is a measurement, a value in this file is an expectation.

## A. Interposer alone (no Pi, no carrier, no HAT)

1. Do all continuity checks in `docs/soldering-interposer.md`.
2. Set the Korad U202 to 5.1 V and its current limit to about 0.1 A, output off. Connect J1 (+ to +), then switch on.
3. Measure J2 pin 2 and pin 4 to pin 6: expect close to 5.1 V (no load). Supply current should be close to zero (no load is connected; Q1's gate draws no steady current).
4. Measure across J5 pin 1 and pin 2: expect about 0 mV (no load).
5. Measure J5 pin 3 to pin 4: expect about the J2 pin 2 voltage.
6. Switch off. Reverse the bench leads at J1, limit 0.1 A, switch on briefly: J2 pin 2 must stay at about 0 V and the supply current near zero (Q1 off). Note: Q1 does not block current flowing back from the Pi side. Switch off and restore polarity.
7. With a known dummy load on J2 pins 2/4 to ground (not the Pi), raise the load in steps toward the 5 A design target, current limit set just above each step. At each step record: supply voltage, J2 pin 2 voltage, voltage across R1 (J5 pins 1–2), and temperature of F1, R1 and Q1 after it settles. Compare the drop with the calculated values in `docs/interposer-layout.md`; stop if anything exceeds its rating or gets hot to the touch.

## B. Carrier alone (Pico on its own USB charger, interposer not connected)

1. Do all continuity checks in `docs/soldering-carrier.md`; then insert U1.
2. Plug in the Pico only (no MikroE, no microSD). Power from the USB charger. Measure 3.3 V at U1 pin 14 to pin 7.
3. Load a test firmware that blinks LED1–LED5 one after another; check each lights.
4. With the buffer enable (GP3) held high, check U1 pins 3, 6 and 8 float or follow the documented idle state; then drive GP3 low and loop GP0 → J8 pin 3 through a 1 kΩ test wire to J8 pin 2 → GP1 to check the UART path.
5. Power off; insert the MikroE module. Power on; scan I2C: expect the INA228 at 0x4A, manufacturer ID 0x5449 at register 0x3E.
6. Power off; insert the microSD module and a card. Power on; write and read back a test file.

## C. Both boards, still without the Pi

1. Connect the sense and UART cables between J5/J6 (interposer) and J7/J8 (carrier), pin 1 to pin 1.
2. Bench supply on with a dummy load: compare the INA228 bus voltage with a multimeter at J2 pin 4, and the current with a reference meter in series with the load, at several currents. This is the start of the installed-channel calibration described in `docs/msr1-qualification.md`.
3. Check both power-state cases: Pico on / bench off, and bench on / Pico off — no LED or supply should be back-powered; measure J8 pin 3 and J6 pin 3 in each case.

## D. First connection to the Pi

Only after A–C pass and the release checklist is complete: Pi with no HAT, Wi-Fi only, bench limit 5 A, monitor current during boot.
