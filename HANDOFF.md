# Project handoff — current state (2026-10-17, evening)

Read [AGENTS.md](AGENTS.md) first (controlling rules), then this file. The older [HANDOFF-DUMB-CLAUDE.md](HANDOFF-DUMB-CLAUDE.md) describes the state *before* schematics existed and is now historical.

The owner (Nicolas) cannot review schematics or layouts technically. Technical reviews so far were done by Claude; ask him only plain-language decisions (parts, cost, physical arrangement, yes/no). He writes French or English: answer in the language of each message.

## Where the design stands

All ten AGENTS.md steps have a first revision, committed locally on `master` (no remote). Nothing has been ordered, uploaded or powered.

| Step | Status | Main files |
|---|---|---|
| Requirements, architecture | Approved earlier | `docs/requirements.md`, `docs/architecture.md` |
| Parts selection | Done, BOM provisional | `hardware/bom.csv` |
| Interposer schematic | ERC clean | `hardware/kicad/interposer/interposer.kicad_sch`, `docs/interposer-schematic.md` |
| Carrier schematic | ERC clean | `hardware/kicad/carrier/carrier.kicad_sch`, `docs/carrier-schematic.md` |
| PCB layouts | DRC clean, 0 unconnected, parity clean (only footprint-filter naming warnings) | `*.kicad_pcb`, `docs/interposer-layout.md`, `docs/carrier-layout.md` |
| Footprint review | Documentary only | `docs/footprint-review.md` |
| Soldering guides, bench tests | Drafted, nothing performed | `docs/soldering-*.md`, `docs/bench-tests.md` |
| Release checklist | Open items remain | `hardware/release-checklist.csv` |
| Gerbers | Exported, **NOT RELEASED** | `hardware/fab/*-r1-NOT-RELEASED.zip` |
| Purchase BOM | Distributor codes supplied by owner | `hardware/purchase-bom.csv` / `.md` |
| Explanation for the owner | Carrier part written | `docs/how-it-works.md` |

## Source of truth: generators, not GUI edits

Everything in `hardware/kicad/` is produced by scripts. Edit the script, regenerate, re-verify. Do not save boards from the KiCad GUI.

```bash
# schematics (any python3)
python3 -I hardware/kicad/gen_interposer_sch.py
python3 -I hardware/kicad/gen_carrier_sch.py
# footprint library and boards (KiCad's python: /usr/bin/python3 has pcbnew 9.0.9)
/usr/bin/python3 -I hardware/kicad/gen_footprints.py
(cd hardware/kicad/interposer && kicad-cli sch export netlist --format kicadsexpr -o interposer.net interposer.kicad_sch)
(cd hardware/kicad/carrier && kicad-cli sch export netlist --format kicadsexpr -o carrier.net carrier.kicad_sch)
/usr/bin/python3 -I hardware/kicad/gen_interposer_pcb.py
/usr/bin/python3 -u -I hardware/kicad/gen_carrier_pcb.py   # ~2 min; gridroute.py routes the carrier deterministically
# checks
kicad-cli sch erc --severity-all --exit-code-violations -o erc.rpt X.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations -o drc.rpt X.kicad_pcb
```

- Board generators save, reload and fill zones (`pcblib.py`); they also promote courtyard checks in the `.kicad_pro` severity map.
- Copper resistance check (5 A path): needs shapely/scipy, installed by the owner in `~/.venvs/kicad-tools`. The skill's `copper_guards.py` reads KiCad 10 net syntax, so run it on a copy made by `hardware/kicad/tools/netnames_for_guard.py`, with `--grid 0.05`. Last result: `hardware/kicad/interposer/copper-resistance.txt` (13/13 pass, two with very small margin).
- Gerbers: `kicad-cli pcb export gerbers ...` and `pcb export drill ...` into `hardware/fab/<board>-r1/`, then zip (see git history for the exact commands).

## Decisions taken today (2026-10-17), all recorded in docs/BOM

- Pico socket headers: option A (Pico 2 WH factory headers, MikroE factory headers, Adafruit-supplied strip) into Harwin M20-782 sockets.
- AI HAT: raised with a second Adafruit 2223 as extender plus M2.5 nylon standoffs (Adafruit 3658 kit); standoff lengths to be set at first assembly.
- Carrier pin map moved so each bus uses the Pico pins nearest its module: LEDs GP28/27/26/22/21; microSD SPI1 (SCK GP10, MOSI GP11, MISO GP8, CS GP7, CD GP6); I2C0 SDA GP12 / SCL GP13; ALERT GP9; UART GP0–GP3 unchanged. See `docs/carrier-integration.md`, `hardware/review/carrier-pico-pin-contract.csv`.
- Carrier U1 (SN74LV125AN socket) and C2 moved to the back side; nothing sits under the MikroE module.
- **Interposer reverse-polarity protection:** Pololu 5383 (not sold by Farnell/Mouser) was replaced by a TO-220 P-MOSFET Q1 + 10 kΩ gate resistor R8, order J1 → Q1 → F1 → R1. The chosen Infineon IPP80P03P4L-04 then turned out to be **end-of-life (both AKSA1/AKSA2)**.

## Open decisions (blocking)

1. **Q1 part — owner to choose:**
   - Infineon **IPP120P04P4L03AKSA1** (logic level, ≈3 mΩ @10 V; drop-in, same G-D-S TO-220 footprint) — recommended if Farnell has it active; AKSA2 is obsolete.
   - Vishay **SUP90P06-09L-E3** (Farnell 1684069, ≈12 mΩ @−4.5 V, ≈60 mV at 5 A) — drop-in compromise, stock uncertain.
   - Infineon **IPB120P04P4L03ATMA2** (same die, D²PAK SMD) — needs a new footprint and layout change.
   - Or **revert to the Pololu 5383**, bought from a European reseller (e.g. Exp-Tech); the pre-change interposer is in git (commit before `85670e5`).
   - Rejected after datasheet review: YAGEO XP4P016I (28 mΩ @−4.5 V), Diotec DIT110P06 (standard-level gate, R<sub>DS(on)</sub> only specified at −10 V, preliminary sheet, wider leads), Adafruit 6359 (up to ≈45 mΩ). Requirement summary for any candidate: P-channel, logic level, R<sub>DS(on)</sub> ≤ 6 mΩ at V<sub>GS</sub> = −4.5 V (≤ 12 mΩ as compromise), ≥ 20 V, ≥ 10 A, through-hole TO-220 preferred.
2. **Q1 hole size:** the TO-220 footprint uses 1.2 mm drills; AGENTS.md limits holes to 1.0 mm, so the owner must approve this as a scoped exception (not yet answered). If a different Q1 is chosen, recheck its lead dimensions.

When Q1 changes: update `gen_interposer_sch.py` value/MPN, BOM row, purchase BOM line 4, `docs/protection-options.md`, AGENTS.md protection row; regenerate; re-run ERC, DRC, copper collision and copper resistance checks; re-export interposer Gerbers; rebind `hardware/release-checklist.csv` hashes.

## Purchase BOM notes

`hardware/purchase-bom.csv` holds the owner's Farnell/Mouser codes (supplied by him, not verified by Claude on the distributor sites). The owner's last pasted list still contained the obsolete Pololu lines 4–6; the file marks lines 5–6 removed and line 4 = Q1. Line 20 (10 kΩ) needs quantity 3. Line 29 = one Adafruit 3658 kit. Line 13 (Adafruit 2223) must be the current square-pin version.

## Other open items before fabrication (see release checklist)

Test fit of delivered parts against footprints; Active Cooler clearance under the interposer; fabricator finished-hole tolerance for the scoped exceptions; MikroE terminal order on the delivered module; standoff heights (carrier back side carries U1 and the microSD module); an independent human review of schematics and layout; all bench tests (none run). Firmware does not exist yet.
