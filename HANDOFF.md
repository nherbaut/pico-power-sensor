# Project handoff — current state (2026-11-03)

The project is published on the `proto` branch of `nherbaut/pico-power-sensor`; GitHub Pages builds that branch. See [the BOM audit](docs/bom-audit-2026-11-02.md) and [32 GB storage-card selection](docs/measurement-storage-card.md). No CAD was changed in the November documentary updates.

Read [AGENTS.md](AGENTS.md) first (controlling rules), then this file. The older [HANDOFF-DUMB-CLAUDE.md](HANDOFF-DUMB-CLAUDE.md) describes the state *before* schematics existed and is now historical.

The owner (Nicolas) cannot review schematics or layouts technically. Technical reviews so far were done by Claude; ask him only plain-language decisions (parts, cost, physical arrangement, yes/no). He writes French or English: answer in the language of each message.

## Where the design stands

All ten AGENTS.md steps have a first revision. The current prototype is committed and published on `proto`. Nothing has been ordered, submitted for fabrication or powered. The owner confirmed on 2026-11-02 that no parts have been purchased.

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

## Current design choices

- Pico socket headers: option A (Pico 2 WH factory headers, MikroE factory headers, Adafruit-supplied strip) into Harwin M20-782 sockets.
- AI HAT: raised with a second Adafruit 2223 as extender plus M2.5 nylon standoffs (Adafruit 3658 kit); standoff lengths to be set at first assembly.
- Carrier pin map moved so each bus uses the Pico pins nearest its module: LEDs GP28/27/26/22/21; microSD SPI1 (SCK GP10, MOSI GP11, MISO GP8, CS GP7, CD GP6); I2C0 SDA GP12 / SCL GP13; ALERT GP9; UART GP0–GP3 unchanged. See `docs/carrier-integration.md`, `hardware/review/carrier-pico-pin-contract.csv`.
- Carrier U1 (SN74LV125AN socket) and C2 moved to the back side; nothing sits under the MikroE module.
- **Interposer reverse-polarity protection:** Vishay Si4143DY-T1-GE3 in SO-8, with 10 kΩ gate pull-down R8. Order J1 → Q1 → F1 → R1. The SO-8 exception is recorded in AGENTS.md. Q1 is in the generated schematic, board and fabrication candidate. It does not block reverse current from the Pi side.
- **Measurement storage:** one Integral INMSDH32G10-90U1, 32 GB, Farnell 3410199; prototype qualification remains partial.

**Shunt BOM update, 2026-11-03:** the owner selected MSR3-0R005F1 / Farnell 4582745. CAD still uses MSR1 at 11.4 mm pitch; MSR3 needs 15.2 mm pitch and a new HAT clearance review. No generator, PCB or fabrication export was changed. See [substitution record](docs/shunt-update-2026-11-03.md).

## Open decisions (blocking)

1. **Purchasing:** the [2026-11-02 audit](docs/bom-audit-2026-11-02.md) records supplier identifiers, indicated stock and pack minimums. Q1 is Farnell 3470713, minimum five in that observation. Exact manufacturer lifecycle remains incompletely qualified; current checkout must be confirmed. The shunt BOM now selects MSR3-0R005F1, Farnell 4582745 (indexed French one-piece offer retrieved 2026-11-03); its PCB integration is blocking. The Adafruit square-pin revision remains unresolved.
2. **Footprints and fit:** the Q1 SO-8 land was compared on paper with Vishay AN826 on 2026-10-17; see [footprint review](docs/footprint-review.md). Populated fit and the remaining release checks are still open. This is separate from supplier stock.
3. **Storage:** verify SPI initialization, write-current peaks, rail margin, latency and power-loss behavior for the selected card.

When Q1 changes again: update `gen_interposer_sch.py` value/MPN/footprint, `gen_footprints.py`, `gen_interposer_pcb.py` (placement and the RAW/PROTECTED pours), BOM row, purchase BOM line 4, `docs/protection-options.md`, AGENTS.md protection row; regenerate; re-run ERC, DRC, copper collision and copper resistance checks; re-export interposer Gerbers; rebind `hardware/release-checklist.csv` hashes without dropping rows added by other sessions.

## Purchase BOM notes

The [purchase CSV](hardware/purchase-bom.csv) and [readable list](hardware/purchase-bom.md) contain only current items. Fitted quantities and indicative order quantities are separate. Line IDs remain stable for the sourcing audit; removed items are preserved in git history rather than as zero-quantity shopping rows.

The dated audit and hash receipts describe their original snapshots. The 2026-11-03 documentation cleanup changes bound BOM inputs; those receipts are not fresh qualification passes and were not rebound. Historical component comparisons remain available in the dated review documents.

## Other open items before fabrication (see release checklist)

Test fit of delivered parts against footprints; Active Cooler clearance under the interposer; fabricator finished-hole tolerance for the scoped exceptions; MikroE terminal order on the delivered module; standoff heights (carrier back side carries U1 and the microSD module); an independent human review of schematics and layout; all bench tests (none run). Firmware does not exist yet.
