# Power-monitor module comparison

Date: 2026-10-15. Status: initial shortlist, followed by the owner's choice to qualify MikroE I2C first. No component has received final selection approval and no purchase is authorized. This comparison follows the approved architecture: external Kelvin shunt on the interposer, independently powered monitor on the carrier. The owner's I2C decision supersedes the initial SPI preference. Current findings are in the [qualification report](mikroe-4810-qualification.md); comparison observations below retain their stated evidence scope.

## Options and recommendation

| Module | Interface | External-shunt suitability | Indicative module price | Assessment |
|---|---|---|---|---|
| MikroE Power Monitor Click, MIKROE-4810 | I2C, INA228 | Schematic v100 exposes IN+/IN− and a separate VBUS/GND terminal pair, without an onboard shunt | EUR 26.34 including VAT, excluding shipping, in the retrieved DigiKey France search snapshot | Owner chose qualification first; final selection remains conditional on sourcing, physical interface review and electrical/accuracy findings |
| Texas Instruments INA229EVM, SENS064 | SPI, INA229 | External shunt explicitly supported; R1 is not fitted in the guide's BOM | EUR 74.39 including VAT, excluding shipping, in the retrieved DigiKey France English search snapshot | SPI alternative; factory-fitted 2 mm connectors need an appropriate harness/adapter and mechanical review |
| Adafruit 5832 | I2C, INA228 | Includes a 15 mΩ shunt; cannot connect its inputs across a remote shunt unchanged | USD 14.95 before shipping/taxes on manufacturer's page | Excluded from the current remote-shunt architecture without module rework or an approved architecture change |

Manufacturer documentation: [MikroE product](https://www.mikroe.com/power-monitor-click), [MikroE schematic v100](https://download.mikroe.com/documents/add-on-boards/click/power_monitor_click/Power_Monitor_click_v100_Schematic.PDF), [TI evaluation-board guide SBOU241E](https://www.ti.com/lit/ug/sbou241e/sbou241e.pdf), and [Adafruit 5832](https://www.adafruit.com/product/5832). Cost snapshots: [MIKROE-4810 at DigiKey France](https://www.digikey.fr/fr/products/detail/mikroelektronika/MIKROE-4810/16182543) and [INA229EVM at DigiKey France](https://www.digikey.fr/en/products/detail/texas-instruments/INA229EVM/13636647).

The MikroE direct shop reports no stock; the retrieved distributor snapshot reports two modules. The TI distributor snapshot reports fifteen. These are retrieved catalogue/search-index observations, not reserved inventory or live quotations. Direct retrieval of those DigiKey pages failed in this session, so reconfirm regional price, taxes, shipping, stock and exact revision before procurement. No budget has been assumed; the owner has been asked for a module budget.

The recommendation is to qualify the MikroE route first, not to select an unresolved component. Neither candidate is currently schematic-ready. TI's higher price buys an SPI evaluation-board implementation, not demonstrated improvement in this instrument's energy accuracy.

## Assembly, pinout and included circuitry

The following maps are documentary interface references. No footprint or harness is approved. Confirm physical orientation, mating part, pitch, drill/pad sizes, complete module envelope and all pins before capture. The custom PCBs must retain the permitted through-hole assembly families; a factory-fitted module connector does not authorize adding an unsuitable connector to the carrier.

### MIKROE-4810

The manufacturer specifies a 42.9 × 25.4 mm module. It can be considered for the inherited 78 × 54 mm carrier, but the bounding dimensions do not prove fit alongside the Pico, storage, connectors and antenna keepout. The vendor CAD archive is retained for subsequent footprint review; no outline or header positions have been changed.

The manufacturer's numbered mikroBUS table maps 7 to 3.3 V, 8/9 to ground, 10 to 5 V, 11 to SDA, 12 to SCL and 15 to ALERT; the remaining positions are NC. This is a logical map, not a verified top/bottom footprint drawing. Operate from the instrument 3.3 V domain; confirm the delivered supply selection and address settings without requiring fine-pitch rework.

Schematic v100 includes the monitor, 100 nF bypass, 4.7 kΩ SDA/SCL pull-ups, 10 kΩ ALERT pull-up and a power LED with 470 Ω resistor. All use module VCC. Do not duplicate these parts automatically on the carrier. The IN1 terminals are labelled IN+ and IN−; IN2 is VBUS and GND. The schematic was inspected as a rendered image; terminal orientation still needs corroboration against the module/CAD.

One sourcing issue remains: v100 names INA228AIDGST, whereas TI's downloaded April 2026 package addendum lists active INA228AIDGSR variants. A separately retrieved TI March 2026 addendum identifies the GST ordering code as obsolete. The family remains active, but this is not proof of the exact component now assembled by MikroE. Obtain current assembly/BOM evidence resolving that difference before selecting the module; do not silently substitute a bare chip or accept an obsolete ordering code. References: [current TI INA228 page](https://www.ti.com/product/INA228) and [TI addendum retrieved with the GST status](https://www.ti.com/lit/ds/symlink/ina228.pdf?ts=1730351667289).

### INA229EVM

Guide SBOU241E, sections 4.2.3 and 5.3.2, supports external shunts and custom controllers. The inference for this project is direct Pico control, without the TI-SCB or Windows GUI. Keep load current on the interposer; use the EVM for sensing only.

Figure 6-3 maps J1: 1 GND, 2 VBUS, 3/4 IN−, 5/6 IN+. J3 maps 2 to +5 V, 4 GND, 6 +3.3 V, 3 SCLK, 5 MOSI, 7 MISO and 8 ALERT. Chip select is switch-routed; choosing SW1 position 1 routes it to PQ1/J3 pin 1. Verify the supplied revision and switch setting before wiring; leave unused supply pins disconnected.

The guide shows onboard bypassing, indicator branches, an ALERT pull-up and digital series links; do not duplicate them blindly. Its BOM identifies J2/J3 as 2 mm connectors and R1 as quantity zero. The rendered schematic was inspected; mechanical qualification and carrier-side connection remain open. The active INA229AIDGSR is listed in the downloaded device addendum. The EVM body size is not qualified in this comparison.

### Adafruit 5832

Its factory-fitted shunt creates a conductive path between the measurement inputs. Connecting those inputs to the external Kelvin pair would place that shunt in parallel with the intended sense element. Simply bridging it would short the sense signal. Removing it requires module rework, which is not part of the proposed assembly process. Moving the whole module and high-current path to the interposer would be a distinct architecture option requiring review; it is not selected here.

## Shunt feasibility and measurement limits

Through-hole four-terminal shunts exist at 5 mΩ. Examples for further review are the [Ohmite CS3FR005E](https://www.ohmite.com/res-cs3/) and [Isabellenhütte PBV](https://www.isabellenhuette.com/hubfs/Files/Data-sheets/PBV.pdf) family. This establishes a sourcing direction, not a selected shunt or an assembly pass. The Bourns PWR4412-2S search candidate is excluded because the [manufacturer sheet marks the series obsolete](https://www.bourns.com/docs/technical-documents/obsolete-parts/pwr4412-2s_obsolete.pdf).

PBV's February 2026 sheet lists R005 with 0.5% and 1% tolerance (page 3). Its page-2 drawing shows four flat leads labelled I/U/U/I, with dimensions incompatible with treating them as round leads fitting the current 0.8–1.0 mm drill rule. Do not assign a footprint or increase drills/introduce slots silently. CS3's lead fit remains unverified: the official download route returned HTML rather than a usable PDF. These candidates therefore do not yet close the hand-soldering or footprint requirements.

At the reference 5 mΩ and proposed 5 A, calculated shunt voltage is I × R = 25 mV and dissipation is I² × R = 0.125 W. Those are nominal calculations, excluding tolerance, temperature drift and lead/contact losses; no physical measurement is claimed. They are compatible in magnitude with the INA228/INA229 selectable ±40.96 mV range, but headroom, current peaks and calibration still require review.

TI's [INA228 SLYS021A](https://www.ti.com/lit/gpn/INA228) and [INA229 SLYS023A](https://www.ti.com/lit/gpn/INA229), electrical-characteristics sections, specify energy error at full-scale conditions. That is not an approximately 1% guarantee over our undefined workload/current range. The final budget must include sensor error, shunt tolerance and drift, voltage-reference/return loss, header loss, conversion timing and integration/calibration error.

Both monitors measure bus voltage relative to device ground. The device specifications permit monitored analog voltage with the device supply off; this does not qualify the entire module, GPIO interface or cable fault behavior. Complete the architecture's reference and power-state checks before connecting the Pi. All indicators and digital pull-ups must use instrument power.

## Evidence and next decision

Primary PDFs and the vendor CAD archive used in this comparison are retained under `hardware/evidence/power-monitor/`, with URLs, revisions, hashes and inspection scope in `sources.csv`. The [candidate table](../hardware/module-candidates.csv) is not an approved BOM. The owner previously reported no prototype parts bought or selected; no inventory account or order history was accessed.

The KiCad skill's linked online-research helper was not installed locally, and its GitHub/raw URL returned 404. Research used the available web tool and direct public manufacturer downloads. PDF magic, readable page counts and text extraction were checked before evidence retention; only the stated schematic/dimension pages received visual inspection. No chart values were estimated. No footprint, electrical error budget, ERC, DRC, parity or bench pass is claimed.

Owner decision received: qualify MikroE I2C first. The qualification work is recorded separately; neither candidate is an approved BOM entry. Resolve eligibility gaps before presenting a final module selection and moving on to the shunt. No CAD changes, procurement or hardware activation are authorized by this comparison.
