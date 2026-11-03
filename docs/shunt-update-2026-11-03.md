# Shunt purchase selection — 2026-11-03

The owner approved updating the shunt BOM to **Bourns MSR3-0R005F1**, **Farnell 4582745**, one piece. This replaces MSR1-0R005F1 / Farnell 4582734 in the current BOM. No hardware has been ordered or energized.

## Sourcing evidence

[Farnell France product listing](https://fr.farnell.com/en-FR/bourns/msr3-0r005f1/res-0r005-3w-metal-element-radial/dp/4582745): the indexed snapshot retrieved on 2026-11-03 reports 1,407 in stock, EUR1.53 excluding VAT, minimum and multiple one. The search index dates the snapshot approximately one month earlier; this is not a live stock or checkout confirmation.

The [manufacturer product page](https://www.bourns.com/products/resistors/details/current-sense-resistors/msr) currently lists the MSR family. The [manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/msr.pdf), revision 05/26, is already retained as `hardware/evidence/shunt/bourns-msr-rev-05-26.pdf`. Its first-page table and drawing were inspected for this comparison. Exact ordering-code lifecycle confirmation remains open; a listed family and distributor stock do not establish an explicit Active declaration.

## Electrical and mechanical comparison

| Item | Former MSR1-0R005F1 | Selected MSR3-0R005F1 |
|---|---|---|
| Resistance and tolerance | 5 mΩ, ±1% | 5 mΩ, ±1% |
| Power rating at 85 °C | 1 W | 3 W |
| Lead pitch, drawing dimension L | 11.4 mm +1.0/−0.5 | 15.2 mm +1.0/−0.5 |
| Height, drawing dimension H | 5.1 ±2.5 mm | 25.4 mm maximum |
| Lead diameter | 1.0 ±0.05 mm | 1.0 ±0.05 mm |

At 5 A and nominal 5 mΩ, the calculated drop is 25 mV and dissipation is 0.125 W for either part. These are calculations, not measurements. The higher power rating does not increase resistance or dissipation at the same current. Four-wire pickups and installed calibration remain necessary; no 1% system-accuracy claim follows from the resistor tolerance. Do not use the catalogue's ±20 ppm/°C as a guaranteed installed-channel TCR: the manufacturer distinguishes resistance-wire TCR from the complete part's resistance-dependent behavior.

## Integration status: blocked pending CAD work

- The current generated interposer schematic, PCB, footprint and fabrication candidate still identify MSR1. This BOM update does not make those files suitable for MSR3.
- Adapt the 11.4 mm footprint to the new pitch and review Kelvin pickups, power copper and local clearances. Do not force the larger part into the old holes.
- Recheck the AI HAT arrangement: the previous estimated gap of about 17 mm does not cover the MSR3 drawing's 25.4 mm maximum height. Actual delivered height and a suitable placement or stack arrangement must be established before assembly.
- The existing 1.30 mm hole / 3.00 mm pad exception explicitly applies only to MSR1. The matching nominal lead diameter supports proposing those dimensions for MSR3, but this BOM-only request does not extend that exception or approve a changed footprint.
- Once CAD is changed, rerun the affected footprint, ERC, DRC, parity and power-path checks and update fabrication outputs and bound release evidence. Until then the BOM and CAD intentionally disagree and fabrication remains blocked.

The historical MSR1 qualification and 2026-11-02 sourcing audit remain records of their original selections. They are not qualification evidence for this substitution. Release receipts bound to the previous BOM are stale for the new selection; none were rebound or upgraded by this documentation update.
