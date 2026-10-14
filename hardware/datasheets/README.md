# Technical sources

Consult current manufacturer documentation before ordering or releasing footprints. Stock and prices are not design specifications. Sources reviewed on 2026-10-13:

| Part or subsystem | Primary source | Use |
|---|---|---|
| Raspberry Pi 5 | [Mechanical drawing](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf) | Approximate envelope; explicitly not production dimensions |
| AI HAT+ and AI HAT+ 2 | [Hardware assembly](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html) | Cooler, stacking header, heatsink and PCIe fit |
| Pi power capability | [Configuration](https://www.raspberrypi.com/documentation/computers/configuration.html) | EEPROM PSU_MAX_CURRENT declaration |
| Korad U202 | [Korad user manual, hosted by distributor](https://priniotakiselectronics.gr/image/KORAD/U202Englishusermanual.pdf) | 0-30 V, 0-5 A adjustable supply; terminal use |
| INA229 | [Datasheet](https://www.ti.com/lit/ds/symlink/ina229.pdf) | SPI, conversion timing, ranges, Kelvin layout |
| INA229 | [Datasheet](https://www.ti.com/lit/ds/symlink/ina229.pdf) (SLYS023A) | Pin map, VSSOP-10 land pattern example, input range and bias, layout guidance |
| Vishay WSK2512 | [Datasheet](https://www.vishay.com/docs/30108/wsk2512.pdf) | 5 mOhm part, tolerance, TCR, four-terminal layout |
| WSK 5-200 mOhm footprint | [KiCad library source](https://raw.githubusercontent.com/KiCad/kicad-footprints/master/Resistor_SMD.pretty/R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm.kicad_mod) | Current pads 1/4 and sense pads 2/3; geometry source |
| LTC4367 | [Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf) | Pin map, input switch, gate drive, threshold and reverse input behavior |
| Infineon BSC010N04LS6 | [Product and package](https://www.infineon.com/part/BSC010N04LS6) | 40 V MOSFET, 4.5 V gate resistance rating; footprint must be reviewed |
| Samtec SSQ | [Connector](https://www.samtec.com/products/ssq-120-03-g-d), [rating catalogue](https://suddendocs.samtec.com/catalog_english/ssw_th.pdf) | Header pitch, tail style and qualified test-pair rating |
| Phoenix input header | [1776508](https://www.phoenixcontact.com/en-us/products/pcb-header-mstb-25-2-gf-508-1776508) | Polarized power entry, flange dimensions and wire interface |
| Phoenix mating plug | [1777989](https://www.phoenixcontact.com/en-us/products/pcb-plug-mstb-25-2-stf-508-1777989) | Screw-flanged removable plug |
| Schurter OGN | [Datasheet](https://at.schurter.com/en/datasheet/typ_OGN.pdf) | Holder 0031.8201, power acceptance, cover and drill geometry |
| Green power LED | [Kingbright APT2012LZGCK datasheet](https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf) | Low-current green 0805 LED; polarity, dimensions and forward voltage |
| UART/marker buffer | [TI SN74AXC4T245 datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf) | PW/TSSOP-16 pinout, power-off behavior, leakage, direction and supply sequencing |
| JST XH | [Datasheet](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf) | Keyed low-current signal/sense connector and crimp system |

The board includes derived draft footprints, not manufacturer-certified land patterns. Review every package and its orientation before fabrication. The WSK coordinates were transcribed from KiCad's library source and must still be checked against the ordered part variant.
