# Lower-cost shunt follow-up

Date: 2026-10-15. Owner decision: the PBV at approximately €45.44 including VAT is too expensive. It is rejected on cost. No hole exception, final shunt selection or purchase is approved. A price-ceiling question was asked; pending an answer, this review explores parts below €5 each without making that an owner requirement.

The owner subsequently replied “ok” to the approximately €1.60 MSR1-0R005F1 proposal and then explicitly approved its 1.30 mm finished holes with 3.00 mm pads. The [four-wire and calibration qualification](msr1-qualification.md) records this prototype choice, with remaining checks open. This does not set an exact overall budget or authorize purchasing.

## Practical lower-cost direction

Consider **Bourns / Riedon MSR1-0R005F1** (5 mΩ) or **MSR1-0R01F1** (10 mΩ). These are two-lead welded through-hole parts, not true four-terminal shunts. Both remain candidates; four-wire sensing is still mandatory. The approved architecture permits independently reviewed sense points, but adding two traces to arbitrary current copper is insufficient.

| Candidate | Quantity-one listed price including VAT | Calculated drop at 5 A | Calculated dissipation at 5 A | Main tradeoff |
|---|---|---|---|---|
| MSR1-0R005F1, 5 mΩ, 1% | Approximately €1.58–€1.62 | 25 mV | 0.125 W | Lowest observed price and same nominal loss as PBV; lead and joint effects are a larger fraction of resistance |
| MSR1-0R01F1, 10 mΩ, 1% | Approximately €2.50 | 50 mV | 0.25 W | Twice the signal and half the fractional effect of a given added resistance; consumes another 25 mV of supply budget |

Price basis: DigiKey France indexed snapshots retrieved 2026-10-15, approximately one month old for the English listings. The 5 mΩ French indexed listing was three months old and slightly higher. Sources: [5 mΩ English](https://www.digikey.fr/en/products/detail/riedon-products-by-bourns/MSR1-0R005F1/1641055), [5 mΩ French](https://www.digikey.fr/fr/products/detail/riedon-products-by-bourns/MSR1-0R005F1/1641055), [10 mΩ English](https://www.digikey.fr/en/products/detail/riedon-products-by-bourns/MSR1-0R01F1/1641056). English snapshots list 324 and 1,858 in stock respectively. Direct retrieval failed; these are not live quotes. Shipping and possible marketplace charges are excluded. The same indexed regional page advertises €25 delivery below a €75 order, so an isolated shunt purchase can erase much of the saving; consolidate later sourcing only if the owner authorizes purchasing.

For comparison with the rejected €45.444 PBV snapshot, €1.584 is €43.86 less (96.5% reduction), and €2.496 is €42.948 less (94.5% reduction), before shipping. No saving in the complete instrument cost is established yet.

## Assembly and sensing constraints

The [current manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/msr.pdf), locally saved as [revision 05/26](../hardware/evidence/shunt/bourns-msr-rev-05-26.pdf), has two pages. Both were text-read; page 1 drawing and tables were visually inspected. It specifies round lead diameter **1.0 ±0.05 mm**, so a 1.0 mm finished hole does not accept the maximum lead even before insertion clearance. A modest larger-hole exception would still be required. No exact footprint is approved. The nominal lead pitch is 11.4 mm with +1.0/−0.5 mm tolerance; final pads must accommodate the permitted lead forming and insertion geometry. The MSR1 nominal height parameter is 5.1 ±2.5 mm; allow the full drawing envelope and mounting clearance, not only a catalogue body dimension.

A viable four-wire implementation needs separately routed sense takeoffs at documented terminal locations, short repeatable lead lengths, and no shared high-current copper between those takeoffs and the measured element. Sense contacts at PCB pads still include the resistor's current-carrying lead segments and some joint geometry. Calibration must therefore determine the effective installed resistance between the actual sense points. Lead/joint resistance and its temperature dependence do not disappear because the PCB has four traces. No such implementation or calibration has been validated here. Dedicated sense wires attached nearer the element would be a different hand-assembly option requiring its own mechanical and soldering review, not a silent substitute.

For scale only, **50 µΩ equals 1% of 5 mΩ**, and **100 µΩ equals 1% of 10 mΩ**. Those are calculated sensitivity thresholds, not estimates of actual lead resistance. Residual uncertainty must be smaller still because other instrument errors share the approximately 1% energy target. Initial 1% resistor tolerance already consumes that target without calibration.

The tabulated power rating is 1 W at 85 °C for MSR1, with derating above the stated reference condition. At nominal 5 A, the calculated dissipations are 12.5% and 25% of that reference rating; these ratios are not thermal measurements or fault validation. Full installed temperature and overload/fuse coordination remain open.

## Temperature and sourcing findings

Do **not** adopt the distributor's ±20 ppm/°C as an assembled-shunt guarantee. Page 1 calls it **resistance wire TCR** and separately plots complete-part TCR versus resistance. The [manufacturer product page](https://www.bourns.com/products/resistors/details/current-sense-resistors/msr) lists the family at ±125–±500 ppm. This is a family range, not a numeric guarantee for either exact candidate; no curve points were read as numbers. A source-grounded exact-part limit or calibration over the intended temperature range is still needed before claiming approximately 1% energy accuracy.

Bourns currently documents and markets the MSR family; DigiKey labels both exact candidates active. Explicit exact-variant manufacturer lifecycle status remains to be confirmed before selection. Do not confuse these Bourns order codes with obsolete Ohmite MSR1 R01 F stock. Other screened leads were excluded or not advanced: Ohmite 13FPR010E is marked obsolete by distributors despite remaining in its manufacturer's web catalogue; Vishay LVR03R0100FE12 is marked obsolete; 610FPR010E listings show low unit prices but large minimum quantities or marketplace terms, with no confirmed economical single-unit French offer.

## Current recommendation and evidence scope

Retain both MSR1 values as inexpensive **qualification candidates**, favoring the 5 mΩ option for initial cost comparison. Neither is an approved drop-in replacement for PBV. Continue only with explicit four-wire pickup/error analysis; preserve all existing measurement-boundary rules. The 10 mΩ option would require the INA228 ±163.84 mV range at the proposed 5 A because 50 mV exceeds ±40.96 mV. Its nominal range ceiling would then be 16.384 A before tolerance/temperature margins; this is an ADC scaling calculation, not a permissible DUT current. Total path-drop feasibility is still unresolved.

No PCB geometry, shunt value, monitor setting or assembly rule has been changed. No selected BOM, KiCad schematic, PCB or footprint exists. Documentation/source-hash/arithmetic checks cover this comparison only; ERC, DRC, parity, physical assembly and bench validation were not performed.
