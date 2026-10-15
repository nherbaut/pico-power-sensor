# Prototype assembly and sourcing

Use a common comparison request of **two assembled interposers and two assembled carriers**, with one working instrument as the immediate goal and the second pair as spares. Also compare one assembled unit per design where the service allows it. Extra bare boards required by an order minimum must be counted. Target EUR 100–200 delivered to France including VAT, assembly, parts, setup/stencils and shipping; owned equipment is excluded. No actual quote has been obtained and the target is not guaranteed.

## Assembly split

For a JLCPCB price with factory placement, see the [quote package](jlcpcb-quote.md).

The generated [assembly review CSV](../hardware/assembly-review.csv) is a local planning list, **not an order-ready BOM/CPL**. Every physical circuit component is classified. Factory placement covers resistors, capacitors, LEDs, ICs, shunt, MOSFETs and the microSD socket. Manual assembly covers the power connector, fuse holder, long-tail header, JST connectors (including the carrier's J_SENSE) and two Pico socket strips. Insert the fuse, Pico and card only at the appropriate assembly stage. Bare test pads and mounting holes require no purchased component.

J_PICO is a combined logical footprint. It must not be ordered as a factory-soldered Pico module. Its two socket strips are listed separately. J2 is one physical stacking socket; the schematic's logical HAT-side J5 is not a second component. Preserve these distinctions when preparing an eventual BOM/CPL.

All MPNs are prototype selections requiring final technical and sourcing review. Do not approve a substitution by package size alone: maintain divider accuracy/TCR, shunt Kelvin geometry, MOSFET SOA/pinout, power-off buffer behavior, regulator pinout and capacitor effective values. Assembly-house generic passives can reduce fees, but must be explicitly reviewed and synchronized before release.

## Provider comparison

Public service information checked 2026-10-14. No design uploaded, supplier contacted or order placed.

| Provider | Relevant capability | What the eventual quote must settle |
|---|---|---|
| [JLCPCB](https://cart.jlcpcb.com/quote/) | BOM/CPL assembly workflow; economic and standard services; extended-part setup costs can matter for many distinct MPNs | Support for interposer 70 µm finished outer copper with chosen assembly service; exact component stock/fees; imported parts; freight and VAT |
| [Eurocircuits](https://www.eurocircuits.com/services/pcb-assembly-capabilities/) | Prototypes from one piece, SMT/THT, own-board assembly, sourced or eligible customer-supplied parts | 70 µm finished copper, border requirements, exact MPN availability and total for both designs; production facilities in [Germany/Hungary](https://www.eurocircuits.com/services/) |
| [AISLER](https://aisler.net/de/products/assembly) | European prototype assembly, native-CAD import and distributor sourcing | Confirm required copper stackup, component availability, treatment of combined Pico socket footprint, total delivered price |

JLCPCB is the first budget candidate, Eurocircuits/AISLER the European comparisons. There is no verified price ranking without design-specific quotes. Do not downgrade interposer copper to a cheaper default or silently substitute extended parts. Public bare-board promotional prices are not estimates for this assembled project.

## Fabrication specification to retain

- Interposer: 67.13 × 46 mm maximum outline, two layers, 1.6 mm FR4, **70 µm finished copper on each side**.
- Carrier: 66 × 54 mm, two layers, 1.6 mm FR4, **35 µm finished copper on each side**.
- Lead-free reflow for SMT; through-hole connectors fitted afterward. Ask the assembler to confirm surface finish, stencil thickness/apertures, soldermask registration, copper/clearance capability and any panel tooling before release. Connector seating must not be obstructed by solder fillets.
- Supplier panel rails/fiducials/tooling must be outside the reviewed finished outline. No ad-hoc holes or geometry changes in the header or antenna keepouts.
- Use local CAD BOM and footprint positions to prepare final files only after review. Confirm rotations and pin 1 in assembly previews; a centroid file alone does not establish orientation.

## Mechanical parts to obtain first

| Item | Quantity per instrument | Status |
|---|---:|---|
| Samtec SSQ-120-03-G-D | 1 | Existing stacking candidate; generic owned connectors are preliminary aids |
| Samtec SSW-120-01-G-S | 2 | Selected Pico socket strips; drawing/seating review pending |
| TI INA229AIDGSR | 1 | Soldered on the carrier (VSSOP-10); footprint and availability review pending |
| M2.5 spacers/screws and side-wing support | Fit-dependent | Determine exact heights with rigid 1.6 mm mock-up; do not reuse 16 mm HAT spacers by assumption |

Use the existing Pi/cooler/HAT hardware. No new scope, load or DUT supply is required: fablab access is confirmed. Procurement remains empty until actual purchases/receipts occur.
