# Picopower-proto handoff for dumb-claude

**Snapshot date:** 2026-10-16  
**Purpose:** Continue the project from this repository state without re-asking settled questions or mistaking documentary work for a finished electrical design. The owner refers to Claude as “dumb-claude.”

## Start here

Read [AGENTS.md](AGENTS.md) first; it is the project’s controlling design and assembly instructions. Then read [requirements](docs/requirements.md), [architecture](docs/architecture.md), this handoff, and the particular qualification documents relevant to the next function. Keep approval history: “ok” approves only the choices explicitly described alongside that answer.

The work is still at **step 5, parts and module selection**, before either custom schematic. The owner has approved many prototype part choices, plus a proposed carrier GPIO allocation. Several supporting components and both carrier sockets remain undecided. Do not jump to schematic capture merely because the design is taking shape. Continue the owner-led, one-function-at-a-time process in AGENTS.md and present the next concrete choice when it is ready.

The owner wants the existing `picopower` board dimensions, mounting-hole locations and Pi/Pico header geometry reused. Physical fit for those inherited mechanical features was checked by the owner in the earlier project. Do not restart that geometry review; check new component, stack, HAT, cooler and solder-access clearances as they arise. Geometry and its evidence scope are in [mechanical baseline](docs/mechanical-baseline.md).

## Project and boundaries

This is one hand-soldered bench energy-measurement prototype comprising an interposer and an independently powered carrier. The interposer feeds a Raspberry Pi 5 from the owner’s existing Korad U202 at a planned 5.1 V setting and owner-confirmed 5 A current-limit setting. The settings are not measured maxima; supply tolerance, transients and shutdown behavior remain unknown. Five amps is a provisional peak design target and fault-review point.

The carrier contains a USB-powered Raspberry Pi Pico 2 W, a power-monitor module, microSD logging, five programmable LEDs and a UART/task-marker interface. Owner’s declared measurement configuration is a **separate USB charger for the Pico, Wi-Fi on the Pi, and occasional AI HAT**. Header-powered HAT load is part of the DUT reading. The charger’s output grounding, bench earth relationship and exact HAT power/clearance still need qualification. HDMI, wired Ethernet and Pi USB peripheral paths are not part of the declared measurement setup; temporary connections can change the grounding analysis.

The intended Pi load current path is bench positive → fuse → reverse-protection module → shunt → Pi 5 V header contacts → Pi ground header contacts → direct interposer return → bench negative. The monitor, Pico, storage, LEDs and buffer run from the instrument USB-derived supply. Separate Kelvin pickups observe the shunt; the measurement and UART cables are not the intended DUT ground return. The owner-approved UART bias exception includes its specified Pi-side resistor loading in the reported DUT consumption. No other Pi-powered auxiliary load is excepted.

The voltage-drop goal (formerly 100 mV at 5 A) was explicitly relaxed by the owner. It is not a fixed acceptance limit. Complete supply-path calculations and Pi voltage requirements are still needed. The energy-accuracy goal is approximately 1%, also not demonstrated. Calculations, automated checks and simulated models must never be called physical measurements.

## Decisions already approved

Selections below are **provisional prototype choices**, not purchase, fabrication or release approvals. Detailed part numbers, evidence and remaining gaps are in [the BOM](hardware/bom.csv) and linked reports.

| Function | Owner-approved direction |
|---|---|
| Shunt | Bourns MSR1-0R005F1, 5 mΩ, 1%, through-hole, four-wire pickup at its pads; calibrate the installed channel |
| Power monitor | Qualify MikroE Power Monitor Click MIKROE-4810 (INA228 over I²C) first. It is not finally selected; supplied revision, headers, fit, power states and energy accuracy remain open |
| Storage module | Adafruit 4682 in SPI mode. It is a 3.3 V assembled breakout without a regulator or level shifter. A Pico-3V3 power direction is proposed under a conditional 235 mA carrier allocation; actual card demand and regulator margin are unknown |
| UART/marker topology | One USB-powered TI SN74LV125AN in a through-hole DIP socket; three channels; omit the earlier MOSFET return and Pi-RX positive pull-up. Buffer and pull-up power are instrument-side |
| UART series-value direction | 470 Ω nominal on all three source-side signal resistors accepted. The value has conditional edge/fault calculations; exact supporting parts and complete interface qualification are open |
| Sense lead conditioning | Three Vishay PR01000108209JR500 82 Ω, 5%, 1 W resistors (one in each positive observation lead before the exposed cable) plus one KEMET C315C104K5R5TA 100 nF differential filter capacitor on the carrier |
| Indicators | Five Vishay TLLR4401 red through-hole LEDs and five Vishay MRS25000C1801FCT00 1.8 kΩ axial resistors, independently driven from Pico GP7–GP11 |
| Interposer power protection | Littelfuse 021706.3MXP 6.3 A cartridge fuse, Schurter 0031.8201.G holder and Pololu 5383 reverse-polarity/reverse-current-blocking module, upstream of the shunt |
| Bench/module connectors | Würth Elektronik 691137710002 bench terminal; two Samtec TSW-102-07-G-S headers fitted to the Pololu module and two SSQ-102-01-G-S sockets on the interposer |
| Pi and harness connectors | Adafruit 2223 square-pin Pi stacking socket (current square-pin version required); JST-XH sense/UART headers and housings; eight JST ASXHSXH22K152 pre-crimped leads. Start with about 10–12 cm board spacing, not a 20 cm cable gap |

Scoped fabrication-hole exceptions are written in AGENTS.md. They apply only to the named part. The carrier sockets have **no hole-size exception**. All custom board parts should be through-hole wherever available; no hot air, microscope or reflow is available.

## Current carrier GPIO plan

The proposed allocation uses 17 of Pico 2 W’s 26 exposed GPIO pins, leaving nine spare. It avoids GP23–GP25 and GP29, which serve internal Pico wireless/board functions.

| Pico GPIO | Physical pin | Use |
|---|---:|---|
| GP0 | 1 | UART0 TX to Pi through buffer |
| GP1 | 2 | UART0 RX from Pi through buffer |
| GP2 | 4 | Pi task-marker input through buffer |
| GP3 | 5 | Buffer common active-low enable |
| GP4 / GP5 | 6 / 7 | INA228 I²C0 SDA / SCL |
| GP6 | 9 | Monitor alert input |
| GP7–GP11 | 10, 11, 12, 14, 15 | Five indicator outputs |
| GP16–GP20 | 21, 22, 24, 25, 26 | SD MISO, software CS, SCLK, MOSI, card detect |

The complete 40-contact map is [carrier-pico-pin-contract.csv](hardware/review/carrier-pico-pin-contract.csv); the 25 monitor/storage module contacts are in [carrier-module-connections.csv](hardware/review/carrier-module-connections.csv). This is a documentary net/pin proposal, not KiCad capture, firmware or parity validation. Pi-side GPIO numbers are still open pending exact AI HAT and Pi UART configuration. Preserve all 40 Pi header contacts.

## Unfinished selection: carrier sockets and mating headers

The current shortlist in [carrier-support-candidates.csv](hardware/carrier-support-candidates.csv) is:

| Module | Candidate socket | Positions |
|---|---|---:|
| Pico | Harwin M20-7822042 | two × 20 |
| MikroE monitor | Harwin M20-7820842 | two × 8 |
| Adafruit storage | Harwin M20-7820942 | one × 9 |

The retained Harwin drawing is revision 11 (03-Aug-2026); the M20 family specification is retained in `hardware/evidence/carrier/`. The shortlisted socket has 8.5 mm above-board height and 3 mm tails. Calculated maximum tail diagonal is 0.783 mm; a proposed 1.00 mm finished hole with assumed ±0.05 mm tolerance leaves 0.167 mm diametral clearance. This is a paper fit screen, not a footprint or insertion test. The maker recommends 1.02 ±0.05 mm holes. Use pads at least 1.8 mm and check solder-tip access.

Harwin’s family specification gives up to 2 N insertion force/contact and at least 0.3 N withdrawal/contact. Sum-of-contact screens are 80 N/12 N for Pico, 32 N/4.8 N for monitor and 18 N/2.7 N for storage. These are not measured module forces. Support the board during insertion and assess extraction access. Its 20 mΩ initial / 30 mΩ post-conditioning maximum contact-resistance ratings yield only conditional connector-loss calculations; they do not qualify the actual mating parts or module header.

The possible 20-position male candidate M20-9992045 has 6.1 mm posts, but exact insertion depth, contact engagement, tolerance, plating compatibility and physical fit with the actual Pico remain open. Do not treat the manufacturer’s nominal post length as a mating qualification. The actual MikroE and Adafruit male headers also need drawing/part/revision confirmation. The older M20-7820846 tin socket is excluded: Harwin’s obsolescence notice lists it for immediate obsolescence. Do not recommend it just because a reseller lists stock.

The carrier envelope model places MikroE on the front and Adafruit storage on the underside while preserving the 78 × 54 mm outline. It is an envelope study, not a populated vertical-clearance pass. Verify module underside protrusions, solder tails, actual socket/header stack, Pico antenna region, card access, supports, cooler/HAT interactions and access to remove each module. Do not change the inherited outline or holes silently.

## Other open work

- Resolve exact supporting UART resistors, capacitor and DIP socket. Candidate codes are in `hardware/uart-support-candidates.csv`; none is in the selected BOM, even though 470 Ω nominal is approved.
- Confirm exact Pico 2 W orderable version/header arrangement and actual 3.3 V load budget with a selected card, monitor and LEDs. The 235 mA figure is an allocation, not a measured bound.
- Confirm the delivered MIKROE-4810 revision, module header/pin order and supply/current. Its onboard INA228 support circuit and I²C pull-ups must not be duplicated automatically.
- Finish measurement error budget: shunt/current calibration, finite INA228 input impedance, bus-voltage loading and ground offset, sampling/conversion timing, storage gaps and complete task energy uncertainty.
- Qualify sense-cable shorts, open/miswired pins, reverse/common-mode transients, lost ground and powered-off/transition states. Source series resistors limit certain positive observation-lead shorts only; they do not clamp voltage or protect the reference conductors.
- Finish protection: fuse/contact drop and heat, Pololu sustained current-limited fault behavior, connector/current sharing at 5 A, board copper and complete 5 A voltage drop. A 5 A supply current-limit setting does not establish a fuse-clearing guarantee.
- Assign Pi header signals with the target AI HAT(s), including Pi UART pins and any reserved HAT pins. Confirm all 40 contacts and populated Active Cooler/AI HAT+ and AI HAT+ 2 clearances.
- Only after the required part/module decisions and schematic authorization, capture conventional interposer and carrier schematics; export netlists, check connector contracts, run native ERC, then layout with KiCad 9, footprint/module review, native DRC and schematic-to-board parity. Do not suppress violations.
- Produce one-page soldering instructions, de-energized continuity/bench checklist and release CSV with reviewer/date/design hashes. Fabrication and connecting the Pi require the completed release checklist.

## Repository state and evidence

Current repository snapshot: branch `master`, base commit `0c8e77b` (“initial agent file”); `AGENTS.md` is modified, and `docs/` and `hardware/` are untracked. **Do not reset, clean, or discard these files:** they are the project’s current design record. No KiCad schematic or PCB files exist in this repository. No firmware project, release-checklist CSV or ERC/DRC/parity reports exist. The sibling `picopower` PCB files were inspected as read-only mechanical references; they have not been copied or modified here. No project files have been committed.

The latest provisional BOM has 19 distinct rows, including the owner-approved indicator parts. It is not a purchase order. Evidence source manifests cover 61 retained-source rows. Eight flat review receipts were hash checked; the MikroE-specific receipt has a nested schema and is intentionally not part of that flat-binding count. These are documentary input-binding checks, not a new electrical, physical or release pass. Each review JSON describes its own scope and historical versus refreshed checks.

Primary current documents:

- [Requirements](docs/requirements.md), [architecture](docs/architecture.md), [BOM](hardware/bom.csv)
- [Carrier integration/GPIO](docs/carrier-integration.md), [indicator approval/qualification](docs/indicator-options.md), [carrier pin contract](hardware/review/carrier-pico-pin-contract.csv)
- [Sense conditioning](docs/sense-interface-options.md), [ground reference](docs/ground-reference-review.md)
- [Monitor qualification](docs/mikroe-4810-qualification.md), [module fit](docs/carrier-module-fit.md)
- [Protection](docs/protection-options.md), [power connectors](docs/power-connector-options.md), [Pi/harness](docs/pi-harness-connector-options.md), [UART](docs/uart-interface-qualification.md)
- Machine-readable checks, calculations and source bindings are under `hardware/review/` and `hardware/evidence/`.

## Suggested immediate continuation

Finish the carrier socket/mating-header function as a sourced comparison with a recommended exact part set. Check current manufacturer drawings and lifecycle, lead/hole fit, actual post length and engagement, contact finish, insertion/extraction forces, 8.5 mm stack, underside modules and support access. Then present the socket decision to the owner and record it. If available documentation cannot establish a mechanical mating condition, label it open and identify what must be verified against the actual modules; never convert a paper envelope into a physical pass.

After socket choice, finish remaining UART support parts and Pico/module variants, one function at a time. Keep all approved decisions and prior BOM rows. The owner prefers direct progress and has already answered many project questions; only ask a new question when a specific unresolved choice blocks a concrete next action.

No purchase, payment, manufacturing upload, fabrication, hardware energizing, Pi connection, remote repository creation, publishing or external messaging is authorized by this handoff.
