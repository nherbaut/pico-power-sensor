# Interposer protection options

Date: 2026-10-16. **Owner-approved prototype choices**, following the owner's response "go for it" to the proposed three-part set and holder hole exception. Littelfuse 021706.3MXP, Schurter 0031.8201.G and Pololu 5383 are recorded in the [provisional BOM](../hardware/bom.csv). Qualification remains partial; no fabrication or electrical release is established. The comparison uses a planned 5.1 V supply and the owner-confirmed 5 A current-limit setting; it does not treat that setting as a measured maximum.

## Recommendation and cost

The owner selected **Pololu 5383** as the prototype reverse-polarity module, with a **Littelfuse 021706.3MXP** replaceable 6.3 A cartridge fuse and **Schurter 0031.8201.G** through-hole holder. The assembled module avoids fine-pitch soldering and has much less normal loss than the examined discrete P-channel or Adafruit alternatives. **Its sustained short-circuit survival is unresolved:** the prototype choice does not authorize fabrication, connection to a Pi, or declaring the protection qualified.

| Option | Component price, quantity one | Calculated semiconductor reference at 5 A | Assessment |
|---|---|---|---|
| Pololu 5383, assembled LM74700-Q1 ideal-diode module | €4.10 excluding VAT; €4.92 with assumed 20% French VAT, before delivery | 25 mV / 0.125 W using the maker's approximately 5 mΩ path description | Owner-approved prototype choice; active/preferred maker status; startup and sustained low-input fault qualification still required |
| Adafruit 6359, assembled LM73100 module | €4.33 excluding VAT / €5.196 including VAT, before delivery | IC full-range resistance limit 44.85 mΩ gives 224.25 mV / 1.12125 W; module contacts/copper extra | Alternative if greater drop is accepted; back-to-back switches and thermal shutdown, but not a 5 A circuit breaker |
| Vishay SUP90P06-09L-E3, discrete high-side P-channel TO-220 | €5.78 excluding VAT in the observed Spanish distributor listing; stock zero; supporting parts/thermal provision extra | 59 mV / 0.295 W using its 25°C, −4.5 V pulse-test resistance | Do not recommend: no present stock in that observation, incomplete exact lifecycle evidence, hot −5 V limit and sustained body-diode thermal case unresolved |

These are component observations, not delivered quotes. Price sources: [Exp-Tech 5383](https://exp-tech.de/en/products/pololu-5383), [DigiKey France 6359](https://www.digikey.fr/fr/products/detail/adafruit-industries-llc/6359/26832920), [DigiKey Spain SUP90](https://www.digikey.es/en/products/detail/vishay-siliconix/SUP90P06-09L-E3/2623132). Their indexed snapshots are respectively about two weeks, one month and one month old when observed. Exp-Tech's prose says 10 mΩ but its specification table says <5 mΩ; use the [maker's 5383 page](https://www.pololu.com/product/5383) as technical authority. The 25 mV calculation is a resistance-only reference, not a guaranteed module drop: the controller deliberately regulates forward voltage, nominally 20 mV, and contacts, temperature and tolerances add uncertainty.

Common fuse costs: [021706.3MXP at Farnell France](https://fr.farnell.com/littelfuse/021706-3mxp/fusible-cartouche-act-rapide-6/dp/1354579), €0.59 excluding VAT; [0031.8201.G at Mouser France](https://www.mouser.fr/en/ProductDetail/Schurter/0031.8201.G?qs=53fxdJjyGHQ26HnfkWkpvg%3D%3D), €1.14 displayed EUR, treated as excluding VAT for this estimate. Snapshots are about one and two months old. The recommended three-part subtotal is **€5.83 excluding VAT, approximately €7.00 at 20% VAT**, before connectors, sockets, cover, wiring and delivery. Three different suppliers can make delivery dominate; consolidate the eventual whole-project purchase. The Adafruit alternative subtotal is €6.06 excluding VAT, €0.23 / 3.95% higher; its module is €0.23 / 5.61% higher. No purchase is authorized.

The fuse is backup protection, not a guaranteed 5 A disconnect. Its time/current table does not establish clearing at 5 A. Retain the 6.3 A candidate only with the eventual wiring/contact ratings, ambient derating and fault coordination review; do not increase its rating to reduce drop. Current manufacturer exact-code active status remains unconfirmed for the fuse and holder; current Schurter family ordering data lists the holder, and distributors report active status. These gaps prevent final qualification rather than proving either part obsolete.

## Circuit and measurement boundary

```text
Bench + → cartridge fuse → module VIN → module VOUT → shunt → Pi 5 V header
Bench − ───────────────── direct high-current return ───────→ Pi ground
                            module GND connects to this return
```

Both module power nodes are upstream of the shunt. All module bias, divider, LED and leakage currents therefore stay outside reported DUT current. The module supplies no instrument rail. Use the existing Kelvin pair across the shunt; do not use either module's power terminals or IMON as the precision current measurement. Neither candidate converts voltage. Do not duplicate assembled MOSFETs/controllers, onboard capacitors, dividers or indicator parts.

For a discrete P-channel comparison, the drain faces fused input, source faces protected output and gate returns through a resistor to ground. Under correct input the body diode permits startup; reversed input prevents normal enhancement. A hard output short collapses source/gate drive, so the body diode can carry the limited current continuously. This is a topology screen, not an approved circuit.

## Loss and thermal limits

The complete path calculation must include both positive and return resistance:

`Vdrop = V_fuse(I,T) + V_holder(I,T) + V_module(I,T) + I × (R_shunt,installed(T) + R_copper,+/−(T) + R_cables,+/−(T) + R_contacts,+/−(T))`.

At 5 A, nominal cold fuse plus nominal shunt gives 72.5 mV / 0.3625 W. Adding the Pololu resistance-only reference gives **97.5 mV / 0.4875 W before holder, copper, cables and connectors**. Thus even this optimistic subtotal leaves essentially no room for the original provisional 100 mV preference. A finished 100 mV path is not demonstrated.

Schurter specifies ≤10 mΩ contact resistance at 100 mA without an explicit per-contact versus complete-holder scope in the reviewed data. A conservative *sensitivity scenario*, assigning 10 mΩ to each of two contacts, adds 100 mV / 0.5 W at 5 A. It is not a guaranteed hot-current bound. That scenario produces a 197.5 mV Pololu subtotal and 4.9025 V remaining from 5.1 V, before all other losses. Substituting the Adafruit IC resistance limit produces 396.75 mV / 4.70325 V under the same mixed-basis scenario. Neither result establishes the voltage at the Pi or an acceptable Pi supply criterion. Full-range shunt/lead effects and warm fuse behavior remain unbounded here.

No continuous thermal pass is claimed. Local ambient, airflow and the actual installed thermal paths are not fixed. Keep fuse/holder/module heating away from the shunt where possible; calibration does not remove subsequent shunt temperature drift. See the [calculation ledger](../hardware/review/protection-calculations.csv) for conditions and exclusions.

## Fault qualification

| State | Pololu 5383 | Adafruit 6359 | Required evidence before release |
|---|---|---|---|
| Correct input, normal load | Low-loss candidate; maker describes around 12 A continuous capability, not our assembled rating | Maker advertises up to 5 A; complete module thermal performance still needs validation | Installed drop and temperatures; connector and copper ratings; local ambient |
| Short present at startup | Controller may remain below startup voltage; forward body-diode path remains | Back-to-back switches permit disconnection on undervoltage; soft-start and supply control-loop interaction need review | Start into a dummy-load short; bound pulse stress, repeated restarts and sustained heating |
| Short applied while running | Input collapse can disable charge pump/gate enhancement; no forward short disconnect is established | Fast trip is typically 21.9 A, not 5 A; undervoltage can recover automatically; thermal shutdown latches | Do not rely on fast trip or fuse clearing; verify the 5 A limited-fault response and capacitor-discharge transient |
| Reversed input | Maker provides reverse-voltage blocking; common-ground wiring must be respected | Reverse-polarity blocking; protected pin limits depend on complete module circuitry | Verify no alternate ground/USB path carries fault current and no exposed interface back-powers the DUT |
| Bench off, instrument USB on, and reverse order | Reverse-current blocking helps only the positive power path | Back-to-back switches block the positive reverse path | Separate sense/UART powered-off and ground-return checks remain mandatory |

Technical authority: retained [LM74700-Q1](../hardware/evidence/protection/ti-lm74700-q1-snosd17g.pdf) electrical table and functional description, and [LM73100](../hardware/evidence/protection/ti-lm7310-snosdc0a.pdf) §§6.5, 7.3.4.2, 7.3.7–7.3.8. TI explicitly recommends additional series overcurrent protection for persistent LM73100 faults. A 5 A bench limit is the intended primary current-limiting layer, but its tolerance/transients are unverified. Neither option is a completed fault-protection solution solely on these documents. No numerical plot values were extracted.

## Assembly, pinout and fit

Pololu 5383 arrives with controller, N-channel MOSFET and three 100 nF capacitors assembled. The optional TVS position is unpopulated; it must not be credited as installed protection. Maker board identifiers are `rvp01a` / `0J4041`. The pinout is established by its labeled top-view photo and schematic: with VIN/VOUT at the top, left column VIN then GND; right column VOUT then GND. The [mechanical drawing](../hardware/evidence/protection/pololu-reverse-voltage-protectors.pdf) gives a nominal 7.6 × 12.7 mm board, rows 10.16 mm apart, and four slots 1.14 mm wide with 1.27 mm between arc centers. Do not mistake these slot dimensions for round custom-board drills. The owner subsequently selected two Samtec TSW-102-07-G-S headers and two SSQ-102-01-G-S sockets; see the [connection review](power-connector-options.md) for rating evidence and the approved socket hole exception. Actual engagement, installed current/thermal performance and populated height remain unverified; **do not substitute an unspecified ordinary 3 A header**.

Adafruit 6359 source CAD maps JP1 pins 1–9 to VOUT, IMON, DVDT, PGTH, PG, OVLO, UVLO/EN, GND, VIN. It includes 10 µF input/output capacitors, 22 nF + 100 Ω slew network, 1 MΩ/580 kΩ/87 kΩ threshold ladder, 1.5 kΩ IMON resistor, LED/47 kΩ and a closed LED jumper. The CAD outline is 25.4 × 17.78 mm; the product envelope is 25.6 × 17.6 × 11.9 mm, so reserve 25.6 × 17.78 mm in this preliminary study. The CAD uses 1.0 mm holes and 1.778 mm header pads on the vendor board; any custom footprint must meet the project's ≥1.8 mm pad rule. The module is an assembled alternative, not permission to copy its bare SMD circuitry onto the custom board.

**Owner-approved holder exception (2026-10-16):** two **1.35 mm nominal finished plated holes, tolerance ±0.05 mm, with 3.00 mm pads**, only for Schurter 0031.8201.G. This fits the manufacturer's 1.30 to 1.40 mm drilling callout; verify eventual fabrication tolerances. Pitch is 22.5 mm. The installed body allowance is 25 × 10.8 mm and about 12.7 mm high with the illustrated cover. Contact orientation is interchangeable. The separately approved shunt holes remain 1.30 mm; the holder exception does not change them or authorize an extra central fastening hole.

The installed KiCad library `Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open` was inspected: two 3 mm pads, 22.5 mm pitch, 1.3 mm drills, plus an anonymous 2.7 mm central NPTH. Its 26 × 10.1 mm courtyard does not contain the manufacturer's 10.8 mm installation width. It requires a project-reviewed derivative with corrected drilling/courtyard and an intentional decision about the central fastening hole; it is **not approved unchanged**. This proposal does not add a new central mounting hole or alter the inherited mechanical baseline.

The [planar capacity model](../hardware/review/protection-envelope.svg) reserves both alternatives, fuse-holder installation width, all 40 inherited header pads and both inherited mounting holes. Their drawn bodies fit the inherited outline without moving those features. It is not a routed board or a completed placement: power entry, shunt, other connectors, sockets, access and populated cooler/HAT height remain open. No physical fit, footprint completion, ERC, DRC, parity or bench pass is claimed.

The owner approved this **prototype set and holder hole exception** with "go for it" on 2026-10-16. AGENTS.md and the provisional BOM record that choice, with the unresolved qualification items retained. The owner subsequently approved the Würth bench terminal and Samtec module header/socket set, with their scoped hole exceptions; see the [connection review](power-connector-options.md). The Adafruit Pi socket and JST-XH harness set, with the Adafruit-only hole exception, are also now approved prototype choices; see the [Pi/harness review](pi-harness-connector-options.md). Remaining carrier sockets, module/power choices and interface protection still need resolution before schematic capture. No purchase, fabrication, hardware energizing or release approval follows from these component choices.

## Owner decision 2026-10-17: Pololu 5383 replaced by a TO-220 P-MOSFET

The Pololu 5383 is not sold by Farnell or Mouser. At the owner's request ("cherche une alternative chez farnell", then "oui"), it is replaced by an Infineon IPP80P03P4L-04 (OptiMOS-P2, 30 V, 80 A, logic level, intended by Infineon for reverse-battery protection; Farnell codes 2443406 / 3290154 observed) with a 10 kΩ gate pull-down (Vishay MRS25000C1002FCT00). Order on the interposer: J1 → Q1 → F1 → R1.

- Function: correct polarity, the body diode conducts, the gate sits 5 V below the source and Q1 turns on; reversed leads, Q1 stays off. Calculated loss with an assumed 4–6 mΩ on-resistance at about 5 V gate drive: 20–30 mV, below 0.2 W at 5 A (estimate from the Farnell listing values; confirm against the Infineon datasheet curves).
- Lost compared with the Pololu ideal diode: no blocking of reverse current from the load side. Do not power the Pi from USB-C while the bench supply is connected.
- Mounting: TO-220 lying flat, tab (drain) down, no screw; about 4.5 mm high. Footprint drill 1.2 mm (pending owner hole exception).
- Removed BOM lines: Pololu 5383, two TSW-102-07-G-S, two SSQ-102-01-G-S.
