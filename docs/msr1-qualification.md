# Bourns MSR1-0R005F1 qualification

Date: 2026-10-15. The owner's first “ok” after the lower-cost proposal authorized continuing qualification of the 5 mΩ Bourns candidate. The subsequent “ok” explicitly approves the proposed 1.30 mm finished holes with 3.00 mm pads for its two leads. Record the owner-approved prototype choice in the [provisional BOM](../hardware/bom.csv), with qualification still incomplete. Neither approval establishes measured accuracy or authorizes purchases. **Result: suitable direction for a calibrated prototype; final qualification remains partial.** The approximately 1% task-energy target is unchanged and unproven.

## Connection decision

Retain MSR1-0R005F1, nominal 5 mΩ, 1%, 1 W at the datasheet's 85 °C reference condition. Use two independent sense traces at its two solder pads, with current entering and leaving from the opposite sides of those pads. Keep the coupled sense pair out of the current path. Each pickup must terminate at the pad itself, not at a convenient point along its supply track. The installed transfer resistance includes the resistor leads and solder-joint region inside these pickup points.

The [Bourns application note](../hardware/evidence/shunt/bourns-current-sense-appnote-2022-04.pdf), issue 04/22 e/N2210, page 4 figure 5, explicitly describes four-wire sensing with a two-terminal resistor. It illustrates surface-mount terminals, so it establishes the principle rather than a qualified through-hole layout. Its page 3 discussion explains the separate lead-resistance and copper-temperature terms. This does not turn the MSR into a four-terminal component or remove its lead error. The [MSR datasheet](../hardware/evidence/shunt/bourns-msr-rev-05-26.pdf), revision 05/26 page 1, remains authoritative for the actual package.

Current path: protected bench positive → upstream shunt pad → MSR → downstream shunt pad → Pi 5 V header. Sense path: upstream pad → SENSE_P → monitor IN+; downstream pad → SENSE_N → IN−. Separately sense DUT bus voltage at the intended header reference. Keep instrument power and auxiliary loads outside the downstream current path. Add no extra hand-attached sense wires to the resistor body in this candidate implementation.

Use repeatable lead insertion/seating geometry and preserve it after calibration. Replacing the resistor, resoldering its joints or changing pickup copper invalidates the installed-resistance calibration. The resistor is nonpolar; the chosen current direction determines SENSE_P/N and reported current sign. Document that direction on the later schematic and silkscreen.

## Owner-approved footprint dimensions

| Item | Proposal or evidence |
|---|---|
| Maximum round lead | 1.05 mm, from 1.0 ±0.05 mm printed diameter |
| Proposed finished plated hole | **1.30 mm**, for both shunt leads only |
| Proposed round pad diameter | **3.00 mm** |
| Finished-hole tolerance used for this screening | Assumed ±0.05 mm; verify against the eventual fabricator before freezing the footprint |
| Minimum diametral insertion allowance | Calculated 1.25 − 1.05 = **0.20 mm** under that assumption |
| Minimum annular ring | Calculated (3.00 − 1.35) / 2 = **0.825 mm**, excluding registration tolerance |
| Lead-centre spacing | Datasheet nominal **11.4 mm**, tolerance +1.0/−0.5 mm; accommodate permitted lead forming and verify actual insertion before release |
| Assembly access | Reserve at least 1 mm solder-tip clearance around accessible joints; review actual neighbouring components and pad entry geometry later |

The dimensions are approved by the owner; they are not yet a KiCad footprint or fabrication approval. The larger holes are made and plated by the PCB manufacturer; the owner only inserts and solders the component. The 3 mm pads exceed the existing 1.8 mm minimum. The inherited outline, mounting holes and Pi header remain fixed. Installed-height, cooler/HAT clearance, lead forming and the high-current pad/zone connection remain open layout checks. Do not silently change a finished-hole requirement into a pre-plating drill size.

**Approved exception:** AGENTS.md now records 1.30 mm finished holes and 3.00 mm pads for the two MSR1-0R005F1 leads. No other component's drill rule changes.

## Electrical and firmware integration

At nominal 5 A and 5 mΩ, calculated shunt loss is **25 mV / 0.125 W**. At +1% initial resistance, it is **25.25 mV / 0.12625 W**, excluding temperature and extra resistance of the installed pickup geometry. The remaining provisional 100 mV path budget is **74.75 mV** for every other positive/return path loss; final total-path feasibility remains unresolved.

The INA228 ±40.96 mV range is a reasonable evaluation setting. Its nominal current ceiling is 8.192 A; at 5.05 mΩ it is approximately 8.111 A. These are ADC range calculations, not allowed operating or protection currents. Recompute from the installed transfer resistance after calibration and include temperature/overload margin.

For evaluation, CURRENT_LSB = 20 µA gives a positive signed-current-register ceiling of 10.48574 A; the analog range remains the tighter limit at nominal resistance. TI SLYS021A section 8.1.2 requires SHUNT_CAL = 13107.2 × 10^6 × CURRENT_LSB × RSHUNT, multiplied by four for ADCRANGE=1. Nominal 5 mΩ gives 5242.88, rounded to **5243**; the register-only scale rounding is calculated as approximately **0.002289%**. This is an illustrative starting setting, not final calibrated firmware. Compute scaling from the calibrated installed transfer, retain the register value and software coefficient, and read configuration back. Merely writing SHUNT_CAL is not physical calibration.

Keep **TEMPCOMP=0**. INA228 SLYS021A section 7.3.5 uses the monitor's die temperature for correction and requires thermal coupling to the shunt. The interposer and carrier are separated by 10–20 cm; that die temperature does not establish shunt temperature. Do not enter the distributor's 20 ppm/°C wire figure as a complete-shunt compensation coefficient. Retain continuous conversion and the earlier monitor-evaluation settings; this review adds no firmware implementation.

## Accuracy decision and calibration contract

Calibrate the complete installed current channel as Vshunt = R_eff × I_ref + V_offset using several reference-current points spanning the intended use, including zero and ascending/descending repeats. R_eff captures the installed transfer resistance and any channel gain folded into this fit; do not report it as an independent measurement of bare resistor resistance. Zero fitting must not conceal common-mode or temperature dependence. Calibration and independent validation must use separate readings, with traceable reference uncertainty and temperature conditions recorded.

The reference equipment is not yet identified. No present multimeter, current source or clock is assumed capable of establishing 1% energy accuracy. A later, separately authorized dummy-load procedure must establish current and voltage reference uncertainty, thermal settling, run duration and acquisition timing before Pi use. This is a component qualification plan, not an executed bench test or the board release checklist.

Proposed planning allocations for relative task-energy error are: 0.20% installed-current calibration residual/reference; 0.20% thermal change of the installed shunt; 0.15% remaining current-channel effects; 0.15% voltage channel/reference boundary; 0.10% integration timebase; 0.10% task-boundary/sampling effects; 0.10% remaining effects and margin. Their arithmetic sum is 1.00%. These are unapproved design allocations, not demonstrated bounds, statistically independent uncertainties or achieved specifications. Correlated and cross-product terms must fit within the complete eventual bound.

For sensitivity only, a 500 ppm/K planning model and 4 K change give 0.20% resistance change. That uses the high end of the manufacturer's published family TCR range, not an exact-variant guaranteed limit or a measured temperature rise. It cannot establish acceptance of a 4 K operating window. The exact effective coefficient, lead/joint contribution and thermal conditions remain unverified. No numeric point was extracted from the MSR TCR chart because the required chart-digitization tooling is unavailable.

A fixed room-temperature calibration does not remove thermal drift. Do not promise 1% accuracy until independent validation covers the accepted load and temperature range, realistic task lengths and marker timing. The earlier 1.08 ms conversion-pair timing example also shows that the proposed 0.10% boundary allocation can fail for short tasks; keep durations owner-defined, characterize alignment and evaluate declared batches where appropriate. The chip's approximately 0.5% oscillator tolerance at room temperature likewise cannot satisfy the proposed 0.10% timebase allocation without a characterized correction or independently validated timing method.

## Qualification disposition

| Review | Finding |
|---|---|
| Cost | Approximately €1.60 including VAT, before shipping, in the retained indexed offer; owner accepted proceeding at this candidate price |
| Four-wire principle | Supported for two-terminal parts by manufacturer application note; actual pickup geometry and transfer uncertainty not yet validated |
| Nominal range/dissipation | Screening calculations support continued design at the proposed 5 A; assembled temperature and faults remain unverified |
| Lead fit | Owner approved 1.30 mm finished holes and 3.00 mm pads; verify actual footprint and fabrication tolerances before release |
| Sourcing/lifecycle | Current manufacturer family documentation and distributor active exact code retained; manufacturer exact-variant lifecycle confirmation remains open |
| Accuracy | Partial: calibration/thermal/reference/timing evidence required; no 1% pass |
| Footprint and populated mechanics | Proposal only; no land pattern, layout or physical fit approval |
| ERC / DRC / parity | Not performed: no KiCad design created in this phase |
| Bench validation | Not performed; no hardware energized |

Calculated values are saved in [the screening CSV](../hardware/review/msr1-calculations.csv); [the input/output receipt](../hardware/review/msr1-qualification-inputs.json) binds the current review. The approved inexpensive part and hole dimensions may now be carried into later design. The provisional BOM is not a qualified release BOM; remaining module/protection/system checks are not waived.
