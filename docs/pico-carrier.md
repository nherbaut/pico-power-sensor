# Pico carrier design specification

Status: routed KiCad 9 engineering draft; physical validation and fabrication release pending. See the [carrier CAD and review package](../hardware/pcb/carrier/README.md). The interposer UART buffer is implemented separately.

## Mechanical arrangement

The carrier holds the INA229 power monitor (U_PM, TI INA229AIDGSR, VSSOP-10) directly on the board; the INA229EVM is not used. The interposer's four-pin sense connector J3 is joined to the carrier's J_SENSE with a short straight-through XHP-4 cable. The previous EVM socket and its mating-number convention no longer exist. Verify the INA229 footprint against TI's DGS0010A land pattern and the J_SENSE footprint against the JST drawing before fabrication. The example photograph (`img/picoinamount.png`) shows the earlier EVM arrangement and no longer reflects this carrier.

Socket a headered Pico 2 W on two 20-pin, 2.54 mm female strips, leaving USB and BOOTSEL accessible. Position its antenna at the board edge with the copper/component keepout prescribed by the Pico 2 W datasheet. Keep LEDs, connectors and mounting hardware outside that keepout.

The two-layer PCB is 78 x 54 mm and 1.6 mm thick, with two 35 um copper layers and four 2.7 mm mounting holes for M2.5 hardware. Hole centers are (4,4), (74,4), (4,50), (74,50) mm from the top-left, each with a 6 mm copper keepout. Both boards are supported independently on a shared bench base. Provide cable strain relief; do not use J_SENSE or J_UART to bear cable loads. Label pin 1, Pico orientation and all external connectors.

## Interposer connector: J_UART

Fit a JST-XH B5B-XH-A(LF)(SN) five-pin, 2.50 mm vertical through-hole header on the carrier. Its numbering and nets match interposer J4 exactly. Use a straight-through five-wire cable with XHP-5 housings at both ends, five contacts per housing, and SXH-001T-P0.6 contacts with suitable 22 AWG wire. Verify pin numbering and continuity; cable colors are not a pinout.

| Carrier J_UART pin | Signal | Pico GPIO / physical pin | Interposer destination |
|---|---|---|---|
| 1 | GND | GND / 3 | J4 pin 1 |
| 2 | PICO_RX | GP1 / 2 | J4 pin 2, buffered Pi TX |
| 3 | PICO_TX | GP0 / 1 | J4 pin 3, buffered Pi RX |
| 4 | PICO_MARK | GP2 / 4 | J4 pin 4, buffered Pi marker |
| 5 | PICO_3V3 | 3V3 OUT / 36 | J4 pin 5, buffer A-side supply |

Pin 5 supplies 3.3 V **from the carrier to the interposer**. Never connect it to PI_3V3, VBUS or VSYS. The five-pin plug cannot mate normally with the interposer's four-pin analog sense connector. No additional UART buffer is required on the carrier; the interposer provides it.

## INA229 power monitor: U_PM and J_SENSE

| INA229 pin | Signal | Pico GPIO / physical pin or other connection |
|---|---|---|
| 1 | CS (active low) | GP5 / 7, 100 kOhm pull-up to PICO_3V3 |
| 2 | MOSI | GP7 / 10 |
| 3 | ALERT (open-drain, active low) | GP3 / 5, 10 kOhm pull-up to PICO_3V3 |
| 4 | MISO | GP4 / 6 |
| 5 | SCLK | GP6 / 9 |
| 6 | VS | PICO_3V3, 100 nF bypass (C_PM) at the pin |
| 7 | GND | GND |
| 8 | VBUS | SENSE_VBUS, from J_SENSE pin 3 |
| 9 | IN- | SENSE_MINUS, from J_SENSE pin 2 |
| 10 | IN+ | SENSE_PLUS, from J_SENSE pin 1 |

Pin numbering follows TI's INA229 datasheet (SLYS023A, table 5-1, DGS package). The INA229 supply range is 2.7 V to 5.5 V; its inputs accept 0 V to 85 V whether or not it is powered, and its input bias is 2.5 nA maximum. J_SENSE is a JST B4B-XH-A: 1 SENSE_PLUS, 2 SENSE_MINUS, 3 SENSE_VBUS, 4 GND, matching interposer J3 pin for pin. Never cross the cable. The four-pin housing cannot mate with the five-pin J_UART.

SENSE_VBUS, SENSE_MINUS and SENSE_PLUS are analog nets that reach only J_SENSE and U_PM. No Pi load current passes through the carrier. Keep the sense pair short and adjacent; its layout still needs review. ALERT is a 3.3 V open-drain signal: use an input with a pull-up (the carrier provides one).

## Five programmable indicators

Use five independent, low-current green Kingbright APT2012LZGCK 0805 LEDs, labelled LED1 through LED5. Their functions remain firmware programmable; do not hardwire labels such as network or test status.

| Indicator | GPIO | Pico physical pin | Series resistor | Reset pull-down |
|---|---|---|---|---|
| LED1 | GP27 | 32 | R_LED1, 1 kOhm | R_PD1, 100 kOhm |
| LED2 | GP26 | 31 | R_LED2, 1 kOhm | R_PD2, 100 kOhm |
| LED3 | GP22 | 29 | R_LED3, 1 kOhm | R_PD3, 100 kOhm |
| LED4 | GP21 | 27 | R_LED4, 1 kOhm | R_PD4, 100 kOhm |
| LED5 | GP20 | 26 | R_LED5, 1 kOhm | R_PD5, 100 kOhm |

Each branch is `GPIO -> 1 kOhm -> LED anode; LED cathode -> GND`, with a separate 100 kOhm pull-down from the GPIO to GND. Use 0805, 1%, 0.125 W resistors. GPIO high turns the LED on; low turns it off. PWM can control brightness. Firmware should initialize the output latch low before enabling output, and leave these pins configured for indicator use. The pull-downs define the reset state; they do not force an LED off if firmware explicitly drives high.

Kingbright specifies a typical 2.65 V forward voltage at 2 mA for APT2012LZGCK. Using that voltage with a 3.3 V GPIO and 1 kOhm gives a 0.65 mA reference calculation per LED, plus about 0.165 mA through the five pull-downs when all outputs are high. Because forward voltage depends on current, this is not a solved operating point or measured consumption. The resistor alone bounds each LED branch below 3.34 mA at an assumed 3.3 V GPIO and -1% resistor tolerance. Verify actual brightness/current and GPIO voltage on the bench. GP4-GP8 do not overlap UART, marker, SPI or ALERT. All indicator current belongs to the independently powered instrument, outside DUT measurements. See the [LED datasheet](https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf).

## Local measurement storage

J_SD is a Würth Elektronik 693072010801 hinged microSD socket on the lower-left of the carrier. Open its lid, insert the card and latch it; allow clearance above the lid and confirm access on the shared base. This socket has no card-detect switch. Card availability is checked by firmware initialization/mounting.

| microSD contact | SPI function | Pico GPIO / physical pin |
|---|---|---|
| 1 DAT2 | Unused; 10 kOhm pull-up | None |
| 2 DAT3 | Chip select | GP13 / 17 |
| 3 CMD | MOSI | GP15 / 20 |
| 4 VDD | SD_3V3 | Dedicated regulator |
| 5 CLK | Clock | GP14 / 19 |
| 6 VSS | Ground | Instrument GND |
| 7 DAT0 | MISO | GP12 / 16 |
| 8 DAT1 | Unused; 10 kOhm pull-up | None |

The card uses SPI1; the INA229 uses SPI0 on GP4-GP7. Five 10 kOhm resistors pull CMD and DAT0-DAT3 to SD_3V3. CLK has no pull-up. No 5 V level shifter is needed: both logic domains use 3.3 V. The four socket shell pads are grounded.

U_SD is a TLV75533PDBVR LDO: IN (pin 1) from Pico USB VBUS (physical 40), GND (2), EN (3) from PICO_3V3, NC (4), OUT (5) to SD_3V3. This reserves the Pico regulator output for the sensor/buffer rather than powering card write bursts through it. SD_3V3 and PICO_3V3 are separate rails sharing ground. VBUS is the USB supply, not VSYS (physical 39) or DUT power. Use an independent regulated 5 V USB supply; do not power the Pico from the DUT Pi's USB.

Fit 4.7 uF X7R/16 V input/output capacitors near the LDO, plus 22 uF X5R/16 V bulk (Samsung CL31A226KOHNNNE) and 100 nF near the slot. Select capacitor parts with adequate effective capacitance under DC bias; TI requires more than 0.47 uF effective at the regulator pins. The LDO's 500 mA rating does not establish the board's continuous thermal capability. At 5 V input and 3.3 V output, calculated dissipation is 0.34 W at 200 mA, excluding quiescent current. Validate the actual card's startup/write peaks, rail droop and LDO temperature with Wi-Fi and all five LEDs active; bulk capacitance is not a substitute for a stable supply.

Default storage target: microSDHC, 8-32 GB, FAT32. The hardware provides the slot and electrical interface; no recording firmware is implemented. Future firmware must initialize SPI1 at the card's prescribed startup speed, buffer acquisition separately from filesystem writes, retain acquisition timestamps/sample sequence/run configuration, report dropped samples or storage errors, and flush/close files before card removal or power-off. A separate SPI bus prevents sharing the INA229 wires; it does not by itself guarantee uninterrupted sampling during SD write stalls. No hot removal during recording.

Sources: [socket drawing](https://www.we-online.com/components/products/datasheet/693072010801.pdf), [LDO datasheet](https://www.ti.com/lit/gpn/TLV755P), [RP2350 GPIO functions](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), [SD pull-up requirements](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/sd_pullup_requirements.html).

## Power

Power the Pico through its own USB input. Its 3V3 output supplies the INA229, GPIO LEDs, the Pico side of the interposer buffer and the SD LDO enable, with shared ground. The card itself uses the separate USB-fed SD_3V3 regulator. Never join this rail to Pi 3V3 or supply the Pico from the measured Pi rail. Account for the INA229, pull-ups, carrier LEDs and buffer loads. Raspberry Pi recommends less than 300 mA of external 3V3 load, with available current depending on internal activity and supply conditions; validate operation during Wi-Fi bursts with all carrier LEDs on. The Pi side of the buffer remains an explicitly included measurement overhead.

Do not power the INA229 from any other source. Confirm sense wiring and rail stability before connection to a Pi.

## CAD and bench acceptance

The independent KiCad 9 project in `hardware/pcb/carrier` includes a schematic, routed board, local footprints, BOM, pinout and mounting/review drawings. Use `make carrier-build` to regenerate it (overwrites carrier hand edits), `make carrier-check`, `make carrier-erc`, `make carrier-drc`, and `make carrier-export` for review artifacts. Interposer CAD remains separate. Require clean ERC/DRC, schematic-to-PCB parity and no unconnected required nets. Verify socket orientation, LED polarity, antenna keepouts, mounting clearances and instrument/DUT supply separation.

On the bench, check continuity and voltage before fitting modules; test all five LEDs individually and together, reset behavior, PWM, SPI device identification, UART and marker communication, card write/read integrity, and both 3.3 V rails during simultaneous SD writes and Wi-Fi activity. Physical fit and electrical acceptance remain separate from automated CAD checks. No carrier firmware or hardware activation is included in this CAD milestone.

Sources: [Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf), [INA229 datasheet](https://www.ti.com/lit/ds/symlink/ina229.pdf), [JST-XH family drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf), [LED datasheet](https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf).
