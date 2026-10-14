# Project state and agent handoff

Snapshot: **2026-10-14**, after the electronic-protection study. Code/design baseline: commit `757351e` (`try reducing the circuit V drop`). The working tree was clean before adding this handoff document. This is a navigation and continuation note; the linked engineering records and release checklist remain authoritative. Update this note when the design direction changes.

## Read first

1. The repository-root `AGENTS.md` working instructions (local agent file, outside the website).
2. This document, then the [current prototype review](design-review.md).
3. [Electronic-protection study](electronic-protection.md) and its [independent review](../hardware/review/power-path-study-review.md).
4. [Release checklist](../hardware/release-checklist.csv): fabrication and Pi connection are separate gates, both incomplete.

The user has limited electronics knowledge. Explain decisions in plain French during the conversation; keep repository documentation and code identifiers in English. The current milestone is PCB design and documentation. Firmware, Pi daemon, ingestion server and model training are planned separately.

## Hardware and agreed constraints

- The owned Korad U202 supplies the DUT directly, with a planned 5.1 V setting and 5 A limit. Start with a Pi 5; later campaigns include Pi 3/4 and both AI HAT versions. Do not substitute a voltage-converter HAT or another supply.
- The interposer retains all 40 header pins, mounting holes and an outward component wing. Active Cooler and both AI HAT configurations require physical compatibility evidence.
- The 5 mΩ four-terminal shunt measures Pi/HAT current. Protection, instrument supplies and indicators belong outside DUT current. The Pi-powered UART buffer side is an explicitly included overhead. New sensing-input bias must also be identified and characterized.
- The independently USB-powered Pico 2 W carrier carries an INA229 power monitor (replacing the INA229EVM) with a four-pin JST-XH sense connector, five GPIO LEDs, five-pin JST-XH UART/marker/3V3 connection, and microSD on a separate SPI bus with a dedicated regulator.
- Ambient target: 10–40 °C. Prototype budget: EUR 100–200 for both boards and assembly, excluding owned equipment; this is not a quote. Factory SMT assembly, manual through-hole fittings.
- The user reports access to the fablab's scope, electronic load, meters and temperature equipment. No assembled-board electrical measurements have been performed. The paper mock-up stage is sufficient for preliminary placement, but rigid/populated fit remains pending.
- The user previously authorized overwriting CAD when needed; preserve deliberate design changes and check for open KiCad sessions before regeneration. No purchases, orders, publishing or hardware activation are authorized by this local design work.

## What exists and what is only a study

The main editable projects are [interposer](../hardware/pcb/interposer/README.md) and [carrier](../hardware/pcb/carrier/README.md). Both are routed engineering drafts with saved zero-violation ERC/DRC, zero unconnected pads and zero parity issues. These automated results do not prove electrical performance, exact footprint fit or release readiness.

Exact passive part selections and several footprint corrections are integrated into native CAD/BOM and generator paths. Generators and `circuit.json` underpin regeneration; inspect the documented workflow before changing either representation. Existing schematics still use generic component boxes and need conventional electrical symbols and a readability/pin-map review. `make hardware-build` and `make carrier-build` overwrite their projects; checking or viewing a design does not require either command.

The authoritative interposer **still contains** the removable 6.3 A cartridge fuse, holder, LTC4367 and two BSC010N04LS6 MOSFETs. It has no latched fault shutdown; automatic voltage-fault reconnection is possible and FAULT is unconnected. The current supervised policy is operator abort and supply cycling. The fuse is not guaranteed to clear a fault held at 5 A by the Korad.

The user explicitly agreed to **study** replacing the removable fuse with electronic protection. That authorizes the investigation, not fabrication or promotion of an incomplete circuit. No electronic replacement has been integrated into the authoritative CAD/BOM.

## Latest findings

| Result | Meaning and limit |
|---|---|
| Six-branch incumbent copper: 7.232 mΩ, 36.16 mV at 5 A | Approximate DC model including positive and ground return, not a measurement or hot bound |
| Existing mixed subtotal: 132.78 mV at 5 A | Supersedes the earlier partial 117.8/118 mV figure; contact/heating contributions remain missing; 100 mV target not demonstrated |
| Isolated two-face copper candidate: about 4.03 mV improvement | Native DRC/parity clean, but insufficient; candidate ZIP is for comparison and is not promoted or a fabrication package |
| Remove cartridge using existing-shunt detector and existing switches: 85.28 mV accounting subtotal | Preferred study direction; based on incumbent copper, not a prediction or guaranteed result for a new board |
| INA300 candidate with 1.43 kΩ threshold resistor: nominal 5.62 A, screening interval 5.41–5.83 A | Preliminary tolerance screen; temperature, power states and timing remain unqualified; a 5 A-limited short may not trip it |

The detector would observe the same Kelvin shunt pair as INA229 and command the existing power switches, avoiding another series resistance. Its independent Pico supply stays outside DUT current, while sense-input bias is explicitly tracked. Direct INA300 ALERT-to-LTC4367 SHDN has zero guaranteed low-level margin. A buffer is a candidate, not a closed interface. SHDN uses slow gate discharge; do not use the fast UV/OV timing as its shutdown time.

Latest local verification: **42 tests passed**, website built and internal links/assets passed, main CAD remained unchanged, and candidate ZIP/model/collision-report hashes agreed. The fresh independent review reproduced the incumbent copper and threshold arithmetic. Its two findings were corrected: stale copper evidence is rejected before export, and TPS25982 terminology is OVP. Review scope and exclusions are recorded explicitly; no physical measurements or circuit qualification resulted.

## Carrier change since this snapshot (2026-10-14)

The INA229EVM was removed. The carrier now carries an INA229AIDGSR (U_PM, VSSOP-10) with a 100 nF bypass, a 10 kOhm ALERT pull-up and a JST-XH four-pin sense connector (J_SENSE, same pinout as interposer J3), and it grew from 66 to 78 x 54 mm. Carrier ERC, DRC, parity and source checks pass; the fabrication gate is still open (new `sense-ic` row: INA229 footprint, Kelvin routing, cable mating). The earlier carrier paper mock-up no longer matches and must be redone. Regenerating the carrier with `make carrier-build` currently fails in the router, so the saved routed board is the source of truth (see the carrier README). The INA229 SPI uses GP4-GP7 and the five LEDs use GP27, GP26, GP22, GP21 and GP20, chosen to keep traces short. The protection-electronics direction was not touched; the INA300 candidate came from the earlier study and has not been selected by the user.

## Continue here

The next design task is to turn the electronic-protection study into a complete, reviewable circuit **before routing it**:

1. Define hardware arming, deliberate fault reset, detector-ready startup sequencing, and a brownout interlock. Loss of Pico power must disconnect the Pi, including transitions below the detector's valid supply range. A static power-off leakage calculation is insufficient.
2. Verify shutdown timing, gate loading and MOSFET safe operating area, startup/inrush, threshold errors, sensing-input behavior and both supply orders. Determine fault coverage after removing the passive fuse. Preserve the measured boundary and record all auxiliary bias.
3. Capture a conventional-symbol schematic, export and independently check the netlist, review it, then integrate the chosen topology into main CAD/BOM/generators and recompute the complete hot-device/copper/contact drop budget.

Other release work remains: exact-package footprint and connector reviews; rigid mechanical fit; copper/Kelvin routing review; stackup/DFM and manufacturing-package inspection; effective KiCad rule-severity audit. Carrier-specific open work includes microSD socket fit, effective capacitance, regulator thermal capability and SD/Pico power sequencing. Do not mistake existing green ERC/DRC reports for closure of these gates.

Only after the fabrication checklist is complete should a manufacturing package be released. A released assembled prototype then needs the [fablab dummy-load/fault/thermal tests](fablab-validation.md), carrier tests and calibration before Pi connection. No further paper photograph alone can close electrical or populated-height checks.

## Commands and source records

```sh
git status --short
make test
make release-check BOARD=interposer
make release-check BOARD=carrier
make release-check BOARD=interposer GATE=connection
make electronic-protection-study
make site-check
```

Release checks are expected to fail while open gates remain; never suppress findings to make them pass. `make electronic-protection-study` consumes the full copper report and rejects a stale main-PCB hash. After a relevant board change, regenerate that diagnostic explicitly with `make copper-screen`. Copper modelling requires the kicad-design solver plus numpy/scipy/shapely and KiCad's distribution Python; it is optional and separate from website generation. Candidate-building targets operate in scratch projects; do not confuse those outputs with the authoritative projects.

The snap Hugo executable needed this local workaround for the last successful website check:

```sh
make site-check BASE_URL=https://nherbaut.github.io/pico-power-sensor/ HUGO='/snap/core24/current/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 --library-path /snap/core24/current/usr/lib/x86_64-linux-gnu /snap/hugo/current/bin/hugo'
```

This builds locally; it does not publish. Website inputs are generated from repository Markdown/CSV; edit source documents rather than `.build/site` or `public`.

Detailed evidence: [hardware review index](../hardware/review/README.md), [full copper budget](../hardware/review/copper-loop-budget.csv), [electronic study JSON](../hardware/review/electronic-protection-study.json), [candidate binding](../hardware/review/power-path-candidate.json), [BOM](../hardware/bom.csv), [footprint review](../hardware/review/footprint-review.csv), [mechanical evidence](../tests/mechanical/paper-mockup-2026-10-14.md). Historical partial calculations remain in dated records; use the full-loop follow-up for current conclusions.
