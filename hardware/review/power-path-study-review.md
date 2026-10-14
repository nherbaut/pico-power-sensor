# Power-path study review, 2026-10-14

Scope: an isolated copper comparison and a preliminary electronic replacement for the removable fuse. The authoritative interposer and carrier CAD/BOM were not modified. No fabrication or Pi connection is approved by this study.

## Independent review

A fresh reviewer performed one read-only, nonvisual pass, with a predeclared termination criterion: rederive the arithmetic, check primary-source conditions, report ranked findings, and stop without edits. It independently reproduced all six incumbent copper branches, their 7.231500920 mΩ total, the 132.782504599 mV mixed subtotal, the 5.414351144–5.827801910 A detector screening interval, and the 85.282504599 mV no-cartridge accounting subtotal. It checked that the candidate ZIP PCB hash matches its recorded binding and that its native DRC report records zero violations, unconnected items and parity errors.

| Finding | Resolution by the implementation agent |
|---|---|
| EP-01: the study exporter could consume stale copper evidence after a main-PCB change | Export now rejects a mismatching authoritative PCB hash, a missing six-branch loop, nonfinite/nonpositive resistance, or an inconsistent branch sum before writing outputs. Mutation tests exercise stale evidence and a changed branch. |
| EP-02: TPS25982's 7.6 V variant was called OVLO | Corrected to the manufacturer's OVP terminology. |

There was no second independent pass. The reviewer did not review visual layout, rerun the candidate solver, measure hardware, or qualify the proposed circuit. Primary-source references and their conditions are in the [study](../../docs/electronic-protection.md) and [calculation artifact](electronic-protection-study.json).

## Candidate verification scope

KiCad 9.0.9 native DRC/parity passes on the isolated narrower copper candidate. A wider exploration isolated ground copper and was rejected; no violation was suppressed. The whole-loop solver reports only 4.034769196 mV improvement at 5 A, including the worsened ground return. This candidate is not promoted to the main design.

The certain-short guard's GUI-initializing CLI could not open an X display. The unchanged headless `audit_board` function was instead calibrated with foreign-net crossing tracks (rejected) and separated tracks (accepted), then applied to the saved candidate without serialization. It reports no findings among 2,468 track/via/pad items; zones are outside that guard's scope and are checked separately by native DRC. The [report](power-path-candidate-collisions.json) binds the candidate hash. This is not a claim that the GUI-dependent CLI passed.

The implementation agent inspected the candidate PCB PNG and conceptual architecture PNG after a same-session vision-probe pass (100352). These images establish reviewable geometry and readable architecture labels, not physical fit or an approved electrical schematic.

## Remaining design gates

The electronic topology still needs a brownout/enable interlock, startup sequencing, deliberate arming/reset, actual shutdown timing and MOSFET SOA analysis, sensing-input power-order checks, and a conventional-symbol schematic/netlist review before PCB integration. Contact resistance, hot-device behavior and the new routing remain outside the accounting comparison. The fabrication and Pi-connection release gates remain incomplete; there are no new bench measurements.
