# Carrier GPIO and remaining parts

Date: 2026-10-16. Status: documentary implementation plan within parts selection, not a schematic or release. The inherited 78 × 54 mm outline, mounting holes and Pico header centres remain unchanged. The [40-pin contract](../hardware/review/carrier-pico-pin-contract.csv) records every Pico header contact, including unused and power pins.

## GPIO allocation

| Function | Pico GPIO | Physical header pin | Peripheral / connection |
|---|---|---|---|
| UART transmit to Pi | GP0 | 1 | UART0 TX → SN74LV125AN pin 9 |
| UART receive from Pi | GP1 | 2 | UART0 RX ← buffer pin 3 |
| Task marker input | GP2 | 4 | SIO input / edge interrupt ← buffer pin 6 |
| Common UART enable | GP3 | 5 | SIO output → buffer pins 1, 4, 10; active low |
| Monitor SDA | GP12 | 16 | I2C0 SDA ↔ MikroE pin 11 |
| Monitor SCL | GP13 | 17 | I2C0 SCL → MikroE pin 12 |
| Monitor alert | GP9 | 12 | SIO input ← MikroE pin 15 |
| Programmable indicators 1–5 | GP28, GP27, GP26, GP22, GP21 | 34, 32, 31, 29, 27 | Five independent SIO outputs (LED1…LED5); moved from GP7–GP11 at the owner's request on 2026-10-17 so the LEDs sit next to the Pico pins that drive them |
| SD MISO | GP8 | 11 | SPI1 RX ← Adafruit pin 4 |
| SD chip select | GP7 | 10 | SIO output → Adafruit pin 6; active low (software CS) |
| SD clock | GP10 | 14 | SPI1 SCK → Adafruit pin 3 |
| SD MOSI | GP11 | 15 | SPI1 TX → Adafruit pin 5 |
| SD card detect | GP6 | 9 | SIO input ← Adafruit pin 9 |

This consumes **17 of the 26 exposed GPIOs**. GP4, GP5, GP14, GP15 and GP16–GP20 remain unused (after the 2026-10-17 owner-requested moves: LEDs to the right-hand pins, microSD to SPI1 and I2C0 to GP12/GP13 so each bus uses the Pico pins nearest its module): nine spare GPIOs. GP23–GP25 and GP29 are internal Pico wireless/board signals and are not assigned. UART receivers stay on digital pins, avoiding the analog-capable pin issue discussed in the [UART review](uart-interface-qualification.md). Optional PWM would share frequency settings between GP8/GP9 and GP10/GP11; independent on/off control does not have that restriction.

The map was cross-checked against the retained [Pico 2 W datasheet](../hardware/evidence/storage/pico-2-w-datasheet.pdf), Figures 2 and 4, and RP2350 GPIO function table 3. Storage pad functions were checked against the retained Adafruit Eagle schematic. This verifies documentary allocation and absence of duplicate GPIO assignments, not saved schematic connectivity or physical orientation. Pi-side GPIO numbers remain open pending the exact AI HAT and Pi UART configuration; Pico GPIO numbers are not Raspberry Pi GPIO numbers.

## Power and startup

Pico pin 36 supplies instrument 3.3 V under the existing conditional rail budget. Leave VBUS pin 40 and VSYS pin 39 unconnected to carrier power nets: the Pico receives its supply through its own USB connector. Do not feed either pin from the DUT. Leave RUN, 3V3_EN and ADC_VREF without external circuitry in this plan. AGND is reserved for a future analog function; ordinary carrier grounds use the seven digital GND contacts. No ADC input is used to measure the DUT directly.

Preload GP3 high before enabling its output, then establish idle-high GP0 UART TX before enabling the buffer. Follow the existing RP2350 A2 E9 input-handling rules for GP1/GP2 until driven; actual silicon revision remains unverified. Set SD CS high before configuring SPI, keep unused SD DAT1/DAT2 unconnected externally, and use the module's existing pull-ups. Card detect is low without a card and high with one in the reviewed module circuit; debounce before accepting it and do not infer safe hot removal from detect alone.

Configure GP12/GP13 for I2C0 with the existing module pull-ups; start at the previously proposed 100 kHz qualification setting. GP9 receives the module's pulled-up alert. Firmware must configure and check the INA228 alert function before interpreting edges as conversion-ready. Set the five indicator output latches low before enabling them. No firmware has been built or run, and no baud rate, final SPI frequency or complete startup waveform is qualified.

The existing allocation remains **235 mA**: 200 mA storage, 15 mA monitor, 10 mA indicators and 10 mA other/interface loads. It is an allocation, not a measured maximum. The owner-selected indicators fit the 10 mA allowance under the assumptions in their review; actual card transients and Pico/radio operating margin remain open. Do not add the interface allowance a second time.

## Remaining parts, with review priority

| Function | Concrete direction | Status / remaining work |
|---|---|---|
| Five indicators | Five Vishay TLLR4401 red LEDs, each with a Vishay MRS25000C1801FCT00 1.8 kΩ resistor | [Owner-approved prototype set](indicator-options.md); five of each code now in BOM, qualification partial |
| Removable Pico | Two Harwin M20-7822042, 20-position sockets | Shortlist only; exact Pico header variant and mating pair, lifecycle, fit and antenna clearance open |
| Removable MikroE module | Two Harwin M20-7820842, 8-position sockets | Shortlist only; module header plating/length, minimum engagement and populated stack open |
| Removable underside microSD module | One Harwin M20-7820942, 9-position socket | Shortlist only; male header choice, mating and underside clearance open |
| UART supports | Previously listed socket, eight resistors and local capacitor | Exact codes/quantities still require selection; the approved sense capacitor quantity does not include this separate bypass |
| Pico orderable module and headers | Required Pico 2 W; manufacturer also lists a variant with headers | Exact purchase variant and supplied headers not yet selected |
| Monitor module | MIKROE-4810 qualification direction retained | Supplied revision/header details and final selection still open |
| Storage power | Selected Adafruit module with instrument 3.3 V | Actual card, current/latency and whether additional bulk capacitance is needed remain open |
| Bench wiring and supports | Existing terminals and mechanical baseline retained | Wire/strain relief, standoffs and populated fit remain open |

The [remaining-parts CSV](../hardware/carrier-support-candidates.csv) distinguishes the owner-selected indicators from the unselected sockets. Harwin's current drawing explicitly lists the 8-position **42** finish; the older **M20-7820846** tin version was excluded after finding its manufacturer obsolescence notice. Do not substitute it because a distributor still lists stock.

## Socket drawing screen

The retained Harwin M20-782 drawing, revision 11 dated 03-Aug-2026, specifies 2.54 mm pitch, 8.50 ±0.15 mm above-board height, 3.00 ±0.25 mm tails and a 3.41 ±0.25 mm contact-point dimension. A contact point is not a qualified engagement-depth range. Actual mating male posts and body stops must still be checked. Its available-variant table includes the shortlisted codes; this is not a standalone exact-code lifecycle declaration.

Tail width is 0.65 ±0.05 mm and thickness 0.25 mm with the drawing's ±0.10 mm general tolerance. The calculated maximum diagonal is 0.783 mm. Proposed 1.00 mm finished holes with an assumed ±0.05 mm tolerance leave 0.167 mm diametral clearance, within the project's nominal hole range. This differs from Harwin's recommended 1.02 ±0.05 mm hole and requires footprint/insertion/fabricator review. Use at least 1.8 mm pads. No hole exception or footprint has been adopted.

Five sockets alone do not complete the two-sided stack. The [module capacity study](carrier-module-fit.md) remains a planar envelope check; do not subtract nominal socket heights and call it a populated clearance pass. Review module underside protrusions, solder tails, extraction access and supports together with the male headers. No layout or schematic-stage approval is implied by this GPIO plan.

## Socket load and assembly follow-up

The retained [Harwin C00120 specification](../hardware/evidence/carrier/harwin-c00120-2022-11.pdf), November 2022, gives 20 mΩ maximum initial contact resistance and 30 mΩ after conditioning. These family ratings do not qualify an unknown mating module header. In a deliberately conservative one-source-contact/one-return-contact model, the 235 mA carrier allocation would give 14.1 mV across two 30 mΩ contacts. A separate 200 mA SD supply/return pair would add 12 mV; neither calculation includes copper, module joints or other connections, and neither is a measured drop. Do not interpret these carrier sockets as a new 5 A DUT connector.

For the M20-782 family the same document specifies up to 2 N insertion force per contact and at least 0.3 N withdrawal force per contact. Simple sums give 80 N insertion / 12 N withdrawal for the Pico's 40 contacts, 32 N / 4.8 N for the monitor's 16 contacts, and 18 N / 2.7 N for storage's nine contacts. These are sums of contact ratings, not measured module forces or predictions of simultaneous engagement. Support the carrier during insertion and provide access to remove modules without loading their solder joints; mounting and extraction ergonomics remain to be reviewed.

The specification does not supply a numerical insertion-depth range for the actual module mating pairs. The current manufacturer page for [M20-9992045](https://www.harwin.com/products/M20-9992045) identifies a possible 20-position, 6.1 mm-post male header for a headerless Pico, but its drawing/tolerance/fit review is not complete and it is not selected. For the nine-position storage header, a product compliance declaration alone does not resolve lifecycle or mating details. Keep the supplied Adafruit header and MikroE factory headers as unverified mating parts until their actual dimensions/plating are established. No module header removal, replacement or new assembly tool is prescribed by this review.
