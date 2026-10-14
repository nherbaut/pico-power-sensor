# Hardware release procedure

Use the [release checklist](../hardware/release-checklist.csv) and [review evidence](../hardware/review/README.md). Neither board is currently released. Physical measurements must be recorded separately from calculations, footprint review, source tests, ERC and DRC.

There are two gates per board:

| Gate | Required evidence | Meaning |
|---|---|---|
| `fabrication` | Component/circuit/footprint/routing reviews, clean source/ERC/DRC, physical mock-up, stackup and final plot review | Readiness of a specific prototype fabrication package; does not permit DUT connection |
| `connection` | All fabrication checks plus assembled-board continuity, supplies, dummy-load/fault/thermal/interface tests and sensing validation | Recorded validation before attaching the Pi or DUT sensing; instrument acceptance continues separately |

Bench tests require a fabricated prototype. They therefore belong to the connection gate rather than being prerequisites for making the first PCB. Prototype fabrication remains blocked until its own gate is complete. Neither gate authorizes purchases, ordering, publishing or hardware activation by an automated tool.

```sh
make hardware-check hardware-erc hardware-drc
make carrier-check carrier-erc carrier-drc
make test
make hardware-review
make release-check BOARD=interposer GATE=fabrication
make release-check BOARD=carrier GATE=fabrication
make release-check BOARD=interposer GATE=connection
```

`release-check` exits nonzero while required evidence is missing, partial, failed or tied to a different design snapshot. A connection check also requires every fabrication item. Deleting rows, duplicating IDs or inventing exclusions does not bypass the gate. The checker evaluates recorded evidence; it cannot independently verify a bench observation or replace engineering sign-off. It does not generate Gerbers, change CAD or power anything.

For each completed row, record `passed`, a named reviewer, an ISO date, repository-relative evidence paths or primary-source URLs, and the current `design_sha256` printed by the command. Separate multiple evidence paths with semicolons. Leave `remaining` empty only when the requirement is fully met. Store dimensional comparisons, photos, measurements and original traces with their exact board/part identities. Do not mark a physical test passed based on a datasheet or calculation.

The fingerprint covers the native schematic/PCB/project, circuit model, local footprint/symbol libraries, board BOM/library tables, reference BOM and passive proposals. Changed component selections invalidate the earlier snapshot. Re-run relevant checks and review the impact before updating evidence; do not mechanically stamp old passes with a new hash. Source-check and native report files are date-specific evidence and must be refreshed deliberately. Website rendering alone does not refresh hardware validation.

Your first physical task is to print the two [mock-up PDFs](../hardware/review/README.md), verify their scale and photograph the unpowered connector/board stack. Use [mechanical acceptance](../tests/mechanical/README.md) for fit and [electrical acceptance](../tests/electrical/README.md) for prototype bench validation. Missing equipment or HATs stays pending, not passed.

Current prototype work: [design review](design-review.md), [assembly sourcing](assembly-sourcing.md) and [fablab validation](fablab-validation.md).
