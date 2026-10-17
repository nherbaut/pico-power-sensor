# Working instructions: hand-solderable measurement boards

Copy this file to the root of a new repository as `AGENTS.md`.

## Purpose

Design and document two printed circuit boards that the owner will solder by hand:

1. **An interposer** that sits between a bench supply and a single-board computer's 40-pin GPIO header. It carries the protection and the current-sense element for the device under test (DUT).
2. **A microcontroller carrier** that measures the interposer's sense signal, logs it and supports a few user-programmable indicators.

The boards are prototypes for a bench energy-measurement instrument. They are not products.

## System requirements (starting values, confirm with the owner)

| Item | Value |
|---|---|
| Bench supply | Existing Korad U202, planned 5.1 V setting and owner-confirmed 5 A current-limit setting. These are operating settings, not measured bounds; current-limit tolerance, startup/transient behavior and output-shutdown mode remain unverified. |
| DUT | Raspberry Pi 5, powered through its 40-pin GPIO header (5 V pins); proposed peak-current design target 5 A, to be confirmed |
| Voltage at the DUT header | Provisional target: at most 100 mV below the supply setting at the proposed 5 A peak current. This is not a fixed acceptance limit. Set the final voltage-drop budget after evaluating hand-solderable components and the Pi's supply-voltage requirements. Include the fuse, reverse-polarity protection, sense element, copper and connectors; label datasheet-based estimates as calculations. |
| Sense element | Owner-approved prototype choice: Bourns MSR1-0R005F1, 5 mΩ, 1%, through-hole, with separate four-wire pickups at its pads and calibration of the installed current channel (calculated nominal drop: 25 mV at 5 A). Qualification remains incomplete: lead/thermal effects, exact lifecycle, footprint, populated fit and calibrated system accuracy require evidence. See `docs/msr1-qualification.md` and the provisional BOM. |
| Sense-cable conditioning | Owner-approved prototype choice (2026-10-16): three Vishay PR01000108209JR500 82 Ω, 5%, 1 W through-hole resistors, one at each positive observation source before the exposed cable, and one KEMET C315C104K5R5TA 100 nF radial differential capacitor on the carrier. They are not in the main DUT power path. Lifecycle, footprint, fault/thermal and installed measurement qualification remain partial; see `docs/sense-interface-options.md`. |
| External measurement connections | Owner confirmed separate USB charger for the Pico, Wi-Fi-only Pi, and occasional AI HAT. Retain shared-ground architecture; header-powered HAT consumption is included in DUT measurement. Actual charger grounding, bench earth relationship and exact HAT power/clearance remain unverified; see `docs/ground-reference-review.md`. |
| Measurement | Voltage, current, power and energy of the DUT. The owner chose to qualify the MikroE Power Monitor Click MIKROE-4810 (20-bit INA228, I2C) first, replacing the initial SPI preference. The module remains under qualification, not finally selected. |
| Instrument controller | A Raspberry Pi Pico 2 W, powered by its own USB, never from the DUT supply |
| Programmable indicators | Owner-approved prototype set (2026-10-16): five Vishay TLLR4401 red through-hole LEDs and five Vishay MRS25000C1801FCT00 1.8 kΩ axial resistors, driven independently by Pico GP28, GP27, GP26, GP22, GP21 (LED1–LED5; owner request 2026-10-17, formerly GP7–GP11) from instrument USB power. Keep the existing 10 mA indicator allocation; lifecycle, actual visibility and footprint/rail qualification remain partial. See `docs/indicator-options.md`. |
| Carrier functions | Power monitor module, owner-approved Adafruit 4682 microSD module in SPI mode, five programmable LEDs, one UART/marker connector to the interposer. Card type and power budget remain under qualification. |
| UART/marker interface | Owner-approved prototype circuit: one TI SN74LV125AN in a through-hole DIP socket, instrument USB-derived 3.3 V, three channels for bidirectional UART and Pi-to-Pico marker. Omit the earlier return MOSFET and Pi-RX positive pull-up. Supporting-part codes, GPIO assignment, logic margins and mixed-power/startup qualification remain open; see `docs/uart-interface-qualification.md`. |
| Protection | Owner-approved prototype choices: Littelfuse 021706.3MXP 6.3 A cartridge fuse, Schurter 0031.8201.G through-hole holder and Pololu 5383 assembled reverse-polarity / reverse-current-blocking module, all upstream of the shunt. Qualification remains partial: sustained current-limited fault survival, thermal behavior, connections, lifecycle gaps and complete voltage drop remain unresolved. See `docs/protection-options.md` and the provisional BOM. |
| Power connections | Owner-approved prototype choices: one Würth Elektronik 691137710002 bench-entry terminal, two Samtec TSW-102-07-G-S headers on the Pololu module and two SSQ-102-01-G-S sockets on the interposer. See the scoped hole exceptions below and `docs/power-connector-options.md`. Actual fit, installed loss, thermal behavior, lifecycle and cooler/HAT clearance remain unverified. |
| Pi and inter-board connections | Owner-approved prototype choices: one Adafruit 2223 Pi stacking socket, requiring the current square-pin version; two JST B4B-XH-A sense headers, two B5B-XH-A UART/marker headers, two XHP-4 and two XHP-5 cable housings, and eight ASXHSXH22K152 pre-crimped leads. Use about 10–12 cm board separation for the nominal 15 cm leads; usable twisted reach remains unverified and they cannot span a 20 cm gap. Leave the fifth UART cable cavity empty. See `docs/pi-harness-connector-options.md`; actual revision, 5 A current sharing, thermal behavior, fit, lifecycle and interface protection remain open. |

If a value cannot be met with hand-solderable parts, report the gap and the options. Do not change a requirement silently.

## Start here (first session)

Do these steps in order. After each one, stop, summarise and ask for approval before the next.

1. **Read the repository.** If it is empty, say so. List which of the files named in "Deliverables" exist.
2. **Ask the owner the open questions below.** Do not assume answers.
3. **Write `docs/requirements.md`** with the table above, the owner's answers and the list of open items.
4. **Write `docs/architecture.md`**: a block diagram that separates the instrument, the DUT and the measurement boundary, and says which current flows through which part.
5. **Select modules and parts**, one function at a time, as options with a recommendation. The owner chooses. Record each choice in the BOM.
6. **Interposer schematic**, then review. 7. **Carrier schematic**, then review. 8. **PCB layouts**, then ERC, DRC and parity. 9. **Footprint and module review.** 10. **Soldering guide and bench test list.**

Do not start a later step before the owner approves the earlier one.

### Open questions to ask first

- Which precision power-monitor module will be used (module name, supplier, interface, whether it has its own shunt that must be bypassed or removed)?
- Which microSD module (bare socket on pins, or module with regulator and level shifter)?
- How is the 3.3 V for the card produced: a through-hole regulator, the module's regulator or the Pico's 3.3 V rail?
- How does the interposer switch or protect the supply with through-hole parts? Is the fuse alone acceptable, or is reverse-polarity protection needed and what current does it have to carry?
- What shunt: a through-hole power resistor, a four-terminal shunt or a module? What value and tolerance?
- Which connectors join the two boards, and which cable length is acceptable?
- Is there an enclosure, an active cooler or a HAT on the Pi that limits the interposer's height?
- Should the first board be a single prototype, and where should the fuse and DUT connector sit for easy access?

## Hand-soldering rules (hard constraints)

- The owner has a normal temperature-controlled soldering iron and **no hot air, no microscope and no reflow equipment**.
- Use through-hole parts wherever a through-hole version exists. Allowed through-hole families: axial or radial resistors and capacitors, 3 mm or 5 mm LEDs, DIP and TO-92/TO-220/TO-247 packages, 2.54 mm headers and sockets, screw terminals, JST-XH.
- No part smaller than a 1206 chip, and no leaded SMD with a pitch finer than 1.27 mm.
- Where only a fine-pitch SMD chip exists (for example a precision power-monitor IC), use a **pre-assembled breakout or evaluation module** on header pins, or a plug-in adapter board. Do not place the bare chip on the board. State which module, its source and its pinout, and what is on the module that the board must not duplicate.
- Where a part has no practical through-hole version and no module exists, stop and report. Do not substitute an SMD part silently.
- Place through-hole footprints with at least 1 mm of clearance for the soldering tip and tolerate a 0.8 to 1.0 mm drill for each lead. Use pads of at least 1.8 mm diameter. Mark pin 1 and polarity on the silkscreen.
- Owner-approved exception (2026-10-15): the two leads of the Bourns MSR1-0R005F1 shunt may use **1.30 mm finished plated holes and 3.00 mm pads** to accommodate the datasheet's 1.05 mm maximum lead diameter. This applies only to that shunt; other lead-hole rules and solder-tip clearance remain unchanged. Verify the eventual fabricator's finished-hole tolerance and the actual footprint before release. See `docs/msr1-qualification.md`.
- Owner-approved exception (2026-10-16): the two electrical leads of the Schurter 0031.8201.G fuse holder may use **1.35 mm nominal finished plated holes, tolerance ±0.05 mm, and 3.00 mm pads**, at 22.5 mm pitch. This applies only to that holder and does not authorize an extra central fastening hole. Verify the eventual fabricator's finished-hole tolerance, correct the library courtyard to contain the manufacturer's installation envelope, and review the actual footprint before release. See `docs/protection-options.md`.
- Owner-approved exception (2026-10-16): the two electrical leads of the Würth Elektronik 691137710002 terminal may use **1.35 mm nominal finished plated holes, tolerance ±0.05 mm, and 3.00 mm pads**, at 5.00 mm pitch. This applies only to that terminal. Verify maximum lead dimensions, actual insertion, the fabricator's finished-hole tolerance and the footprint before release. See `docs/power-connector-options.md`.
- Owner-approved exception (2026-10-16): the four electrical leads of the two Samtec SSQ-102-01-G-S sockets on the interposer may use **1.10 mm nominal finished plated holes, tolerance ±0.05 mm, and 2.00 mm pads**, at 2.54 mm pitch within each socket. This applies only to those sockets. Verify maximum lead dimensions, insertion, fabrication tolerance and the footprint before release. The mating TSW-102-07-G-S headers use the existing Pololu module slots; do not drill or enlarge the module. See `docs/power-connector-options.md`.
- Owner-approved exception (2026-10-16): all 40 electrical leads of the **Adafruit 2223 square-pin Pi stacking socket only** may use **1.10 mm nominal finished plated holes, tolerance ±0.05 mm, and 2.00 mm pads**. This approves changing the inherited 1.00 mm header holes while preserving all 40 pad centres, the outline and mounting holes. It does not cover the unselected Samtec 40-pin alternative or carrier sockets. Confirm the actual square-pin revision, resolve the 10 mm retail / 11 mm drawing tail-length discrepancy, and verify insertion, fabrication tolerance, mating depth and populated cooler/HAT clearance before release. See `docs/pi-harness-connector-options.md`.
- Prefer sockets for ICs and modules so that a wrong or dead part can be replaced.

## Measurement and power boundaries

- **Preserve the distinction between instrument, DUT and measurement boundary.** The instrument's own supply, indicator LEDs, pull-ups to an external supply, protection bias currents and any other auxiliary load must come from the instrument side. They must not be included in the current the instrument reports as DUT current, except for the scoped UART-bias exception below.
- Put power protection and everything that draws instrument current **upstream** of the sense element, except for the scoped UART-bias network below.
- Owner-approved measurement-boundary exception (2026-10-16): the proposed UART interface may include **one 10 kΩ pull-up from Pi UART RX to Pi 3.3 V and two 100 kΩ pull-downs on the Pi UART TX and task-marker inputs** in reported DUT consumption. Keep the buffer supply and MOSFET gate-drive network instrument-powered. The calculated nominal resistor-network allowance is **1.3068 mW on the 3.3 V side** with the return low and both Pi outputs high, before leakage, switching, internal pulls and Pi conversion losses; it is not a measured or complete worst-case bound. Report the DUT boundary as including this communication load and do not subtract a fixed nominal value. This exception does not authorize Pi-powered buffer ICs, other auxiliary loads, exact device selection or hardware energizing. See `docs/uart-interface-options.md`.
- Use a four-wire (Kelvin) connection to the sense element. Keep the sense pair short, tightly coupled and away from switching or high-current copper.
- The bench supply is a 5.1 V, current-limited laboratory supply. The DUT is a single-board computer powered through its GPIO header. Do not buy another supply or substitute a voltage-converter HAT.
- Keep **all 40 header pins** available. Check physical clearance for an active cooler and for HATs mounted on top of the header before calling a layout complete.
- Reuse the earlier `picopower` PCB outlines, mounting-hole positions and Pi/Pico header geometry as the mechanical baseline. The owner reports having checked the earlier hole and pin fit. See `docs/mechanical-baseline.md` for the source geometry and evidence scope. Preserve that geometry when changing the electronics; report any required outline, hole or header change before implementing it. Recheck clearance where new parts or changes affect fit, rather than restarting unchanged mounting geometry from scratch.
- Keep a cartridge or through-hole fuse as the protection element in the first prototype. Do not add electronic protection that cannot be hand-soldered.

## Evidence discipline

- Never describe design calculations, simulations or automated checks as physical measurements.
- Track ERC, DRC, footprint review, parts review and bench validation as separate items. A pass in one does not imply a pass in another.
- Fabrication and connection to the single-board computer require a completed release checklist. Never suppress or exclude a violation to make a release pass.
- Record every voltage-drop, current-limit and thermal figure with its basis: datasheet value, calculation or measurement. State the conditions.
- Record which parts are through-hole, which are modules and which are unresolved. Keep a table of module source, version and pinout.

## Authorizations

No repository creation on a remote host, publishing, ordering, payment, uploading to a manufacturing service or energizing of hardware is authorized unless the owner says so in that conversation. Local commits are allowed when the owner asks for them.

## Tooling and conventions

- Use KiCad 9. Keep generated and routed files consistent: when a generator no longer reproduces a hand-edited routed board, say so in the documentation and treat the board file as the source of truth.
- Run native ERC and DRC and a schematic-to-board parity check. Save the reports as evidence.
- English documentation and code identifiers. Keep a CSV bill of materials with one row per distinct part, one row per module and a "hand-solder / module / not fitted" column.
- Keep a CSV release checklist with the checks above, the reviewer, the date and a hash of the design files so a change invalidates stale evidence.
- When a library footprint is used, compare it with the manufacturer's drawing (pad size, drill, pitch, outline) and record the result. Do the same for a module's header spacing and pin order.

## Deliverables for each board

1. Schematic with conventional symbols and net names.
2. PCB with through-hole footprints only (plus the headers for any module).
3. BOM with manufacturer part numbers and source for every line.
4. A one-page soldering guide: order of assembly, which parts to fit first, polarity checks and a continuity test list before first power-up.
5. A bench test list that checks supply, ground and the sense pair with a multimeter before the single-board computer is connected.
