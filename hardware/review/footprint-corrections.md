# Footprint corrections and electrical follow-up

Review date: 2026-10-14. **The user has authorized overwriting CAD, and the checked corrections are now integrated into both main projects.** The previous saved boards, changed footprint libraries and interposer autosave were preserved under `.build/pre-footprint-integration/`. The obsolete autosave was removed from the working project. Neither board is released; no Gerbers are generated.

The shared `scripts/footprint_corrections.py` applies the same geometry during future native layout/generation. Interposer draft pad definitions and the carrier socket generator are updated too. Regression checks cover native dimensions, cathode mapping, local libraries, generator output and correction idempotence. Board outlines, mounting positions and net assignments are unchanged; the existing paper evidence remains useful for preliminary placement. Actual 1.6 mm seating and cooler/HAT checks remain pending.

## Isolated CAD candidates

The [interposer candidate](interposer-footprint-candidate.zip) and [carrier candidate](carrier-footprint-candidate.zip) retain the historical isolated review copies used before integration. Each contains native KiCad files, local libraries and its ERC/DRC reports. The change manifests identify the old baseline and candidate PCB hashes: [interposer](interposer-candidate-changes.json), [carrier](carrier-candidate-changes.json). Use the main project packages for current CAD and drawings. These historical archives are not fabrication releases.

```sh
make footprint-candidates
```

This reads current saved projects, copies them into `.build/footprint-candidates/`, changes the specified geometry, refills zones and runs native checks. It never regenerates or reroutes the originals. Any violation fails the target; no exclusion is added. The script checks that original CAD, circuit files and autosaves retain their hashes. Candidate routing otherwise remains unchanged.

| Item | Saved CAD discrepancy | Candidate correction | Remaining |
|---|---|---|---|
| Six APT2012LZGCK LEDs | Previously generic pads 0.975 x 1.40 mm, 0.90 mm inner gap | Integrated: 1.25 x 1.10 mm, 1.10 mm gap; pad 1 cathode retained; silk/courtyard adjusted | Physical soldering/brightness and assembly review |
| WSK2512 shunt | Previously sense pads 1.40 x 0.76 mm | Integrated: 1.70 x 0.76 mm sense pads; outer edge retained and centre adjusted; current pads unchanged; silk moved clear | Kelvin routing/sign-off and fitted calibration |
| NPPN062FJFN socket | Previously 7.20 mm projected body depth | Integrated: 4.85 mm projected depth; 7.20 mm is height; larger courtyard retained | Body offset, EVM numbering/mating and physical support remain provisional |

Sources: [Kingbright page 1](https://www.kingbrightusa.com/images/catalog/spec/apt2012lzgck.pdf), [Vishay page 2](https://www.vishay.com/docs/30108/wsk2512.pdf), [Sullins drawing 10461-H](https://drawings-pdf.s3.amazonaws.com/10461.pdf). Geometric agreement is a datasheet review, not a physical measurement. Enlarging the shunt sense pads exposed a silkscreen/mask violation; moving the silkscreen resolves it without suppressing the check.

## Fuse and drop budget

The existing reference BOM already proposes **021706.3MXP**; earlier review wording incorrectly said an exact fuse part was missing. [Littelfuse's 217-series datasheet](https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe), page 2, specifies 70 A interrupting capability at 60 VDC for the 6.3 A variant, nominal cold resistance 9.5 mOhm, and maximum 130 mV drop at its rated 6.3 A. That supports the DC choice for this low-voltage, current-limited bench arrangement. It does not establish assembled drop at 5 A or fuse clearing with a 5 A limit.

At 5 A, the fuse's nominal cold reference contributes 47.5 mV. Add the shunt's initial-tolerance reference 25.125 mV and two MOSFETs' room-temperature reference 14 mV: **86.625 mV before holder, input/header contacts and copper**. The complete 100 mV loop target leaves 2.675 mOhm for those elements under these reference assumptions. This is not a worst-case guarantee; hot fuse and MOSFET resistance still need review and measurement. The 130 mV fuse specification at 6.3 A must not be rescaled into a guaranteed 5 A value. The drop target remains unresolved; do not raise the Korad voltage or remove protection to hide losses.

## Protection recovery

For the [LTC4367](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4367.pdf), changing only divider precision cannot guarantee both automatic OV recovery at 5.10 V and a 5.25 V static cutoff ceiling. Even ignoring resistor errors, the stated comparator/hysteresis corners require divider gain above 5.10 / (0.4925 - 0.032) = 11.075 for guaranteed recovery, but below 5.25 / 0.5075 = 10.345 for that ceiling. Those inequalities conflict. This is a calculation using the stated test conditions, not a Pi absolute-rating assertion.

The current design needs either a validated manual recovery procedure with run abort on a fault, or a protection redesign if unattended recovery and a tighter ceiling are required. Do not assume SHDN resets comparator hysteresis. The prototype test plan must verify disconnect, rail decay, fault-state recovery and repeatable startup. No recovery procedure is yet validated.

## Component choices

The [passive selection table](../passive-proposals.csv) now records Samsung CL31A226KOHNNNE (22 uF, 16 V, 1206, X5R, +/-10%) as an explicit prototype selection. The later [design review](../../docs/design-review.md) adopts the X5R change in CAD/BOM for the agreed 10..40 C ambient use. Component temperature, effective capacitance and SD write tests remain open; selection is not release approval.

The LED consumption estimate now uses the selected part's datasheet reference rather than an assumed 1.8 V. The forward-voltage/current operating point and brightness are still bench measurements. Remaining work includes complete passive land-pattern review, semiconductor copper/mask/paste review, microSD socket documentation, SD supply sequencing/thermal review and physical stack checks. Both fabrication and connection gates remain blocked.

## SD regulator thermal reference

For the selected DBV package, the [TI thermal table](https://www.ti.com/lit/gpn/TLV755P), section 5.4, gives 100.8 C/W on its EVM and 231.1 C/W on its JEDEC reference board. Neither is a measurement of this carrier. At an assumed 5 V input, 3.3 V output and 500 mA, nominal dissipation is 0.85 W; those references imply junction estimates of 125.7 C and 236.4 C at 40 C ambient, against a 125 C recommended operating maximum. The advertised 500 mA electrical rating therefore cannot establish continuous carrier capability. See the [reference calculation table](carrier-power-budget.csv). Validate actual card bursts, average load, output droop and temperature before accepting the card/regulator combination; the table does not specify an approved load envelope.
