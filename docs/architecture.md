# Instrument architecture

The current hardware is a Pi 5 interposer plus a separately powered Pico 2 W carrier that carries the INA229 power monitor. Their [electrical schematics](../hardware/pcb/interposer/README.md) and [carrier drawings](../hardware/pcb/carrier/README.md) are engineering drafts. The execution and storage behavior described below is the intended software architecture; no firmware, Pi daemon or server has been implemented.

## Measurement boundary

The DUT includes the Pi, its HAT, cooling fan and all peripherals powered by the Pi. Separately powered peripherals must be declared. The Korad, fuse, upstream protection, shunt and external Pico/INA229 circuitry are outside the intended measurement boundary.

The Pi-powered side of the UART buffer and its bias network are an explicitly accepted interface load included in DUT current. The Pico-powered side stays outside that current measurement. Characterize interface overhead under idle and active traffic, retain raw total energy, and do not silently subtract a constant.

The interposer is a direct DC power path, not a voltage converter. The Korad supplies 5.1 V. Current is measured across the four-terminal shunt; voltage is sensed at the header power bus. Header-contact and return-path drops remain uncertainty until measured or a separate Pi-side sense pair is installed. Do not claim the local board sense point is identical to the Pi's internal rail.

## Responsibilities

| Component | Responsibility |
|---|---|
| Interposer | Secure power entry, fuse, protection, shunt, buffered UART/marker and 40-pin continuity |
| INA229 (carrier U_PM) | Voltage/current conversion; SPI interface |
| Pico carrier | INA229 and sense connector, five programmable LEDs, buffered UART/marker harness and independently powered microSD slot |
| Pico 2 W firmware (planned) | Monotonic sample timestamps, command sequencing, GPIO marker capture, buffered logging and Wi-Fi upload |
| Pi daemon | Commands, runtime metrics, configuration fingerprint and workload marker |
| Server | Plan management, persistent storage, alignment, profiles and predictive modelling |

The Pico and INA229 have independent instrument power. No TI evaluation board, TI-SCB or Windows driver is used; the Pico talks to the INA229 directly over SPI. UART carries commands and runtime metrics; power acquisition does not depend on the Pi daemon running.

The carrier's microSD slot uses SPI1 on GP12-GP15; INA229 communication uses SPI0 on GP4-GP7, with ALERT on GP3. A dedicated 3.3 V card regulator takes input from the independently powered Pico's USB VBUS. The card, regulator and GP27/26/22/21/20 indicator LEDs are instrument loads outside DUT current. See the [carrier specification](pico-carrier.md) for the five-pin JST-XH interface, power rails and pin numbering.

## Data workflow

In the planned workflow, the server validates a versioned test plan and hands the Pico a bounded sequence. The Pico runs setup, warm-up, idle baseline, task, cooldown and cleanup with the daemon. Power acquisition will run throughout those phases. Runtime metrics have a 10 Hz target and GPIO markers will establish daemon execution boundaries. The server will align clocks with an explicit uncertainty estimate, compute energy and train models.

Nominal acquisition target is 10 kHz using INA229 sequential bus/shunt conversions, no averaging and no die-temperature conversion in the fast sequence. Achieved sample rate, register coherence, conversion skew and bandwidth must be validated. This is not a simultaneous-sampling oscilloscope. Prediction uses 100 ms averages rather than claiming to resolve every transient from Linux metrics.

The first software milestone will use bounded RAM buffering and short, connected tests. The microSD hardware allows a future local logger, with an initial microSDHC/FAT32 target. Separate SPI buses avoid sharing sensor and storage wires, but acquisition still needs buffering and scheduling to tolerate card write stalls. Record sample sequence numbers, acquisition timestamps and configuration identifiers; report lost samples or storage errors and flush files before removing the card. Buffer overflow invalidates a run rather than silently producing a complete-looking trace.

PostgreSQL is the proposed store for run/configuration records and runtime metrics; checksummed files are proposed for raw power traces. The backend and model-training pipeline remain unimplemented. Whole runs will stay together during model evaluation.
