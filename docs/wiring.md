# Wiring

## DUT power

With the Korad output disabled, connect red + to J1 pin 1 and black - to J1 pin 2. The green earth terminal is not the DC negative output. The mating plug is wired once, polarity-checked and secured with its flange screws. Do not connect another Pi power source.

Normal supply setting is 5.10 V with a maximum 5.00 A current limit. Verify the actual voltage and polarity with a multimeter; confirm the completed harness remains in constant-voltage operation during workload peaks. The protection circuit does not make arbitrary supply settings safe until physically validated.

J2 routes its 5 V power to physical pins 2 and 4 and ground to pins 6, 9, 14, 20, 25, 30, 34 and 39. Every other pin is passed through individually. Do not confuse physical pin numbering with BCM GPIO numbers.

## Power indicator

D1 (green, marked POWER) is fed from the protected supply before the shunt through R9 (2.7 kOhm). It shows that voltage is present after the fuse/protection circuit. Its approximately 1 mA current is outside DUT measurements. It does not confirm Pi boot or exact Pi-side voltage, and an extinguished LED is not proof that all rails are discharged or that another connected device cannot back-power the Pi.

## J3: INA229EVM sense cable

| J3 pin | Signal | EVM destination |
|---|---|---|
| 1 | SENSE_PLUS | J1 pin 5 or 6, IN+ |
| 2 | SENSE_MINUS | J1 pin 3 or 4, IN- |
| 3 | PI_5V / VBUS | J1 pin 2, VBUS |
| 4 | GND | J1 pin 1, GND |

The EVM's R1 shunt remains unpopulated. Use a short twisted sense pair. Never pass the Pi load current through the sense connector or EVM. The measurement inputs are analog connections; do not connect them to Pico GPIOs.

## J4: buffered daemon communication

J4 is now a five-pin JST-XH B5B-XH-A header with an XHP-5 housing. This replaces the earlier four-pin UART connector and prevents mating with the four-pin measurement cable. Existing four-pin UART harnesses are incompatible; never force or partially mate them. Use 3.3 V logic and a short five-wire harness. Pin numbering follows the footprint/datasheet; verify continuity rather than relying on cable colors.

| J4 pin | Signal | Pico destination |
|---|---|---|
| 1 | GND | GND |
| 2 | PICO_RX, buffered Pi TX (BCM14 / physical 8) | GP1 / UART0 RX |
| 3 | PICO_TX, buffered to Pi RX (BCM15 / physical 10) | GP0 / UART0 TX |
| 4 | PICO_MARK, buffered Pi marker (BCM17 / physical 11) | GP2 input |
| 5 | PICO_3V3, buffer A-side supply only | 3V3 OUT, physical pin 36 |

Pin 5 carries Pico 3.3 V **to the interposer**; it is not a Pi supply output. Never connect it to Pico VBUS/VSYS or 5 V. PICO_3V3 and PI_3V3 are separate nets sharing ground. The marker is driven by the Pi; the Pico never drives it. Verify HAT use of these GPIOs.

U2 (SN74AXC4T245PWR) provides fixed-direction buffering. Bank 1 carries Pi TX and marker to the Pico; bank 2 carries Pico TX to the Pi. C3/C4 decouple the separate supplies. Local 100 kOhm pull-ups keep UART signals idle-high on each domain, and pull-downs keep the marker idle-low when outputs disconnect. TI specifies disabled/high-impedance outputs when either supply is below 100 mV, plus partial-power-down support. This is shared-ground signal isolation, not galvanic isolation or a guarantee throughout every brownout voltage.

The cable is intended to remain connected during power cycling **after physical validation**. Power-off means the relevant 3.3 V rail is actually off; Linux shutdown alone need not remove it. Capture rail decay and signals on a scope, including both startup orders. Communication during a rail transition is invalid; discard transition marker edges. No firmware enforcing this policy exists yet. Until the electrical acceptance procedure has passed, do not rely on the circuit to prevent back-powering a Pi.

U2's Pi-side current, R10/R11 pull-ups and R14 pull-down load are included in DUT current. Measure their static and switching overhead; do not subtract an assumed constant. Configure the Pi 5 UART on the intended header pins and disable serial console/debug output; do not assume `/dev/serial0` maps identically across Pi versions. Initial link test: 115200 baud, 8N1.

Source: [TI buffer datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf).

## Instrument power and SPI

Power the Pico through its own USB supply. Use Pico 3V3 and GND for the EVM's sensor supply, accounting for LED, pull-up, buffer and module loads within the Pico regulator budget. Raspberry Pi recommends keeping external 3V3 load below 300 mA; actual available current depends on the Pico and Wi-Fi activity. The EVM supply and Pico side of U2 are instrument loads, independently powered from the DUT. Never connect a TI controller/another supply at the same time as the Pico supply without reviewing power-source contention. Proposed SPI0: GP18 SCLK, GP19 MOSI, GP16 MISO, GP17 CS; GP3 for ALERT. Match the selected CS routing switch on the EVM to the wired header pin. Confirm the exact EVM header numbering and pin polarity from its schematic before connection.

## Pi 5 power capability

Once the entire source, connector and board path has been validated for 5 A, edit the EEPROM bootloader configuration with `sudo rpi-eeprom-config --edit` and set `PSU_MAX_CURRENT=5000`. Reboot. This declaration is not a capability upgrade or a substitute for validation.

Source: [Raspberry Pi bootloader power properties](https://www.raspberrypi.com/documentation/computers/configuration.html).

Power sources: [Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf), [INA229EVM guide](https://www.ti.com/lit/ug/sbou241e/sbou241e.pdf).

## Carrier indicators and interposer cable

The carrier specification reserves GP4, GP5, GP6, GP7 and GP8 for LED1-LED5 respectively (Pico physical pins 6, 7, 9, 10 and 11). Each active-high green LED has its own 1 kOhm series resistor and each GPIO has a 100 kOhm pull-down to ground for the reset state. Indicator current is supplied by the independent Pico USB power source, outside DUT measurements. Firmware roles and PWM remain programmable.

Carrier J_UART uses the same five-pin JST-XH B5B-XH-A header and pin numbering as interposer J4. Connect with a straight-through cable using XHP-5 housings at both ends: GND, PICO_RX, PICO_TX, PICO_MARK, PICO_3V3. Do not cross TX/RX in the cable; the board assignments already account for signal direction. Pin 5 powers the interposer buffer from the Pico, never the other way around. See the [carrier specification](pico-carrier.md) for its direct-plug EVM connection and indicator circuit. The routed carrier CAD is available in the [review package](../hardware/pcb/carrier/README.md); physical validation remains pending.

## Carrier microSD

The card slot uses independent SPI1: GP12/MISO (physical 16), GP13/CS (17), GP14/SCLK (19), GP15/MOSI (20). The INA229 remains on SPI0. A dedicated TLV75533PDBVR supplies SD_3V3 from the Pico's USB VBUS (physical 40); its enable follows Pico 3V3. Do not join SD_3V3 to PICO_3V3 or Pi power. Both instrument rails share ground. CMD/DAT0-DAT3 have 10 kOhm pull-ups to SD_3V3. The hinged socket has no card-detect switch.

The card is an instrument load, outside DUT measurements. Initialize/mount and flush/unmount belong to future firmware; do not remove a card during recording. Validate card-write power peaks, regulator temperature and acquisition buffering before relying on stored measurements. See the [carrier storage specification](pico-carrier.md).
