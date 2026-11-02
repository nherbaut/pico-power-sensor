# Project handoff — current state (2026-10-17, evening)

**Update 2026-11-02:** the project is now published on the `proto` branch of `nherbaut/pico-power-sensor`; GitHub Pages builds that branch. See [the BOM audit](docs/bom-audit-2026-11-02.md) and [32 GB storage-card selection](docs/measurement-storage-card.md). The older Codex Q1 follow-up below predates the owner-selected Si4143DY and is historical; current purchase line 4 already records Farnell 3470713. No CAD was changed in the November review.

Read [AGENTS.md](AGENTS.md) first (controlling rules), then this file. The older [HANDOFF-DUMB-CLAUDE.md](HANDOFF-DUMB-CLAUDE.md) describes the state *before* schematics existed and is now historical.

**Codex follow-up, 2026-10-17:** read [Q1 procurement review](docs/q1-resolution-2026-10-17.md) before acting on the Q1 recommendations below. Mouser also labels the proposed IPP120P04P4L-03 replacement obsolete and lists AKSA1 as an alias; its lifecycle is not established by this handoff. Pololu 5383 is manufacturer Active and Preferred, with a dated Exp-Tech listing of €4.10 ex-VAT / 21 in stock. The owner subsequently chose to continue without Pololu and requested a discrete MOSFET from Mouser or Farnell. That supersedes the restoration recommendation. The follow-up search has not verified a suitable stocked replacement: SUP90P06-09L-E3 is an electrical compromise but Mouser shows zero stock and Farnell quotes about 44 weeks. Current Q1 procurement is blocked; CAD has not been changed.

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
- **Interposer reverse-polarity protection:** the Pololu 5383 (not sold by Farnell/Mouser) was replaced by a P-MOSFET Q1 + 10 kΩ gate resistor R8, order J1 → Q1 → F1 → R1. The first choice, Infineon IPP80P03P4L-04 (TO-220), is end of life; after review (see `docs/q1-resolution-2026-10-17.md`) **Q1 is now the Vishay Si4143DY-T1-GE3 in SO-8** (9.2 mΩ max at −4.5 V / 5 A, pinout 1-3 S, 4 G, 5-8 D), generated into the interposer schematic, board and Gerbers.

## Open decisions (blocking)

1. **Q1 sourcing:** the owner reported 100,612 Si4143DY pieces ready to dispatch but did not name the distributor. Record distributor and order code in `hardware/purchase-bom.csv` line 4, and confirm the exact code `SI4143DY-T1-GE3` is active (DigiKey: Active, 0 stock, ~19 weeks). If it is unavailable, the fallbacks and the rejected parts are in `docs/q1-resolution-2026-10-17.md` and `docs/protection-options.md`; reverting to the Pololu 5383 (Exp-Tech) is the earlier Codex recommendation.
2. **Q1 footprint:** the SO-8 land is the stock KiCad SOIC-8 with pads renamed S/G/D; compare it with Vishay's recommended land (not read) before release. No hole exception is needed any more (the TO-220 1.2 mm question is withdrawn).

When Q1 changes again: update `gen_interposer_sch.py` value/MPN/footprint, `gen_footprints.py`, `gen_interposer_pcb.py` (placement and the RAW/PROTECTED pours), BOM row, purchase BOM line 4, `docs/protection-options.md`, AGENTS.md protection row; regenerate; re-run ERC, DRC, copper collision and copper resistance checks; re-export interposer Gerbers; rebind `hardware/release-checklist.csv` hashes without dropping rows added by other sessions.

## Purchase BOM notes

`hardware/purchase-bom.csv` holds the owner's Farnell/Mouser codes (supplied by him, not verified by Claude on the distributor sites). The owner's last pasted list still contained the obsolete Pololu lines 4–6; the file marks lines 5–6 removed and line 4 = Q1. Line 20 (10 kΩ) needs quantity 3. Line 29 = one Adafruit 3658 kit. Line 13 (Adafruit 2223) must be the current square-pin version.

## Other open items before fabrication (see release checklist)

Test fit of delivered parts against footprints; Active Cooler clearance under the interposer; fabricator finished-hole tolerance for the scoped exceptions; MikroE terminal order on the delivered module; standoff heights (carrier back side carries U1 and the microSD module); an independent human review of schematics and layout; all bench tests (none run). Firmware does not exist yet.
