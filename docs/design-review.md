# Prototype design review

This review implements the selected prototype components and documents the remaining engineering limits. It is **not a fabrication release**. The main KiCad projects are authoritative; earlier candidate archives are historical.

## Agreed requirements

- Indoor bench use: 10–40 °C ambient. Component temperatures are higher and need separate limits and measurements.
- EUR 100–200 target for both prototype boards and assembly, excluding owned equipment. This is a budget, not a supplier quote.
- Factory SMT assembly; manual through-hole connectors, fuse insertion, socketed modules and mechanical hardware.
- Retain the Korad U202, direct Pi power, 40-pin pass-through, and upstream protection/indicator supplies. Pi-side UART buffer consumption remains explicitly included in DUT consumption.
- Operator stops and invalidates the experiment after a detected fault and power-cycles the DUT supply. **The present circuit has no latched fault shutdown.** Automatic reconnection can occur; unattended fault handling is not implemented.
- User reports owning Pi 3/4/5, both AI HAT versions, cooler, generic stacking connectors, Pico 1 and Pico 2 W. The INA229EVM is no longer used. Access to the fablab's scope, load, meters and temperature equipment is confirmed; none of the electrical checks has been performed.

## Component changes applied

All 20 passive selection groups now have exact references in the [BOM](../hardware/bom.csv), native circuit descriptions, schematic MPN properties and board BOMs. [The selection register](../hardware/passive-proposals.csv) retains its filename for existing links; its statuses distinguish prototype selection from approval.

The precision divider uses Vishay TNPW0805, 0.1%, 25 ppm/K. R2–R4 now use the manufacturer's IPC reflow copper lands: 0.90 × 1.45 mm, 1.00 mm gap. This is dimensional evidence, not solder-joint qualification. [Vishay land recommendations](https://www.vishay.com/docs/28950/recsoldpaddims-drabeyresfus.pdf).

Selected Murata GRM21 capacitors now use 0.60 × 1.25 mm lands with a 1.20 mm gap, matching the reference sheet's reflow recommendation for the 2.0 × 1.25 mm body. Interposer C2 is explicitly 100 V instead of the former 63 V minimum. C1 now uses KEMET density-B reflow lands: 1.15 × 1.45 mm, centres at ±0.90 mm, courtyard 3.50 × 2.00 mm. The manufacturer drawing was visually inspected; mask/paste process qualification remains open. [KEMET C1003, 2025-02-20, p. 12, table 3](https://content.kemet.com/datasheets/KEM_C1003_C0G_SMD.pdf). [Murata reference sheet, land dimensions](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR71C104KA01-01.pdf).

Carrier C_SDBULK is explicitly changed to Samsung **CL31A226KOHNNNE**, 22 µF, 16 V, ±10%, **X5R**. Its -55..85 °C component rating covers the intended ambient range but does not establish effective capacitance or actual component temperature. This is no longer an unrecorded alternative to X7R. [Samsung specifications](https://product.samsungsem.com/mlcc/CL31A226KOHNNN.do).

Two **Samtec SSW-120-01-G-S** female strips are selected for Pico mechanical review and manual fitting; the owned Pico itself is not an assembly-house component. Verify the strips' drawing, drill fit, seating and engagement with the actual Pico male headers before purchasing. [Samtec part](https://www.samtec.com/products/ssw-120-01-g-s).

## Power path: target not yet demonstrated

**Decision update, 2026-10-15:** the cartridge fuse is kept for the first prototype (option A). The 100 mV loop-drop figure below was a design preference, not a Pi requirement, and is replaced by a measured criterion: at least 4.8 V at the header with 5 A load and the Korad at 5.10 V, with the actual drop recorded. This does not raise the supply voltage. The criterion is proposed and must be confirmed on the bench. The electronic-protection study is deferred to a possible second revision, decided with measured drop and current peaks. The analysis below is kept as the record that led to this decision.

At 5 A, the 100 mV input-to-header loop target permits only 20 mΩ. The reference subtotal including the input contacts is **19.325 mΩ / 96.625 mV**, leaving **0.675 mΩ** for the holder, Pi header, copper, solder and additional temperature effects. These mixed nominal/room-temperature numbers are not a worst-case bound. The complete budget remains open.

The retained Littelfuse 021706.3MXP has nominal cold resistance 9.5 mΩ. The same-current 215-series alternative has 10.8 mΩ, so changing to that time-delay fuse worsens the cold reference and changes its fault behavior. It is rejected as a drop improvement. The reviewed 215 table specifies 1000 A at 72 VDC for 4–6.3 A, but that interruption rating does not reduce operating resistance. [Littelfuse 215, p. 2](https://www.littelfuse.com/assetdocs/littelfuse-fuse-215-datasheet?assetguid=990f7193-d9a2-48e4-b760-2b43514249cf).

No higher-current fuse, bypass, supply-voltage increase or reduction of the copper stackup is adopted to make the budget appear to pass. A soldered fuse could remove holder contacts, but neither a reviewed replacement nor a complete resistance bound is established. A lower-value shunt would also change metrology sensitivity; it has not been substituted. The current fuse remains provisional, and 100 mV remains the requirement. With the Korad limited to 5 A, the 6.3 A fuse is not a guaranteed short-circuit interrupter.

The Schurter OGN datasheet (page 1) gives a contact resistance of 10 mΩ maximum at 100 mA for the holder, without saying whether that is per clip or for the whole holder. At 5 A this is up to 50 mV, or up to 100 mV if per clip. The Littelfuse 217 datasheet (Rev. GD) confirms the 9.5 mΩ nominal cold resistance used in the reference and gives a maximum voltage drop of 130 mV at the 6.3 A rating, which would be up to about 103 mV at 5 A if scaled linearly (an upper-bound estimate the datasheet does not guarantee). Adding the holder to the 132.8 mV reference gives about 183 to 233 mV; using the fuse's datasheet maximum instead of its nominal value raises that to about 238 to 288 mV. All of these exclude the header contacts and heating. With the Korad at 5.10 V, the header would then sit at roughly 4.87 to 4.92 V in the first case and 4.81 to 4.86 V in the second, against the proposed 4.8 V criterion, so the worst case leaves little margin. This is arithmetic on datasheet bounds, not a measurement; the assembled path must be measured at 5 A.

The same datasheet shows why the fuse is not a protection at the supply's 5 A limit: the 6.3 A part must carry 150% of its rating (9.45 A) for at least 60 minutes and opens in 0.05 to 2 s only at 275% (about 17 A). Its interrupting rating is 70 A at 60 VDC. Only the Korad's current limit and the LTC4367 thresholds act below about 9 A.

The [power-path register](../hardware/review/power-path-budget.csv) explicitly retains unknowns. Final review must include actual filled copper, thermal spokes, necks and current sharing through the two 5 V header contacts. Summing trace lengths would not describe the parallel planes correctly.

A subsequent [DC copper screen](../hardware/review/implementation-review.md) models the shunt-to-Pi positive branch with both 5 V contacts ideally tied. It adds approximately 21.2 mV at 5 A, taking the mixed reference subtotal to about 117.8 mV before the other missing contributions. This is an approximate computation, not a complete bound or physical measurement. It strengthens the case for redesigning the loss path before fabrication; the original 100 mV requirement remains unchanged.

## Protection and startup

The [calculation artifact](../hardware/review/design-analysis.json) now adds independent resistor tolerance, 25 ppm/K drift and ±10 nA comparator leakage. It assumes resistor temperatures of 10–70 °C (ambient plus possible heating), which still need validation. Hysteresis and leakage datasheet conditions differ from our 5.1 V application. The previous wider-temperature calculation is retained for comparison.

The LTC4367 gate drive at VIN = VOUT = 5.0 V is 7.2 V minimum, 8.7 V typical and 10.8 V maximum above VOUT (Rev. D, page 4), so the BSC010N04LS6, specified at a 4.5 V gate, is fully enhanced at the intended 5.1 V input; this is a datasheet condition, not a measurement. The datasheet also gives a 32 ms gate turn-on delay after the input returns within thresholds for the part used (500 µs only for the -1 variants), and the FAULT output is an open-drain pin that the design leaves unconnected.

The 12 nF gate capacitor is a slew-control element, not a guaranteed 1 A current limit for every Pi/HAT. A separate calculation uses its tolerance/TCR and the controller's 60 µA upper gate-current reference. For an illustrative 1000 µF load the simplified charging-current reference exceeds 5 A. Actual load capacitance, load current, supply limiting and the MOSFET's safe operating area must be assessed before approving startup. Stored capacitor energy alone cannot establish MOSFET SOA. Gate-current specifications here use VIN=VOUT=12 V and need application verification. [LTC4367, pp. 4 and 15](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf).

The MOSFET ordering code is **BSC010N04LS6ATMA1, PG-TDSON-8 FL**, with enlarged source interconnection. The existing generic TDSON-8-1 snapshot must be compared against the **Rev. 2.3 copper, mask and stencil drawing on p. 11**, not approved from pin pitch or the SuperSO8 name. Its updated board-pad drawing and SOA remain open review items. [Infineon datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc010n04ls6-datasheet-en.pdf).

The LTC4367 FAULT pin is currently unconnected. Thus neither automatic experiment invalidation nor a reliable fault-event log exists. For this supervised prototype, the operator must observe faults and stop the run. A future unattended system needs fault capture and, if required, a hardware latch. This is a documented limitation, not a firmware feature delivered by this change.

The intended ±30 V fault envelope is also still unqualified. Do not execute that entire range merely because it appears in circuit.json: lead inductance, disconnect overshoot, clamping and semiconductor limits need a reviewed test envelope first. The OV threshold is not a proven Pi-safe maximum.

## microSD supply

Keep the dedicated USB-powered TLV75533PDBVR for now. Its 500 mA electrical rating is not continuous thermal approval for this SOT-23 board. A preliminary 150 mA average-current screen at 5.25 V input, 3.267 V output and 40 °C ambient gives about 0.297 W and 109 °C using the JEDEC DBV thermal reference. This excludes quiescent current and is not the actual board thermal resistance. Card selection must demonstrate peak/average current and acceptable write droop; no arbitrary card is approved by this screen. [TI regulator datasheet](https://www.ti.com/lit/gpn/TLV755P).

The 4.7 µF output capacitor must retain at least the specified 0.47 µF effective stability minimum after DC bias, tolerance and temperature, with margin for transients. Nominal 4.7 µF or 22 µF labels do not establish this. Supplier bias curves and measured bursts remain required.

EN is tied to Pico 3V3, while SD pull-ups are tied to the separate SD rail. This does not by itself establish safe power sequencing. Check Pico reset, USB removal, 3V3 collapse and a retained SD charge: GPIO must not be driven above an unpowered domain's allowed limits. Firmware should leave SPI pins high impedance until rails settle, but firmware alone cannot cover every abrupt power-loss case. Review actual rail decay and any need for interface isolation before clearing the SD-power gate. The regulator's active discharge is useful, but no discharge timing guarantee for this assembled circuit is claimed.

## Work still needed before fabrication

1. Complete the remaining exact-package footprint reviews, particularly MOSFET copper/mask/paste, socket orientation/offset, microSD hinge/shell and regulator/buffer packages.
2. Resolve the complete 5 A drop budget, startup SOA, fault envelope and SD power sequencing/effective capacitance. None is marked passed by the automated checks.
3. Perform the rigid mechanical checks with the selected connectors.
4. Confirm assembler stackup/DFM and cost; only then inspect final manufacturing plots. See [assembly sourcing](assembly-sourcing.md) and [fablab validation](fablab-validation.md).

`make component-sync` is an explicit local mutation command: it backs up the projects in `.build/pre-component-selection/`, updates selected components/lands and regenerates schematics from circuit.json without rerouting boards. `make hardware-review` regenerates calculation and geometry evidence. Neither command grants release.

## Electronic-protection follow-up

The [new study](electronic-protection.md) supersedes the partial 117.8 mV accounting subtotal with the six-branch 132.8 mV reference. Copper-only changes give approximately 4.0 mV improvement on the isolated comparison. The user agreed to study electronic protection; no new topology has been promoted to main CAD or BOM.
