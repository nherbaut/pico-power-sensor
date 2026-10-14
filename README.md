# PicoPower

A reproducible instrument for measuring Raspberry Pi task energy and correlating power with runtime metrics across hardware and software configurations.

## The instrument

PicoPower is being designed to answer a practical question: how much energy does a Raspberry Pi need to complete a task, and how does that change with its software, Pi model, cooling and accelerator HAT?

The first design targets a **Raspberry Pi 5**, powered directly by the existing **Korad U202**. A custom interposer measures the Pi's supply current and voltage. A separate Pico 2 W carrier connects the INA229EVM sensor, talks to the Pi through a buffered UART cable, and provides Wi-Fi and a microSD slot for future measurement logging.

| Part | What it does |
|---|---|
| Korad U202 | Supplies the DUT at the planned 5.1 V setting |
| Pi interposer | Power entry, fuse, protection, four-terminal shunt and 40-pin HAT pass-through |
| INA229EVM | Measures shunt voltage and bus voltage through its analog sense connections |
| Pico carrier | Independent USB power, EVM SPI0 connection, five programmable LEDs, JST-XH UART/marker cable and microSD on SPI1 |
| Pi and HAT | The device under test, running the workload and reporting runtime metrics through a future daemon |

The Pi, HAT and Pi-powered peripherals form the measured load. Pico, sensor, card and carrier LEDs use independent instrument power. The Pi-powered side of the communication buffer is an explicitly included interface overhead; it must be characterized rather than silently subtracted. See the [measurement boundary](docs/architecture.md) and [wiring guide](docs/wiring.md).

## Hardware designs

### Pi power-and-sensing interposer

The interposer carries the fuse and 5 mOhm four-terminal shunt on an outward extension. Its protection circuit and power indicator draw current before the shunt. All 40 header pins pass through for HAT use; fit with the Pi 5 Active Cooler and both AI HAT versions still needs physical validation.

![Front PCB layout of the Pi power-and-sensing interposer](hardware/pcb/interposer/layout-front.png "Interposer front PCB drawing. Engineering draft; this is a CAD export, not a photograph of assembled hardware.")

[Interposer schematics, connections and review files](hardware/pcb/interposer/README.md).

### Pico instrument carrier

The carrier sockets a Pico 2 W and accepts the INA229EVM through a direct plug-in socket. Five green LEDs on GP4-GP8 can show firmware-defined status. Its five-pin JST-XH connector carries UART RX/TX, a workload marker, ground and the Pico-side buffer supply to the interposer.

The hinged microSD slot uses **SPI1 on GP12-GP15**, while the INA229 retains **SPI0 on GP16-GP19**. The card has a dedicated USB-fed 3.3 V regulator. Its power consumption stays outside DUT measurements. Recording requires future firmware with RAM buffering so card write stalls do not block acquisition.

![Front PCB layout of the Pico carrier with five LEDs, UART connector and microSD slot](hardware/pcb/carrier/layout-front.png "Carrier front PCB drawing, including the microSD slot and dedicated card regulator. Engineering draft; physical fit and electrical validation are pending.")

[Carrier electrical schematic and review files](hardware/pcb/carrier/README.md) · [Carrier pinout and power details](docs/pico-carrier.md).

## Planned experiment workflow

1. Describe the DUT hardware, software configuration and task in a test plan.
2. Record the idle baseline before the workload starts.
3. Send commands to the Pi daemon and capture workload markers and runtime metrics.
4. Acquire power samples throughout the task and correlate them with runtime events.
5. Store traces on the card and/or upload them, retaining timestamps and configuration identifiers.
6. Compare energy across configurations and train models from validated runs.

This software workflow is planned. Firmware, local recording, the Pi daemon, server ingestion and model training have not been implemented. Pi 3/4 and other Pi 5/HAT configurations are future campaign targets; the current mechanical design is a Pi 5 engineering draft.

## Current validation

Both custom boards have routed KiCad designs and saved reports showing zero ERC, DRC, unconnected-pad and schematic parity issues. These are automated CAD checks, not measurements of built hardware.

| Check | Interposer | Carrier |
|---|---|---|
| Schematic ERC | Passed in saved report | Passed in saved report |
| PCB DRC and schematic parity | Passed in saved report | Passed in saved report |
| Manufacturer footprint / connector fit review | Pending | Pending |
| Assembly, power and thermal bench validation | Not performed | Not performed |
| Calibration and measurement campaign | Not performed | Not performed |

**Engineering drafts — not released for manufacture or connection to a Pi.** Procurement and inventory tables are project records, separate from user-reported ownership of existing lab equipment.

## Navigation

| Need | Location |
|---|---|
| Circuit and editable PCB | [Interposer design](hardware/pcb/interposer/README.md) |
| Proposed hardware | [BOM](hardware/bom.csv) |
| Purchases and receipts | [Procurement](hardware/procurement.csv) |
| Installed and available parts | [Inventory](hardware/inventory.csv) |
| Hardware source documents | [Datasheets](hardware/datasheets/README.md) |
| Pico carrier engineering draft | [Connections and power](docs/pico-carrier.md), [KiCad and review files](hardware/pcb/carrier/README.md) |
| Instrument architecture | [Architecture](docs/architecture.md) |
| Power and signal connections | [Wiring](docs/wiring.md) |
| Build and first power-up | [Assembly](docs/assembly.md) |
| Measurement boundary and uncertainty | [Metrology](docs/calibration.md) |
| Mechanical compatibility | [Mechanical requirements](docs/mechanical.md) |
| Experiment workflow | [Test plans](docs/test-plans.md) |
| Documented choices | [Decisions](docs/decisions/README.md) |
| Instrument records | [Instruments](nodes/README.md) |
| Acceptance procedures | [Tests](tests/README.md) |
| Documentation website | [Website workflow](docs/website.md) |

## Working locally

```sh
make site-serve
make site-check
make hardware-images
make hardware-check
make hardware-export
make carrier-export
```

Open either board's `.kicad_pro` file in KiCad. `make hardware-images` refreshes PNGs from current CAD without regenerating or rerouting either board. Full board export targets refresh checked review packages. `make hardware-build` and `make carrier-build` regenerate their designs and overwrite manual CAD edits.

The site reuses NoiseNet's Hugo layout and Markdown/CSV publishing workflow, translated into English. The reference project is left untouched. The local site is served at `http://localhost:1313/`.

Firmware, daemon, ingestion and model training are subsequent implementation milestones; the directories presently document their intended responsibilities. The current work focuses on the custom PCB requested during the architecture discussion.

## Tracking conventions

Hardware IDs `HW-xxx` connect the proposed BOM, procurement, inventory and assembly records. Instrument IDs are `PP-xxx`; DUT IDs are independent of instruments. Every run records the actual Pi, HAT, cooling, software, plan and instrument calibration revisions.

CSV files are UTF-8 with comma delimiters and decimal points. Dates use `YYYY-MM-DD`. Empty fields mean unknown, not zero. BOM quantities describe one instrument; the owned Korad and Pi are recorded as user-reported equipment, not purchases or verified inventory. Do not publish secrets or private measurement campaigns.
