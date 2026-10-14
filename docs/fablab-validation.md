# Fablab validation worksheet

The user has confirmed access to the requested equipment. This is a future test procedure, not a record of passed tests or authorization to energize hardware. Complete design/fabrication checks first; assembled-board tests precede Pi connection. Record board revision, design hash, instrument identities, calibration status, wiring, ambient temperature and operator/date with every result.

## Rigid unpowered fit

No further paper-only photographs are required. Transfer the existing outline to a rigid insulating 1.6 mm mock-up and use actual selected sockets, M2.5 hardware and component-height blocks. Verify both interposer holes, header engagement and pin 1, cooler inlet and connector access, then each AI HAT and PCIe ribbon separately. Support the outward wing so cable forces do not load the Pi header. Record spacer heights, available pin engagement and interference dimensions, with photographs. All hardware must be unpowered.

For the carrier, check Pico socket seating/USB access/antenna clearance, J_SENSE and J_UART cable access, and full microSD hinge/card travel. Verify the J3-to-J_SENSE cable by continuity, not cable color, before connecting the sense pair to the interposer. Read the INA229 device ID over SPI as the first electrical check of the assembled carrier.

## Equipment and wiring

Bring the Korad U202. Use the fablab's electronic load (5 A at 4.5–5.1 V continuously), scope, meters and temperature equipment. The load substitutes for the Pi. Its auxiliary electronics must be separately powered when applicable. Connect both Pi 5 V contacts and sufficient return contacts through a fixture representing the real mating header; attaching the load upstream would omit the header drop.

Review earth/reference connections with the lab operator. Ordinary scope ground clips share ground; attach them only to the common circuit GND. Use differential probes or two ground-referenced channels with math for gate-to-source and other floating differential voltages. Never float the scope protective earth. Keep probe loops short. A current probe is preferred for inrush; any temporary sense resistor changes the path and must be recorded and removed from the final drop result.

## Test sequence and evidence

| Stage | Method | Required record / acceptance |
|---|---|---|
| Unpowered assembly | Inspect solder/polarity; check all 40 pins, fuse path, Kelvin paths and isolated rails | Continuity matrix; no shorts or shunt bypass; no load or Pi connected |
| Carrier alone | Independent USB power with current limit; then fit the Pico after rail checks | Pico/INA229/SD voltages, ripple, temperature; verify no unintended DUT supply path |
| Interposer initial power | Low current limit, no Pi; scope Korad input and protected output at 5.10 V | Startup captures; investigate unexpected output or oscillation before increasing load |
| Slow UV/OV sweep | Small dummy load; sweep through calculated thresholds with scope and meter | Trip/recovery values and hysteresis; compare to calculation including equipment uncertainty; no Pi attached |
| Fault recovery | After each fault disable output, investigate, allow rails to discharge, verify input/output near 0 V, restore 5.10 V and restart deliberately | Whether automatic reconnection occurs before operator action; successful power-cycle recovery; invalidated trial record; FAULT currently NC |
| Startup/inrush | Start with known fixture capacitance, then reviewed larger values; capture VIN, VOUT, VGS and current | Peak/duration/load capacitance; compare MOSFET VDS–ID trajectory to derated SOA; no inferred pass from capacitor energy alone |
| Steady load | 0.5, 1, 3 and 5 A after thermal stabilization; pause on abnormal heating or regulation | J1-to-header positive **plus return** drop recorded (header at least 4.8 V at 5 A with the Korad at 5.10 V), contact rise <30 °C, all component limits respected; external harness drop reported separately |
| Power domains | Pico first, DUT fixture first, reset, brownout, removal | UART/marker levels, off-side leakage and Pi-side buffer overhead; no off-side rail held up |
| SD exercise | Actual selected card, Wi-Fi + all LEDs + repeated writes/reads; abrupt USB removal/reset | Peak/average current, SD/Pico rail decay and GPIO injection, write integrity, voltage droop and LDO temperature; firmware/fixture still required |
| Metrology | Known loads and independent references | Actual shunt value, current/power/energy comparison and uncertainty; the INA229 is not its own calibration reference |

The full ±30 V fault range is **not** an executable test instruction yet. Freeze the fault/transient limits and protective fixture after circuit/SOA review. Likewise, transient acceptance needs an agreed DUT voltage envelope; an OV comparator threshold alone is not a Pi absolute maximum. Leave those rows open until limits are established.

Use a contact thermocouple on shiny metal where IR readings are unreliable. Record stabilization criteria and time traces rather than a single immediate temperature. Do not change the supply setpoint upward to compensate for a failed drop target.

On any failure, stop, record it and revise the design as needed; do not mark the connection gate passed. Only a completed release checklist supports subsequent Pi connection. Firmware, logging and unattended fault capture are separate implementation work.
