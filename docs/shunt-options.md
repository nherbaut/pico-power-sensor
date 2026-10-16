# Through-hole shunt comparison

Review date: 2026-10-15. This is a component comparison, not a selected BOM, footprint approval or physical test. The owner approved proceeding with component qualification; no shunt has been chosen. Existing inventory: the owner reported no parts bought or selected for this prototype.

**Superseded recommendation:** the owner subsequently rejected the approximately €45.44 PBV price as too expensive. PBV is rejected on cost; the proposed drill exception was not approved. The original comparison below is retained as evidence, not a current recommendation. See the [lower-cost follow-up](shunt-cost-followup.md). No exact budget ceiling has been confirmed.

## Original recommendation and proposed decision — superseded on cost

The initial recommendation was to continue qualification of **Isabellenhütte PBV-R005-F1-0.5**, a 5 mΩ, 0.5%, four-terminal through-hole shunt. Its separate current and sense leads preserve Kelvin sensing without requiring SMD assembly. Its nominal calculated loss at the proposed 5 A is **25 mV and 0.125 W**. Changing resistance was not necessary on that electrical evidence. The owner rejected its price.

There is a specific conflict with the present assembly rules: the PBV's flat leads cannot fit 0.8–1.0 mm finished holes. The proposed exception is **larger factory-made plated holes or slots for this shunt only**, with correspondingly larger pads. The owner would solder the leads normally, without drilling the PCB. Do not modify AGENTS.md, select the part or implement a footprint until the owner accepts this exception and candidate direction. Exact hole/slot dimensions remain subject to lead-tolerance, insertion-depth, pad and fabrication review.

The PBV is no longer recommended for this prototype because of cost. Manufacturer lifecycle confirmation, a suitable iron-soldering process and populated interposer clearance were also open; no larger-hole direction was approved.

## Candidates

| Exact candidate | Construction and value | Mechanical assessment | Procurement observation | Disposition |
|---|---|---|---|---|
| Isabellenhütte PBV-R005-F1-0.5 | Four-terminal through-hole, 5 mΩ, 0.5%; manufacturer standard-value table includes this combination | Flat current leads up to 1.7 × 1.2 mm; sense leads up to 1.3 × 1.2 mm. Requires larger holes/slots. Body drawing 22.5 × 4.45 × 17.5 mm, excluding insertion/standoff effects | DigiKey France indexed listing: 998, €37.87 excluding VAT / €45.444 including VAT at quantity 1, shipping excluded | Rejected by owner on cost; not selected |
| Ohmite CS3FR005E | Four-terminal through-hole, 5 mΩ, 1%; manufacturer lists exact code | Manufacturer drawing has flat leads, including a 3.00 ±0.20 mm current-lead callout and 0.80 mm thickness. Incompatible with 1.0 mm holes; larger than PBV at the terminal. Final insertion geometry not reviewed | DigiKey France indexed listing: 169, €46.08 excluding VAT / €55.296 including VAT at quantity 1, shipping excluded | No benefit over PBV for this prototype established; lower initial accuracy and higher listed price |
| Ohmite 610FPR005E | Four-terminal bare-element through-hole, 5 mΩ, 1%; exact code is in manufacturer catalogue | Exact lead drawing not successfully retrieved for visual review. No drill-fit or footprint approval claimed | DigiKey listing: available to order, not stocked, minimum listed price break 250, 26-week manufacturer lead time | Poor single-prototype sourcing on this evidence; mechanical qualification incomplete |

Stock/prices are indexed distributor snapshots observed on the review date, crawled approximately four weeks earlier for PBV/CS3 and two months earlier for 610. They are not live quotes or reservations. RS also indexes the PBV exact code, but French price/stock could not be verified. Do not replace the DigiKey estimate with an unverified cheaper price.

Lifecycle is separate from stock: DigiKey labels all three active; current manufacturer documentation/catalogue supports the families/order codes, but an explicit manufacturer lifecycle declaration for these exact variants was not obtained. Keep lifecycle verification open before final selection. Bourns PWR4412-2S was screened out because the manufacturer marks it obsolete; old stock does not make it eligible. Two-terminal resistors were not substituted: board-level Kelvin traces would still include some terminal resistance and require a separate uncertainty analysis.

## PBV source and connection review

Use the [manufacturer datasheet, issue 12-February-2026](https://www.isabellenhuette.com/hubfs/Files/Data-sheets/PBV.pdf), saved as [PM-S05](../hardware/evidence/power-monitor/isabellenhuette-pbv-2026-02-12.pdf). All four pages were text-inspected; page 2 dimensions and page 3 standard values were visually inspected. No numerical values were extracted from plotted curves.

Page 2 drawing Z-DW-132b labels the terminals **I, U, U, I** across the illustrated body elevation: outer terminals carry current, inner terminals sense voltage. Adjacent nominal spacings are 5.08, 7.62 and 5.08 mm (outer span 17.78 mm). This source establishes terminal roles, not an independently verified KiCad top-view pad-number map. Any future footprint must record its view/datum/transform and corroborate the mapping before release. Connect upstream protection to one outer current terminal, DUT supply to the other, and take IN+/IN− separately from the inner terminals with matching polarity. Do not sense on the high-current solder pads.

The current-tail width is 1.5 +0.2/−0.1 mm, sense-tail width 1.1 +0.2/−0.1 mm, and thickness 0.8 +0.4/−0.1 mm. The conservative rectangular diagonals are calculated as 2.081 mm and 1.769 mm respectively, before insertion allowance or plating/finished-hole tolerance. Thus even the sense terminals fail the 1.0 mm rule. Wider shoulder sections, seating height, standoff and solder access must also be considered; these calculations are lower bounds for footprint development, not final drill specifications. Retain at least 1 mm solder-tip access and sufficiently enlarged pads/annular rings.

The datasheet's page 2 process table describes reflow/IR soldering, while page 4 specifies solderability by MIL-STD-202 method 208. Neither supplies an iron dwell-time qualification. Through-hole construction makes iron assembly plausible, but a permitted time/temperature process or separately authorized assembly trial remains necessary. Do not invent a dwell time or call hand soldering validated.

A 22.5 × 4.45 mm body projection alone does not prove fit. Check its installed height, insulation from nearby copper/hardware, lead access, harness bends and clearance to the Pi Active Cooler and required HATs on the inherited interposer. Preserve the existing outline, mounting holes and Pi header geometry. No placement or geometry change has been made.

## Electrical screening calculations

All figures below are calculations, not measurements. Conditions: proposed 5 A load, nominal 5 mΩ PBV, 0.5% initial resistance tolerance. Temperature behavior, ageing, soldering stress and other supply-path elements are excluded unless stated.

| Quantity | Result | Basis |
|---|---|---|
| Nominal shunt voltage | 25 mV | I × R |
| Nominal shunt dissipation | 0.125 W | I² × R |
| Initial-tolerance high resistance | 5.025 mΩ | 5 mΩ × 1.005 |
| Corresponding drop and dissipation | 25.125 mV, 0.125625 W | 5 A at high initial resistance |
| Nominal small-range current ceiling | 8.192 A | INA228 ±40.96 mV range divided by 5 mΩ; not a system overload rating |
| Small-range ceiling at high initial resistance | 8.151 A | 40.96 mV / 5.025 mΩ; temperature and overload margins still required |
| Remaining provisional path-drop allowance | 74.875 mV, equivalent to 14.975 mΩ at 5 A | 100 mV target minus 25.125 mV; for all other positive/return wiring, fuse, protection, contacts and copper combined |

PBV page 1 lists **3 W without heatsink / 10 W on a heatsink**, with temperature derating required. Do not copy the distributor's unconditional-looking 10 W field into a thermal claim. Nominal 0.125 W is approximately 4.17% of the unheatsinked reference rating; that ratio does not validate the assembled temperature or fault behavior. Fuse clearing, supply current limiting, possible overload energy and PCB heating remain separate protection work. No pulse rating is inferred from the page 4 curve, which is specifically for R0005 rather than R005.

For R <10 mΩ, page 1 specifies TCR <75 ppm/K over 20–60 °C. An illustrative 20 K change within that interval corresponds to <0.15% resistance change using the tabulated coefficient; it is not an all-temperature bound. The 0.5% initial tolerance is not a complete current/energy uncertainty. Calibration, monitor errors, timebase, thermal gradients, offset and marker boundaries still need a combined budget. The approximately 1% task-energy objective remains unproven; see the [monitor review](mikroe-4810-qualification.md).

## Evidence and next boundary

The [candidate CSV](../hardware/shunt-candidates.csv) keeps candidates distinct from selected parts. The [source manifest](../hardware/evidence/shunt/sources.csv) binds locally saved manufacturer material; [sourcing observations](../hardware/evidence/shunt/sourcing-observations.csv) retain the dated distributor snapshots. The Ohmite PDF links returned HTML or access errors; these were not accepted as PDFs. The 610 manufacturer page supports its catalogue identity but no visually reviewed lead dimension is asserted.

The owner rejected the PBV price. Continue with the lower-cost follow-up; final selection still requires closing the applicable qualification gaps. This review does not authorize purchases or hardware energizing. No schematic, board, footprint or BOM has been created; ERC, DRC, parity and bench validation are not performed at this stage.
