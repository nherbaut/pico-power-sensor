# Acceptance tests

Software/source checks and physical validation are separate. No physical test is recorded yet.

| Procedure | Purpose |
|---|---|
| [Electrical](electrical/README.md) | Polarity, continuity, fault response, inrush, drop and temperature |
| [Mechanical](mechanical/README.md) | Pi, cooler, header, HAT and cable fit |
| [Metrology](metrology/README.md) | Calibration, energy integration, time alignment and bandwidth |

`make hardware-check` checks pin mapping, absence of shunt bypasses, exclusion of instrument loads, nominal shunt heating and threshold corners. `make test` injects representative wiring/calculation errors and verifies that the checks reject them. Neither command replaces ERC, DRC or a reference instrument.

`make hardware-erc` and `make hardware-drc` use KiCad 9. Missing tools fail explicitly. The routed review board passes ERC and DRC, including zero unconnected pads and schematic parity checks. Re-run after edits; do not hide failures. Reports are included in the interposer review package.

For each bench test record date, instrument, DUT, exact parts, supply settings, reference equipment, temperatures, procedure, numerical acceptance criteria, observations and outcome (`passed`, `failed`, `inconclusive`). Save original traces and photos; distinguish observations from interpretation.

Carrier checks use `make carrier-check`, `make carrier-erc` and `make carrier-drc`. Source checks verify the instrument/DUT supply boundary, five LED GPIOs and their polarity/current limiting, and both connector mappings against the PCB. Carrier regression tests reject supply swaps, UART cable crossover, reversed LEDs and GPIO conflicts. Native DRC includes schematic parity. The [carrier package](../hardware/pcb/carrier/README.md) records pending physical acceptance.
