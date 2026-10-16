# Carrier module sockets and mating headers

Date: 2026-10-16. Status: **comparison for owner decision; documentary review only**. No part in this document is selected until the owner approves it. It continues the socket shortlist in [carrier integration](carrier-integration.md) and keeps the inherited 78 × 54 mm outline, holes and Pico header centres unchanged.

## Question

Each carrier module plugs into Harwin M20-782 sockets so that a wrong or dead module can be replaced. The socket alone does not complete the connection. The decision is which male header each module carries into those sockets.

## Evidence

| Source | Finding (documentary) |
|---|---|
| Harwin M20-782 drawing rev 11 (CAR-S03) | Socket 8.50 ±0.15 mm above board; contact point 3.41 ±0.25 mm; tail 3.00 ±0.25 mm; recommended hole 1.02 ±0.05 mm. 20- and 9-position codes and M20-7820842 are listed as available |
| Harwin M20-999 drawing (CAR-S06, new) | Male header: 6.10 mm mating post, 3.00 mm tail, 2.54 ±0.10 mm insulator, 0.64 ±0.02 mm square pin; M20-99920XX and M20-99909XX are on the active list; finish 45 = gold |
| Harwin C00120 (CAR-S05) | Both families use the same 0.64 mm square-pin system; 3 A/contact; 20 mΩ initial / 30 mΩ conditioned; gold 300 cycles, tin 50 cycles |
| Pico 2 W datasheet | 1 mm thick PCB, 0.1 in through-holes plus castellations. The datasheet does not specify the header fitted to the factory "WH" variant |
| MikroE product page | Not retrievable (HTTP 403). Whether MIKROE-4810 ships with headers fitted, and their length and plating, remain unverified |
| Adafruit 4682 guide | Ships with a loose header strip of unspecified manufacturer, length and plating |

## Options per module

| Module | Option A: supplied or factory header | Option B: documented Harwin header (recommended) |
|---|---|---|
| Pico 2 W | Pico 2 WH with factory headers; no header soldering, but header dimensions and plating undocumented, possibly tin against gold socket contacts | Headerless Pico 2 W plus two M20-9992045 (20-pos, gold). Owner solders 40 joints at 2.54 mm pitch onto the Pico. Gold-on-gold pair from one documented family |
| MikroE monitor | Factory headers, if fitted; dimensions unverified | If the delivered module is headerless, fit two M20-9990845 (8-pos, gold, M20-99908XX on the active list). Not needed if factory headers are present and fit |
| Adafruit storage | Supplied loose strip; undocumented | M20-9990945 (9-pos, gold) soldered instead of the supplied strip. Owner solders the header in either case, so it adds no work |

Sockets in every option: two M20-7822042 (Pico), two M20-7820842 (monitor), one M20-7820942 (storage), all with gold contact areas.

## Calculations (not measurements)

- Engagement past the contact point: 6.10 mm post − 3.41 mm contact point = **2.69 mm nominal**. With the stated tolerances (post ±0.25 mm general, contact point ±0.25 mm), the worst case is 2.19 mm. Harwin does not state the socket cavity depth, so whether a 6.10 mm post bottoms out before the header insulator seats on the socket is **open**. Check it on the first delivered pair.
- Pico stack, fully seated: 8.50 mm socket + 2.54 mm insulator + 1.0 mm Pico PCB = **12.04 mm** from carrier top to Pico top face, before components. This places the Pico antenna well above the carrier copper; antenna keep-out on the carrier remains a layout item.
- Insertion and withdrawal: unchanged from carrier integration (sum of ratings: Pico 80 N / 12 N, monitor 32 N / 4.8 N, storage 18 N / 2.7 N).
- Hole fit: header pin diagonal 0.64 × √2 = 0.905 mm (0.934 mm at +0.02 mm). On the module side, holes are the module's own. On the carrier, only the socket tails are drilled (maximum diagonal 0.783 mm); the proposed 1.00 mm holes are unchanged and need no exception.

## Recommendation

Option B for the Pico and storage. For the monitor, use the factory headers if fitted, otherwise M20-9990845. Reasons: both halves of every mating pair are drawn by one manufacturer with the same pin system and gold plating, which avoids undocumented tin-on-gold mating. The only extra soldering is 40 header joints on the Pico.

## Remaining open items

- Socket cavity depth versus 6.10 mm post (first-article check).
- MIKROE-4810 delivered header state, length and plating.
- Fit of 0.64 mm square pins in the Adafruit 4682 and Pico through-holes (both designed for standard 0.1 in headers; not dimensionally verified here).
- Exact-code lifecycle for every Harwin code: the drawing tables list families as active, but no exact-code lifecycle declaration was retrieved.
- Populated two-sided stack, solder access, supports and extraction access, as listed in [module fit](carrier-module-fit.md).

No purchase, footprint, schematic, ERC, DRC or physical fit has been performed.

## Owner decision

On 2026-10-16 the owner chose **option A** ("A"): Pico 2 WH with factory-fitted headers, the MikroE factory headers and the header strip supplied with Adafruit 4682, mating with the five Harwin M20-782 sockets listed above. The sockets and the Pico 2 WH are now in the [provisional BOM](../hardware/bom.csv). The Harwin M20-999 male headers are not selected. Consequences carried as open items: the factory and supplied header lengths and plating are undocumented, so seating depth and possible tin-on-gold mating must be checked on delivered parts; the exact Pico 2 WH ordering code is not yet recorded.
