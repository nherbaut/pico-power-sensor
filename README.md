# PicoPower hand-soldered prototype

Two prototype boards for measuring voltage, current, power and energy consumed by a Raspberry Pi during AI tasks. This is the **proto branch**, with its own hand-solderable design and project history.

The interposer carries bench-supply protection and a 5 mΩ shunt. A separately USB-powered Pico carrier reads the INA228 monitor, logs measurements to microSD and drives programmable indicators.

## Current documentation

- [Requirements](docs/requirements.md) and [architecture](docs/architecture.md)
- [Bill of materials](hardware/bom.csv) and [purchase list](hardware/purchase-bom.csv)
- [Release checklist](hardware/release-checklist.csv)
- [Interposer layout](docs/interposer-layout.md) and [carrier layout](docs/carrier-layout.md)
- [Assembly and circuit explanation](docs/how-it-works.md)
- [Project handoff](HANDOFF.md) and [working instructions](AGENTS.md)

The hardware is **not released for fabrication or connection to a Pi**. Calculated values and automated checks are not bench measurements. The BOM sourcing review requested on 2026-11-02 and selection of a 32 GB measurement-storage card are in progress; no parts have been purchased, as confirmed by the owner.

## Website

GitHub Pages publishes this branch. The workflow always checks out `proto`, including manual runs. Documentation and CSV tables are generated from this branch's source files; linked design files and evidence are available as downloads.

Run `make site-check BASE_URL=https://nherbaut.github.io/pico-power-sensor/` to build the site and check internal links. Hugo is required. Run `make site-serve` for a local preview.

## Hardware editing

Follow the regeneration instructions in [HANDOFF.md](HANDOFF.md). Hardware generators live in `hardware/kicad/`; the website build never regenerates or changes the CAD.
