# Q1 procurement review and recommended resolution

Date: 2026-10-17. Reviewer: Codex. Status: **owner chose discrete MOSFET; sourcing unresolved; CAD not changed**. This follows the handoff at commit `14ab747` and the current AGENTS.md. The existing generated interposer still contains IPP80P03P4L-04 and a 1.2 mm-drill TO-220 footprint.

## Earlier recommendation (superseded by owner choice)

Restore **Pololu 5383**, sourced from Exp-Tech in Germany, rather than continue with the current obsolete-Q1 procurement line. The [manufacturer page](https://www.pololu.com/product/5383) explicitly says **Active and Preferred** and identifies reverse-voltage and reverse-current protection, 4–60 V operating range and approximately 5 mΩ on-path impedance. This is an assembled module, so the owner would solder its connectors, not its fine-pitch controller or MOSFET.

The [Exp-Tech listing](https://exp-tech.de/en/products/pololu-5383), observed through the web tool on 2026-10-17, lists **€4.10 excluding VAT, 21 units in stock, shipping from Germany**. At assumed 20% French VAT the module calculates to **€4.92**, before delivery and mounting connectors. The retrieved indexed page was about two weeks old; this is a dated sourcing observation, not a stock reservation or delivered checkout quote. Delivery may dominate the price of a separate order.

The earlier Pololu design exists in git before `85670e5`. A restoration should be surgical: reuse the module circuit and mounting work while preserving the current carrier, LED assignments, HAT arrangement and other later changes. The old fuse-first order, module connectors and their scoped exceptions would need to be reactivated explicitly in current documentation. Owner approval of restoring this option is still required; no purchase or CAD change follows from this review alone.

## Candidate findings

| Option | Evidence available in this review | Decision |
|---|---|---|
| Current IPP80P03P4L-04 | Handoff and owner report identify the originally selected device as end-of-life; current purchase sheet still said to order it | Mark current procurement line blocked pending replacement; do not treat it as ready to order |
| IPP120P04P4L03AKSA1 | [Mouser's IPP120P04P4L-03 listing](https://www.mouser.com/en/ProductDetail/Infineon-Technologies/IPP120P04P4L-03?qs=%252BWnEOWq1JvFWUOHcG7BlGg%3D%3D) says Obsolete, includes this exact AKSA1 code among aliases, and lists a 2024-07-29 discontinuation notice. Other distributor listings say Active | Withdraw the handoff's recommendation until the lifecycle conflict is resolved. The primary discontinuation PDF was not recovered; do not claim it was inspected or assert that only AKSA2 is obsolete |
| Vishay SUP90P06-09L-E3 | Retained primary datasheet specifies 11.8 mΩ maximum at −4.5 V under its 25 °C pulse-test conditions; dated Farnell search results do not establish current stock | Electrical compromise candidate only; 5 A reference calculation is 59 mV and 0.295 W. Hot performance, exact lifecycle, current availability and footprint still need review |
| Vishay SUP75P03-07-E3 | [Primary datasheet](https://www.vishay.com/docs/71109/supsub75.pdf), Rev E, gives 10 mΩ maximum at −4.5 V, −20 A and 25 °C, pulse width ≤300 µs and duty ≤2%; TO-220AB G-D-S, tab drain | Additional electrical compromise, **not a selected or fully qualified replacement**. At 5 A the resistance-reference calculation is 50 mV and 0.25 W. Exact lifecycle, stock, package dimensions, thermal/fault behavior and full fit remain unverified |
| Pololu 5383 | Current manufacturer lifecycle declaration and a dated European stock/price listing, plus extensive retained project review | Recommended prototype restoration, still subject to owner choice and the existing module qualification gaps |

The search target of ≤6 mΩ at −4.5 V appears in the handoff. Current AGENTS.md does not impose a fixed 6 mΩ Q1 limit; it retains an explicitly provisional total supply-drop goal. Treat 6 mΩ as the preferred selection target rather than silently creating a new immutable requirement. A higher-loss alternative could be proposed with its full voltage/thermal consequences and owner choice. None establishes acceptable Pi header voltage merely from its semiconductor resistance.

The XP4P016I and DIT110P06 assessments pasted by the owner were not independently requalified here. In particular, a recent datasheet date alone does not prove an exact ordering code is active. A “logic level” label or gate-threshold number alone does not establish on-resistance at the available gate voltage. Never turn an estimated multiplier from an unreviewed graph into a guaranteed warm resistance.

## Holes, mounting and fault behavior

Q1's current footprint uses 1.2 mm drills without an approved exception to the project's normal 0.8–1.0 mm rule. That is already an explicit open release condition. Do not request approval of this hole size before selecting the actual part and checking its maximum rectangular lead diagonal, finished-hole tolerance, insertion clearance and formed mounting geometry. Sharing a G-D-S pinout does not establish a mechanical drop-in replacement. The live drain tab and its clearance also need review.

Restoring the module would remove Q1 and R8's discrete gate network and make this particular Q1 hole exception unnecessary. Its earlier Samtec connector exceptions and mechanical/thermal checks are a separate matter; they would have to be reinstated and checked against the restored board.

The Pololu maker's approximately 5 mΩ value gives a simple 25 mV / 0.125 W reference at 5 A, not a guaranteed complete module drop. Its controller's forward regulation, temperature, contacts and traces matter. Its 4 V startup specification, low-input/short behavior, input transients and sustained supply-limited fault survival remain unresolved in the project. A 6.3 A fuse is not guaranteed to clear a 5 A current-limited fault. Reverse-current blocking does not authorize simultaneous bench and Pi USB-C powering or hardware energizing.

## Repository action in this review

The purchase Q1 row is marked **blocked, replacement choice required**, and the release checklist gains an explicit Q1 procurement gate. The selected topology, generated schematics, boards and fabrication files are unchanged. Earlier ERC/DRC/parity reports remain historical reports for their recorded design; they were not rerun or promoted by this documentary update. Earlier hash receipts that bind the edited BOM/checklist context must not be represented as fresh passes.

If the owner approves restoration, update the generator sources, current BOM and purchase sheet, protection/integration/assembly documents, applicable AGENTS.md choices and release record. Then regenerate only after checking KiCad open-file locks, inspect the generated schematic/PCB, run native ERC/DRC/parity and required copper checks, re-export the interposer fabrication candidate and bind new evidence to the resulting design. Keep all fabrication outputs unreleased until the remaining release conditions are complete.

## Owner direction and distributor search follow-up

On 2026-10-17 the owner explicitly chose to continue without Pololu and requested a MOSFET from Mouser or Farnell. The module restoration recommendation above is superseded. No discrete replacement has been selected, and no suitable stocked low-loss device has been verified at either requested distributor in this search. This is a search outcome, not proof that none exists.

Dated web observations on 2026-10-17 (indexed pages, not checkout quotes):

- **SUP90P06-09L-E3** remains the best electrically reviewed compromise in this search: 11.8 mΩ maximum at −4.5 V under the retained Rev B datasheet conditions, giving a calculated 59 mV and 0.295 W reference at 5 A and 25 °C. Not a hot installed bound. [Mouser](https://www.mouser.com/en/c/semiconductors/discrete-semiconductors/transistors/?mounting+style=Through+Hole&transistor+polarity=P-Channel&vgs+th+-+gate-source+threshold+voltage=3+V) lists zero stock. [Farnell 1684069](https://es.farnell.com/vishay/sup90p06-09l-e3/mosfet-p-to-220/dp/1684069) lists available to order, approximately 44 weeks and €6.86 excluding VAT on its Spanish site. French checkout price and delivery not verified. Do not present this as an immediately available purchasing solution.
- **SUP75P03-07-E3** is labelled obsolete/restricted by [Mouser](https://www.mouser.com/en/ProductDetail/Vishay-Siliconix/SUP75P03-07-E3?qs=l%252BcklhsjygejnWlO5Xf07A%3D%3D) and no longer manufactured by [Farnell 1794812](https://uk.farnell.com/vishay/sup75p03-07-e3/mosfet-p-ch-30v-75a-to220ab/dp/1794812). Withdraw its practical sourcing candidacy.
- **IPP120P04P4L03AKSA1** is also explicitly no longer manufactured at [Farnell 2725864](https://uk.farnell.com/infineon/ipp120p04p4l03aksa1/mosfet-aec-q101-p-ch-40v-to-220/dp/2725864), corroborating Mouser's obsolete indication. No primary discontinuation notice inspected.
- **XP3P7R0EP**, **XP3P7R0EI**, **XP3P010I** and **XP4P016I** Mouser listings are non-stocked with minimum orders of 3000; unsuitable for this prototype's procurement. Their technical qualification is not completed. [XP4P016I listing](https://www.mouser.pl/pl/ProductDetail/YAGEO-XSemi/XP4P016I?qs=wT7LY0lnAe2BLKRzVRDAXA%3D%3D).
- **STP52P3LLH6** surfaced as a through-hole logic-level alternative but [DigiKey](https://www.digikey.pt/en/products/detail/stmicroelectronics/STP52P3LLH6/7313469) labels it obsolete. Its active DPAK sibling **STD52P3LLH6** must not be confused with the TO-220 part. No suitable Mouser/Farnell supply established.

A supplier constraint change, accepting a significantly greater loss, or a different protection implementation would require an explicit proposal and owner choice. Keep the present purchase/release Q1 block. No footprint exception, CAD regeneration, purchase, or hardware test follows from this sourcing review.

## Resolution 2026-10-17 (Claude): Vishay Si4143DY, SO-8

After the owner confirmed that hand-soldering an SO-8 (1.27 mm pitch) is acceptable and supplied the Vishay Si4143DY datasheet, Q1 was changed to the **Si4143DY-T1-GE3**. Datasheet values (retained by the owner's upload, Vishay document 63242, S14-0910 Rev A): 9.2 mΩ maximum at −4.5 V / −5 A, 6.2 mΩ maximum at −10 V, −30 V, pinout 1-3 S / 4 G / 5-8 D. The generated schematic, SO-8 footprint, board, BOM, protection and soldering documents were updated, the interposer Gerbers re-exported and the release checklist rebound. ERC, DRC with parity, the copper-collision audit and the DC copper-resistance guard were re-run on the new board (13/13 branches pass). The owner reported 100,612 pieces ready to dispatch; the distributor is not named, so the purchase row still needs the distributor and order code. No exception to hole size is needed. Lifecycle of the exact code and its footprint against Vishay's own land drawing are still open.
