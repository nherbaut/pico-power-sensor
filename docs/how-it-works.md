# How the instrument works

## Part 1: the carrier board

The carrier is the instrument's "brain". It sits on the bench next to the Pi, roughly 10–12 cm away, and is connected to the interposer by two cables. It never takes power from the Pi side.

### 1. Power

- The Pico 2 WH is powered by its own USB cable from a separate USB charger.
- The Pico's on-board regulator produces 3.3 V (Pico pin 36). That 3.3 V is the only supply on the carrier. It feeds the power-monitor module, the microSD module, the UART buffer chip and the pull-up resistors.
- The Pico's USB 5 V pins (VBUS, VSYS) are deliberately left unconnected, so the carrier can never feed or be fed by the Pi's 5 V.
- Ground is common to everything on the carrier. It meets the Pi's ground through the two cables, so that voltages on both boards share one reference.

Because the carrier runs only from its own USB supply, nothing it consumes appears in the measured Pi current.

### 2. Measuring the Pi: the power-monitor module

The MikroE Power Monitor Click (MIKROE-4810) carries a Texas Instruments INA228, a 20-bit measurement chip.

- **Current.** On the interposer, the Pi's whole supply current flows through a 5 mΩ resistor (the shunt). At 5 A it drops 25 mV. Two thin wires pick up the voltage at each end of the shunt (a "Kelvin" or four-wire connection), so the copper and solder joints carrying the 5 A are not included in the reading. Those two wires arrive on the 4-pin sense connector (J7). The INA228 measures the small voltage between them and converts it to current: current = voltage ÷ 0.005 Ω, refined later by calibration.
- **Voltage.** A third wire brings the 5 V present at the Pi's header pin 4 (VBUS). The INA228 measures it relative to ground.
- **Power and energy.** The INA228 multiplies voltage by current internally to give power. It also accumulates power over time into an energy register, so energy (joules or watt-hours) is counted continuously in hardware, independent of how fast the Pico reads it.
- **Filtering.** On the interposer, an 82 Ω resistor sits in each measurement wire. On the carrier, a 100 nF capacitor (C1) is connected across the two current wires. Together they filter out fast noise and limit current if a cable wire is shorted.
- **Connection to the module.** The module takes these signals on its own screw terminals, not on its header pins. The carrier therefore has three solder pads (J6), from which three short wires run to the module's terminals.
- **Talking to the Pico.** The Pico reads the INA228 over I²C: two wires, SDA on GP12 and SCL on GP13. A third line, ALERT on GP9, lets the INA228 signal "a new measurement is ready".

### 3. Talking to the Pi: serial link and task marker

The Pi needs to tell the instrument when a workload (an LLM prompt, an image classification) starts and stops. Energy can then be reported per task.

- **Task marker.** One Pi pin (GPIO23) goes high during a task. The Pico watches it on GP2 and records the energy counter at each edge. The difference between the two readings is the energy used by that task.
- **Serial link (UART).** Pi TX goes to Pico GP1 and Pico GP0 goes to Pi RX, so the Pi can send task names or commands and the Pico can reply.
- **Why a buffer chip (U1, SN74LV125AN).** The Pi and the Pico are powered separately and may be switched on and off at different times. Connecting their pins directly could push current into an unpowered chip. The buffer is powered by the carrier's 3.3 V and sits between the cable and the Pico. The Pico enables it through GP3, only once both sides are ready. A 10 kΩ resistor (R4) keeps the buffer off by default.
- **Protection resistors.** A 470 Ω resistor in each signal line limits current if a wire is shorted or the boards power up in the wrong order. Two 100 kΩ resistors (R2, R3) hold the Pi-driven lines low when the Pi is off, so the Pico does not see random noise.

### 4. Recording: the microSD module

The Adafruit 4682 microSD module plugs into the back of the carrier. The Pico writes to it over SPI: SPI1 with clock GP10, data out GP11, data in GP8, chip select GP7, plus card-detect on GP6. The firmware logs time-stamped voltage, current, power, energy and task markers to the card, so a long test does not depend on a connected computer. The Pico's Wi-Fi can also be used to send results.

### 5. Indicators: five LEDs

Five red LEDs (LED1–LED5) at the right edge are driven by Pico pins GP28, GP27, GP26, GP22 and GP21 (right-hand pin row), each through a 1.8 kΩ resistor that limits the current to about 1 mA. Their meaning is set in firmware, for example: powered, logging, task running, link OK, error.

### 6. Physical arrangement

- The Pico, the monitor module and the microSD module all plug into sockets, so a damaged module can be swapped without desoldering.
- The microSD module and the buffer chip U1 are on the back of the board; nothing sits under the monitor module. The carrier needs standoffs taller than the back-side parts.
- The two JST cable connectors are on the left edge, facing the interposer.

### 7. Typical measurement sequence (firmware, not yet written)

1. The Pico starts on USB power and keeps the buffer disabled.
2. It configures the INA228, checks the card, then enables the buffer and waits for a "hello" from the Pi.
3. The Pi runs a workload, raising the marker at the start and lowering it at the end.
4. At each marker edge, the Pico reads the INA228 energy counter and the time, and writes a line to the card.
5. Result per task: energy = counter at end − counter at start; duration; average power = energy ÷ duration.

The firmware does not exist yet, and accuracy (target about 1 %) still has to be established by calibration against reference instruments; see `docs/bench-tests.md`.
