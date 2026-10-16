# microSD module options

Comparison date: 2026-10-15; owner selection recorded 2026-10-16. Requirements: removable microSD logging on the independently USB-powered Pico 2 W carrier, assembled with an ordinary iron. The socket and small parts must arrive soldered; the owner may solder 2.54 mm headers. The owner approved **Adafruit 4682 in SPI mode**; it is now in the [provisional BOM](../hardware/bom.csv). No card or separate card regulator has been selected, and no purchase was authorized. Existing inventory was already reported empty for this prototype; no account/inventory access was attempted.

## Recommendation

Choose **Adafruit 4682, Micro SD SPI or SDIO Card Breakout Board, 3V only**, for further integration in **SPI mode**. It provides a pre-assembled socket and passive parts without a regulator or level shifters. It is the lowest-priced documented 3.3 V candidate found in this comparison, with a French supplier option. Fit header pins and a replaceable carrier socket; do not place its bare microSD socket or tiny passives on the custom PCB.

The owner accepted this recommendation. The choice remains conditional on the full power and populated mechanical reviews below; it is not a claim that storage qualification or the carrier layout is complete. The [combined capacity study](carrier-module-fit.md) supports continuing with storage on the underside while keeping the inherited board geometry.

| Option | Price observation at quantity 1 | Interface and assembly | Disposition |
|---|---|---|---|
| Adafruit 4682 | DigiKey France €3.684 including VAT, indexed approximately one week earlier; GoTronic ADA4682 €4.55 including VAT, indexed approximately one month earlier; maker US$3.50 | Direct 3.3 V SPI or SDIO; assembled socket/passives; header strip supplied loose | Owner-approved prototype choice; use SPI; card power and full carrier fit remain open |
| Pololu 2597 | Maker US$4.95 | Direct low-voltage breakout, 2.54 mm headers supplied loose; maker labels Active and Preferred | Alternative, smaller nominal 20.32 × 17.78 mm envelope; support passives and exact header geometry not qualified here |
| SparkFun BOB-00544 | Maker US$5.95, listed in stock | 3.3 V socket breakout, assembled/tested; no level shifter per maker guide | Alternative; more expensive at maker price; full mechanical/support-circuit review not performed |
| Pololu 2587 | Maker US$7.49; Active and Preferred | Onboard regulator, but MISO is translated to 5 V and EN/CD default pull-ups go to its 5 V VDD | Excluded from a direct Pico connection; a regulator on a module does not establish 3.3 V logic compatibility |

Sources: [Adafruit product](https://www.adafruit.com/product/4682), [DigiKey offer](https://www.digikey.fr/en/products/detail/adafruit-industries-llc/4682/12822319), [GoTronic offer](https://www.gotronic.fr/art-lecteur-de-carte-micro-sd-ada4682-33468.htm), [Pololu 2597](https://www.pololu.com/product/2597), [SparkFun](https://www.sparkfun.com/sparkfun-microsd-transflash-breakout.html), [Pololu 2587](https://www.pololu.com/product/2587). Prices exclude cards, sockets, shipping and any marketplace charges; USD figures are not converted into euros or treated as French tax-inclusive prices. No cart, order or payment was created. GoTronic's slightly higher unit price may be preferable for a small local order; final landed cost is not established.

## Adafruit pinout and included circuitry

The [vendor source schematic](../hardware/evidence/storage/adafruit-4682-source.sch) and [board](../hardware/evidence/storage/adafruit-4682-source.brd) are Eagle files retained unchanged as evidence, not project KiCad designs. They were parsed independently as XML and the header connections cross-checked. The [manufacturer guide](../hardware/evidence/storage/adafruit-4682-guide.pdf), page 45 schematic/fab drawing, was visually inspected. The header has **one row of nine contacts at 2.54 mm pitch**, not two rows. Numbering below is vendor JP1 numbering; the future carrier socket must preserve orientation and mark pin 1.

| Vendor JP1 pin | Vendor net / function in SPI mode | Carrier connection |
|---|---|---|
| 1 | 3.3V | Instrument 3.3 V card supply only; never USB 5 V or DUT 5 V |
| 2 | GND | Instrument ground |
| 3 | SCLK | Pico SPI clock |
| 4 | DO / SO / DAT0 | Pico SPI MISO |
| 5 | DI / SI / CMD | Pico SPI MOSI |
| 6 | CS / DAT3 | Pico chip select |
| 7 | DAT1 | No external connection in SPI mode; retain onboard pull-up |
| 8 | DAT2 | No external connection in SPI mode; retain onboard pull-up |
| 9 | CARDDET / DET | Optional Pico input; low without a card, high with a card per manufacturer pinout guide |

The retained source includes 10 µF and 100 nF supply bypass capacitors plus two 47 kΩ four-resistor packs, with seven used pull-ups (clock, command, data/CS and detect nets). It has no regulator or level shifter; do not duplicate those bypass/pull-up networks automatically. Carrier bulk capacitance may still be necessary after transient review. The [web pinout guide](https://learn.adafruit.com/adafruit-microsd-spi-sdio/pinouts) calls the detect pull-up 4.7 kΩ, whereas the retained schematic specifies 47 kΩ. Preserve this source discrepancy; it does not change pin function, but confirm the supplied revision/value before deriving leakage, pull-up current or timing bounds from it. The product lists a 2024 silkscreen update, while the public CAD/guide schematic is an earlier revision.

Header-pad centres in the vendor board are at x=2.54 through 22.86 mm, y=2.54 mm, with 20.32 mm end-to-end span. Vendor module pads are 1.778 mm diameter with 1.0 mm drill; these describe the purchased module, not an approved custom carrier footprint. The new carrier socket pads must satisfy the project's ≥1.8 mm pad rule, lead-fit and solder-tip clearance. Confirm header fitting and actual module assembly access during footprint review; do not copy the vendor land pattern into the carrier blindly.

## Power and acquisition contract

Proposed first power direction: supply the module from the Pico's **instrument-side 3V3 output**, with the same rail as its I/O. The [Pico 2 W datasheet](../hardware/evidence/storage/pico-2-w-datasheet.pdf), release 2 build 03 July 2026, PDF page 9, recommends keeping external load below 300 mA and states that available current depends on RP2350 load and VSYS. This is not an unconditional 300 mA guarantee for every operating state.

A preliminary allocation is 200 mA for the selected card/module, 15 mA for the monitor module, 10 mA for five indicator LEDs, and 10 mA for other carrier/interface loads: **235 mA total**, calculated, leaving 65 mA below that recommendation. These are design allocations, not measured loads or component limits. Card type/peak current, final LED currents, radio/controller operating states, actual regulator margin, USB source/cable and transient voltage are unverified. Select and validate the actual card before accepting this supply arrangement. A bulk capacitor cannot prove an unknown peak-current requirement is met. If this budget fails, qualify a separate hand-solderable instrument-side regulator; do not draw card power from the DUT or force a 5 V logic module onto the Pico.

Use a dedicated Pico SPI bus for storage; the INA228 remains on I2C. The [carrier integration map](carrier-integration.md) now allocates GP16 MISO, GP17 software CS, GP18 SCLK, GP19 MOSI and GP20 card detect; schematic/parity validation remains open. Keep CS deasserted through reset using the module's existing pull-up. Use 3.3 V signals only, and ensure the card rail is present before driving the interface. No independent card power switch is proposed here; if added later, revisit back-powering and sequencing. Hot insertion/removal and unpowered states require later checks.

Buffer acquisition independently of filesystem writes. At the illustrative 1.08 ms conversion-pair period, a proposed 32-byte binary record gives a **calculated 29,630 bytes/s** before filesystem overhead. A 64 KiB buffer would cover approximately **2.21 seconds** at that nominal rate. Neither number is a demonstrated storage throughput or worst-case card stall bound. Validate write latency and buffer overflow behavior with the actual card; record dropped samples and logging failures. Preserve task markers, timestamps and acquisition validity rather than counting repeated register reads as new measurements. Card capacity/filesystem compatibility is a firmware/card decision; the retailer's “8 GB maximum” is not adopted as a proven electrical limit of this passive breakout.

## Mechanical and evidence boundaries

The Adafruit source board has a 25.4 × 22.86 mm envelope, consistent with its rounded product dimensions. The inserted card projects beyond the board; leave insertion/ejection and finger access. The previous MikroE-only envelope study does **not** establish room for this added module: at its illustrative (8, 5.5) mm placement, the monitor occupies most of the space left of the fixed Pico socket. Joint placement, socket heights and potentially mounting a module on the underside must be evaluated before calling the carrier feasible. No flat, fully populated carrier fit has been established. Do not change the inherited outline, mounting holes or Pico header to make it fit without first reporting the required change.

Sources are retained in [the manifest](../hardware/evidence/storage/sources.csv), including attribution/license for Adafruit CAD. Pololu's published single-page schematic was visually inspected to confirm its 5 V output path; it was not qualified as a Pico-compatible design. A SparkFun legacy binary Eagle board was retrieved during research but could not be XML-parsed; no geometry claim depends on it and it is not included as qualified evidence. No custom KiCad schematic or PCB was created, so native ERC, DRC and parity were not run. Physical assembly, power-transient, throughput and populated-clearance validation remain separate future work.
