# Measurement storage card

Selected on 2026-11-02 at the owner's request: **one Integral INMSDH32G10-90U1**, 32 GB microSDHC, Class 10 / UHS-I U1, Farnell **3410199**. This is removable storage in the instrument's Adafruit 4682 breakout, not the Raspberry Pi's operating-system card.

[Farnell France](https://fr.farnell.com/integral/inmsdh32g10-90u1/32gb-ultimapro-microsd-c10-90/dp/3410199) showed 1,815 units and €19.48 excluding VAT, minimum one, in an indexed listing retrieved on 2026-11-02. At 20% VAT that calculates to €23.38, before delivery. Availability is an observation, not a reservation or checkout quote.

The [manufacturer's current product page](https://www.integralmemory.com/product/micro-sd-card-microsdhc-xc-90mb-s-uhs-i-u1/) lists this exact 32 GB MPN. Its [specification](https://www.farnell.com/datasheets/2174071.pdf) identifies the capacity, card class and ordering code. A current catalogue entry was recovered, but an explicit manufacturer lifecycle declaration was not; do not label lifecycle fully qualified.

This is a cost-conscious bench-prototype selection, not an industrial or guaranteed high-endurance card. The Kingston industrial option found at CPC Ireland was approximately €97.72 excluding VAT. The cheaper preloaded Raspberry Pi card Farnell 4550988 is marked no longer manufactured, and the old Multicomp card 3879376 is no longer stocked; neither was selected. Their category pages still show prices, which do not establish availability.

## Use and qualification

- Reformat the card as **FAT32** before logging; no existing card has been erased or formatted.
- Use the existing 3.3 V instrument-side SPI connection through Adafruit 4682. No PCB change is required. The card itself has not been tested in SPI mode with this Pico firmware; the retrieved Integral documents do not establish a card-specific SPI performance guarantee.
- The existing 200 mA storage allocation is a design allocation, not a verified maximum for this card. Measure initialization/write peaks and the 3.3 V rail before closing the carrier power budget.
- Buffer records and use block writes. Log overflow/error counters and timestamps so write stalls cannot silently appear as complete acquisition. Flush and close before removing the card or instrument USB power. These are firmware requirements, not implemented or tested behavior.
- Endurance, worst-case write latency and power-loss integrity remain unqualified. The advertised UHS transfer speed is not a guaranteed SPI logging rate.

Capacity illustration only: 1,000 records/s at 64 bytes/record calculates to 64 kB/s; 32 billion nominal bytes would hold about 139 hours before filesystem overhead and reserve space. Actual record format and acquisition rate have not been selected.

No ordering or hardware energizing follows from this selection.
