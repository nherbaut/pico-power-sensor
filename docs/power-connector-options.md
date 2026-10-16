# Power-entry and protection-module connections

Date: 2026-10-16. **Owner-approved prototype choices and two scoped hole exceptions**, following the owner's response "ok" to the socketed set and both proposed exceptions. The selected connectors are recorded in the [provisional BOM](../hardware/bom.csv). Qualification remains partial. Scope: the interposer's bench-power entry and Pololu 5383 mounting connections. Pi pass-through parts and the measurement/UART harness were subsequently approved in the separate [Pi/harness review](pi-harness-connector-options.md); carrier sockets remain open.

## Selected set and alternatives

The owner selected a **Würth Elektronik 691137710002** two-position, 5.00 mm screw terminal for bench power, and **two Samtec TSW-102-07-G-S headers with two SSQ-102-01-G-S sockets** for a replaceable Pololu 5383. All soldering is through-hole. Gold mating surfaces are paired with gold; generic headers are not interchangeable merely because their pitch matches. The soldered-module and Phoenix alternatives remain unselected.

| Arrangement | Parts and quantities | Indicative component subtotal | Tradeoff |
|---|---|---|---|
| Selected, socketed module | 1 × Würth 691137710002; 2 × TSW-102-07-G-S; 2 × SSQ-102-01-G-S | €2.41 excluding VAT; €2.892 with assumed 20% French VAT | Replaceable module; adds two current-carrying mating contacts and about 8.5 mm of height compared with the soldered option |
| Lower module, soldered headers | Same screw terminal and two TSW headers; omit both sockets | €0.69 excluding VAT; €0.828 at 20% VAT | Saves €1.72 excluding VAT / €2.064 including assumed VAT (71.4% of the connector-set cost); module replacement requires desoldering four pins |
| Smaller power entry | Phoenix Contact 1727010 MKDS 1/2-3.81 in place of the Würth terminal; same Samtec pairs | €3.04 excluding VAT; €3.648 at 20% VAT, using €0.96 terminal observation | Approximately 7.61 × 7.3 mm body instead of 10 × 7.5 mm; €0.63 / 26.1% higher connector-set cost. Different footprint and hole exception would need a separate selection |

Unit observations: Würth €0.33 excluding VAT, [DigiKey France](https://www.digikey.fr/en/products/detail/w%C3%BCrth-elektronik/691137710002/6644051); TSW €0.18 excluding VAT / €0.216 including VAT, [DigiKey France](https://www.digikey.fr/fr/products/detail/samtec-inc/TSW-102-07-G-S/1101325); SSQ €0.86 excluding VAT, [DigiKey Portugal](https://www.digikey.pt/en/products/detail/samtec-inc/SSQ-102-01-G-S/1110617). These indexed observations are about one to three weeks old; the socket's cross-region EUR price is an estimate for comparison, not a France checkout quote. Phoenix €0.96 is a France catalogue observation; an RS offer is €1.13 each but requires a five-piece purchase (€5.65 excluding VAT), so it is not a €1.13 single-unit acquisition. Delivery, wire and hardware are additional. No order or payment is authorized.

## Current, loss and qualification

The [Würth manufacturer datasheet](https://www.we-online.com/components/products/datasheet/691137710002.pdf), revision 001.003 (2021-07-30), lists 16 A under cULus and 24 A under VDE; neither is an installed-board rating. It lists 20 mΩ contact resistance without a min/typ/max heading. At 5 A, assigning that value to **each** of the positive and return terminals gives a calculated 200 mV and 1 W total. This is a datasheet-value substitution, not measured loss or a hot-current guarantee. A high current rating alone does not close our voltage-drop budget.

The [Samtec catalogue](https://suddendocs.samtec.com/catalog_english/ssw_th.pdf) lists **SSQ/TSW: 6.3 A per pin with two pins powered**. The manufacturer's supporting power report tests a different, long double-row gold assembly and reports 6.3 A with two energized contacts, at 30°C rise after 20% derating, with 23.2°C room ambient. That supports the family selection; it does not measure these two-position connectors installed near our fuse. Temperature, actual supply-limit tolerance, solder joints and PCB copper still need qualification. No current is intentionally shared between contacts to obtain a larger rating.

The selected module interface has one 5 A VIN contact and one 5 A VOUT contact, on separate connectors. Its GND contacts serve the controller reference; provide the DUT's high-current return directly on the interposer. Do not route that return through the module as a required series path.

No applicable absolute worst-case resistance for the exact mated pair has been established here. **Do not use the power report's resistance changes as absolute resistance limits.** A planning scenario of 5 mΩ per positive mating contact adds 50 mV / 0.25 W at 5 A; that value is an allocation to validate, not a manufacturer specification. Combining it with the Würth table-value substitution adds 250 mV to the earlier protection reference before cable, Pi-header and remaining copper losses. The provisional 100 mV total-path preference remains unproven; a final minimum Pi voltage criterion remains open.

Exact manufacturer active/preferred lifecycle status remains an open qualification item: current Samtec exact-code pages and ordering tables were found, with Reserve-marked related configurations, and Würth supplies a current document marked Valid. Neither a document's Valid stamp nor a distributor's Active field is an explicit exact-code manufacturer lifecycle declaration. No known obsolete code is proposed. Final sourcing and release must resolve these gaps.

## Soldering and approved hole exceptions

The owner approved these **scoped exceptions** on 2026-10-16; actual footprint and fabrication checks remain required:

- Würth terminal, two electrical leads: **1.35 mm nominal finished plated holes, ±0.05 mm tolerance, 3.00 mm pads**, at 5.00 mm pitch. The drawing recommends 1.3 mm holes and shows nominal 0.7 × 1.0 mm rectangular pins. Matching the recommended opening is a preliminary fit argument; maximum lead dimensions and actual insertion remain to be checked.
- Two Samtec SSQ sockets, four electrical leads on the interposer: **1.10 mm nominal finished plated holes, ±0.05 mm tolerance, 2.00 mm pads**, at 2.54 mm pitch within each socket. Samtec's footprint recommends 1.02 mm openings; the print shows reference 0.64 mm square tails. Verify maximum lead envelope, finished-hole tolerance and insertion on actual parts before release.

These exceptions apply only to the named terminal and sockets. Existing shunt and holder exceptions, inherited mounting holes and 40-pin-header centres remain unchanged. TSW headers are soldered into the **existing Pololu slots**; do not drill or enlarge that module. No lead-hole exception is granted for the vendor's assembled board.

Use the two TSW short tails through the Pololu PCB, with their insulators below it and long posts pointing down into the SSQ sockets. The 5.84 mm nominal mating length lies within the catalogue's 3.68–6.35 mm insertion range. A nominal fully seated stack is `8.51 mm socket + 2.54 mm header insulator + 1.02 mm module PCB + 1.4 mm components = 13.47 mm` above the custom board; see the [nominal stack comparison](../hardware/review/power-connector-stack.svg). This calculation omits tolerance/seat gaps and is **not a maximum-height or HAT-clearance guarantee**. For a hypothetical 1.6 mm custom PCB, the socket's nominal 2.64 mm tail leaves about 1.04 mm for the solder joint; board thickness is not selected by that example.

For the soldered alternative, place header insulators on the interposer, module on their upper face, and trim excess posts after soldering. Its nominal module-top calculation is about 4.96 mm above the custom board, before tolerances. Do not solder a module in place while it remains plugged into a socket intended to stay removable.

The terminal accepts stranded conductors in the published range; a proposed 1.5 mm² copper pair is within it, but cable length, exact wire, bench-end termination and strain relief remain unselected. Manufacturer strip length is 6 mm and torque is 0.4 N·m. Support the connector body while tightening. Leave clearance for the screwdriver, wire exit and soldering iron; these require actual placement review.

## Connection contract and orientation

These are proposed custom-board connector assignments, not manufacturer numbering inferred from a list of signal names. Final footprint orientation must implement and visibly mark them.

| Connection | Pin | Proposed net and ownership | Normal and fault conditions |
|---|---|---|---|
| J_POWER bench terminal | 1 | BENCH_5V1_RAW, bench positive into fuse F1 | Planned +5.1 V; proposed 5 A load, supply limit set to 5 A. Actual current tolerance/transients unverified; reversed lead connection can apply negative voltage |
| J_POWER bench terminal | 2 | BENCH_GND, direct high-current return to supply | Normal DUT return up to the proposed 5 A target. No carrier/USB or signal cable may be its required substitute |
| J_RPIN socket/header | 1 | FUSED_5V1 → module VIN | Full DUT forward current plus upstream auxiliary bias; not an instrument-power output |
| J_RPIN socket/header | 2 | Module GND → local BENCH_GND reference | Tie to the same local reference region as the other module GND; avoid a geometry that makes the module a parallel high-current return |
| J_RPOUT socket/header | 1 | Module VOUT → PROTECTED_5V1 → upstream side of shunt | Full DUT forward current; still outside the measurement boundary. Reverse blocking does not establish forward-short disconnection |
| J_RPOUT socket/header | 2 | Module GND → same local reference region | Controller reference, not the Pi's required high-current return |

Use the retained Pololu labeled **top-view** photo and schematic as electrical authority. With VIN at upper left, VOUT at upper right and the GND pads below them, each proposed two-pin header spans its positive and GND slot. The module's slotted pads permit 2.54 mm headers; align them with the maker's 10.16 mm end-row spacing. Exact slot-to-post placement, socket orientation and assembly engagement must be checked on the actual footprint and module before release.

The symmetric headers are **not mechanically keyed**. Mark VIN, VOUT, GND and pin 1 on the custom silkscreen and soldering guide, and verify orientation electrically before applying power. Replacement is with both supplies off. With bench off / USB on or the reverse, these connectors provide no permission to join positive supplies or bypass the separate sense/UART powered-off checks. Reversed bench leads with USB/earth connections still require a complete ground-path fault review.

## Evidence and remaining work

Retained manufacturer drawings and the limited review record are under [connector evidence](../hardware/evidence/connectors/sources.csv). Direct Würth and Phoenix PDF downloads returned HTTP403 after an escalated attempt. Würth revision 001.003 tables were readable through the web tool; an older manufacturer document, revision 001.002 (2019-08-12), was retained from Octopart and its page 1 visually inspected. Its printed nominal dimensions/hole pattern agree with the newer web-readable callouts. This is not a visual review of the newer PDF or a completed footprint qualification. Phoenix's generic dimension image is not a numbered pin or hole drawing.

Samtec's assembly prints (SSQ revision BH, TSW revision DS), recommended layouts (revision A), catalogue and power report were retained. Relevant printed dimensions were visually inspected; no numerical curve values were read. Generic KiCad 1×2 header/socket footprints do not prove Samtec body height, mating depth, hole fit or current rating. No custom footprint, schematic, routed PCB, ERC, DRC, parity, thermal test or physical connection has passed here. The component choices and two scoped drill exceptions are approved for the prototype; installed fit, loss, thermal behavior, lifecycle and cooler/HAT clearance remain open. This decision does not authorize purchase, fabrication or hardware energizing.
