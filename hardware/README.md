# Hardware

The [BOM](bom.csv) represents a proposed instrument, not a purchase record. [Procurement](procurement.csv) and [inventory](inventory.csv) start empty. Sources and review obligations are recorded with each component.

The first instrument combines the [custom interposer](pcb/interposer/README.md), INA229EVM and a Pico 2 W on the [carrier](pcb/carrier/README.md). The carrier adds five GPIO-controlled indicators, a JST-XH interposer connection and a microSD slot with its own USB-fed regulator. The Korad U202 supplies the DUT at the planned 5.1 V setting through a direct DC path. The card regulator belongs to the separately powered instrument, outside DUT measurements.

The replaceable fuse and shunt are mounted on the interposer. Current is sensed with a dedicated Kelvin pair. An upstream electronic switch disconnects incorrectly connected or excessive input voltage; it does not regulate output voltage. Its low-resistance power path still introduces a small voltage drop that must be checked under load.

The [optional BOM](optional-bom.csv) contains shared bench equipment. Calibration equipment is not part of the finished instrument.
