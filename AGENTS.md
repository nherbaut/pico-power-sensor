# Working instructions: hand-solderable measurement boards

Copy this file to the root of a new repository as `AGENTS.md`.

## Purpose

Design and document two printed circuit boards that the owner will solder by hand:

1. **An interposer** that sits between a bench supply and a single-board computer's 40-pin GPIO header. It carries the protection and the current-sense element for the device under test (DUT).
2. **A microcontroller carrier** that measures the interposer's sense signal, logs it and supports a few user-programmable indicators.

The boards are prototypes for a bench energy-measurement instrument. They are not products.

## Hand-soldering rules (hard constraints)

- The owner has a normal temperature-controlled soldering iron and **no hot air, no microscope and no reflow equipment**.
- Use through-hole parts wherever a through-hole version exists. Allowed through-hole families: axial or radial resistors and capacitors, 3 mm or 5 mm LEDs, DIP and TO-92/TO-220/TO-247 packages, 2.54 mm headers and sockets, screw terminals, JST-XH.
- No part smaller than a 1206 chip, and no leaded SMD with a pitch finer than 1.27 mm.
- Where only a fine-pitch SMD chip exists (for example a precision power-monitor IC), use a **pre-assembled breakout or evaluation module** on header pins, or a plug-in adapter board. Do not place the bare chip on the board. State which module, its source and its pinout, and what is on the module that the board must not duplicate.
- Where a part has no practical through-hole version and no module exists, stop and report. Do not substitute an SMD part silently.
- Place through-hole footprints with at least 1 mm of clearance for the soldering tip and tolerate a 0.8 to 1.0 mm drill for each lead. Use pads of at least 1.8 mm diameter. Mark pin 1 and polarity on the silkscreen.
- Prefer sockets for ICs and modules so that a wrong or dead part can be replaced.

## Measurement and power boundaries

- **Preserve the distinction between instrument, DUT and measurement boundary.** The instrument's own supply, indicator LEDs, pull-ups to an external supply, protection bias currents and any other auxiliary load must come from the instrument side. They must not be included in the current the instrument reports as DUT current.
- Put power protection and everything that draws instrument current **upstream** of the sense element.
- Use a four-wire (Kelvin) connection to the sense element. Keep the sense pair short, tightly coupled and away from switching or high-current copper.
- The bench supply is a 5.1 V, current-limited laboratory supply. The DUT is a single-board computer powered through its GPIO header. Do not buy another supply or substitute a voltage-converter HAT.
- Keep **all 40 header pins** available. Check physical clearance for an active cooler and for HATs mounted on top of the header before calling a layout complete.
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
