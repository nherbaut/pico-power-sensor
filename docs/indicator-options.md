# Five programmable indicators

Date: 2026-10-16. Status: **owner-approved prototype option; qualification partial**. Use five identical red through-hole LEDs labelled LED1–LED5; software controls their meanings. This meets the programmable-indicator requirement without a driver IC or extra supply.

The owner accepted the set with "ok" on 2026-10-16. Selected prototype parts: **five Vishay TLLR4401** low-current 3 mm LEDs and **five Vishay MRS25000C1801FCT00**, 1.8 kΩ, 1%, axial resistors. Each branch is Pico GP7–GP11 → resistor → LED anode, with cathode to instrument ground. High means on. All indicator energy comes from Pico USB, outside reported DUT current.

| Option | Consequence |
|---|---|
| **Five red LEDs with 1.8 kΩ each** | Recommended: one LED type, five independent outputs, modest current |
| Mixed red/green/yellow LEDs | Possible alternative; separate codes and brightness/current reviews needed, particularly for higher-forward-voltage yellow LEDs |
| Lower resistances for brighter LEDs | Requires a revised current allocation and GPIO/load review; not selected |

## Electrical screen

The [Vishay datasheet](https://www.vishay.com/docs/83029/tllx440x.pdf) characterizes TLLR4401 at 2 mA and 25 °C: forward voltage is 1.9 V typical, 2.4 V maximum; luminous intensity is 1 mcd minimum, 2 mcd typical. These do not guarantee brightness at our lower current. Using 1.9 V only as an illustrative fixed-drop model gives **0.778 mA per LED**, or **3.89 mA for five**, at 3.3 V. This is not a solved LED operating point or a brightness measurement; visibility needs checking with the actual parts and lighting.

For a deliberately conservative calculation, set LED drop to zero, use the existing hypothetical 3.465 V rail and 1.8 kΩ −1%. Current is then **1.944 mA per branch**, **9.722 mA for five**, within the existing 10 mA allocation under those assumptions. The same model limits resistor dissipation to **6.74 mW per branch**. Actual rail maxima, resistor temperature/drift and aggregate GPIO source current including other functions remain to be verified. The nominal resistance lower limit for that initial-tolerance, 2 mA-per-branch screen is 1.75 kΩ; 1.8 kΩ is the next proposed standard value. The model is not a full-system worst-case guarantee.

Each output sources this small branch current; no separate LED driver is proposed. GPIO drive-strength settings specify output behavior, not a regulated LED current. Start with low outputs before enabling them. Reversed/open LEDs will not indicate normally; a shorted LED retains its series resistor. A short bypassing the resistor is not covered by this model. Neither PWM nor a software default establishes brownout/reset electrical qualification.

## Hand assembly and alternatives screened

Vishay's drawing gives maximum lead dimensions of 0.70 × 0.55 mm, a calculated 0.890 mm diagonal. A proposed 1.00 mm nominal finished hole with assumed ±0.05 mm tolerance leaves about **0.060 mm diametral clearance**. This is a small calculated fit allowance, not an insertion pass; retain it as a footprint/fabricator check. Use 2.54 mm lead pitch, pads at least 1.8 mm across, explicit A/K markings, and solder-tip access. No larger-hole exception is requested. Do not assume a generic LED library footprint has the correct pin polarity.

Kingbright WP710A10LID was screened but not recommended under the unchanged hole rule: its retained drawing permits a square lead side up to 0.75 mm, whose 1.061 mm diagonal exceeds a 1.00 mm hole. Its recommended 0.9 mm PCB holes do not resolve that worst-tolerance conflict. Vishay's rectangular-lead drawing provides a more usable fit screen here. The earlier L-7104LID source download could not be validated because of a TLS error and is not used as design evidence.

The resistor reuses the MRS25 family already reviewed for UART candidates: proposed 10.16 mm mounting pitch, ≥1.8 mm pads, with maximum lead diameter and final insertion still open. Keep LEDs sufficiently raised to meet the manufacturer's soldering conditions and avoid stressing the body. Final visible placement, solder clearance and populated module access remain layout work.

## Sourcing and decision

Dated distributor search results on 2026-10-16 show TLLR4401 at €0.48 each and the resistor at €0.09 each, quantity-one prices excluding VAT. Five of each calculate to **€2.85 excluding VAT**, or **€3.42 assuming 20% VAT**, before delivery. These are indexed sourcing indications, not a live checkout quote; the direct LED page could not be fetched. Sources: [LED listing](https://www.digikey.fr/en/products/detail/vishay-semiconductor-opto-division/TLLR4401/4074717), [resistor listing](https://www.digikey.fr/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS25000C1801FCT00/7350486).

Manufacturer exact-code active/preferred declarations, actual visibility and footprint fit remain incomplete. No known obsolete code is recommended. The [candidate table](../hardware/carrier-support-candidates.csv) and [calculations](../hardware/review/carrier-integration-calculations.csv) preserve the scope. Owner approval covers this indicator function only: five LEDs and five resistors are now in two provisional BOM rows. The socket shortlist remains unselected. No hardware was energized.
