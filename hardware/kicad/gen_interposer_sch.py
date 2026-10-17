#!/usr/bin/env python3
"""Generate the interposer schematic (KiCad 9) from the approved part set.

Source of truth for hardware/kicad/interposer/interposer.kicad_sch.
Do not edit the generated schematic in the GUI; edit this file and rerun.

Connectivity is expressed with local net labels on short wire stubs at every
pin, so each net name in the netlist equals a name used in the project
contracts (docs/power-connector-options.md, hardware/review/*contract*.csv).

Run:  python3 -I hardware/kicad/gen_interposer_sch.py
"""
import hashlib
import math
import sys
import uuid
from pathlib import Path

SKILL_SCRIPTS = Path.home() / ".claude/skills/kicad-design/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from kicad_symlib import SymbolLib, transform_pin  # noqa: E402

SYMDIR = Path("/usr/share/kicad/symbols")
OUT = Path(__file__).resolve().parent / "interposer" / "interposer.kicad_sch"
PROJECT = "interposer"
GRID = 1.27
STUB = 2.54

ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "picopower-proto/interposer/root"))


def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "picopower-proto/interposer/" + "/".join(map(str, parts))))


def ongrid(v):
    return abs(v / GRID - round(v / GRID)) < 1e-6


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


_libs = {}


def lib(name):
    if name not in _libs:
        _libs[name] = SymbolLib(SYMDIR / f"{name}.kicad_sym")
    return _libs[name]


# ---------------------------------------------------------------- Pi header
# Physical pin -> net, from hardware/review/pi-header-contract.csv. Pi-side
# UART/marker GPIO choice (GPIO14 TX, GPIO15 RX, GPIO23 marker) is the default
# recorded in docs/interposer-schematic.md; change it here and in that doc.
PI_PINS = {
    1: "PI_3V3", 2: "DUT_5V_POST_SHUNT", 3: "PI_GPIO2", 4: "DUT_5V_POST_SHUNT",
    5: "PI_GPIO3", 6: "BENCH_GND", 7: "PI_GPIO4", 8: "PI_GPIO14_TXD",
    9: "BENCH_GND", 10: "PI_GPIO15_RXD", 11: "PI_GPIO17", 12: "PI_GPIO18",
    13: "PI_GPIO27", 14: "BENCH_GND", 15: "PI_GPIO22", 16: "PI_GPIO23_MARKER",
    17: "PI_3V3", 18: "PI_GPIO24", 19: "PI_GPIO10", 20: "BENCH_GND",
    21: "PI_GPIO9", 22: "PI_GPIO25", 23: "PI_GPIO11", 24: "PI_GPIO8",
    25: "BENCH_GND", 26: "PI_GPIO7", 27: "PI_ID_SD_GPIO0", 28: "PI_ID_SC_GPIO1",
    29: "PI_GPIO5", 30: "BENCH_GND", 31: "PI_GPIO6", 32: "PI_GPIO12",
    33: "PI_GPIO13", 34: "BENCH_GND", 35: "PI_GPIO19", 36: "PI_GPIO16",
    37: "PI_GPIO26", 38: "PI_GPIO20", 39: "BENCH_GND", 40: "PI_GPIO21",
}

# ---------------------------------------------------------------- parts
# (ref, lib, symbol, x, y, angle, value, fields, {pin: net or None(=NC)})
PARTS = [
    ("J1", "Connector", "Screw_Terminal_01x02", 45.72, 73.66, 0,
     "Bench 5.1V in", {"MPN": "Wurth Elektronik 691137710002"},
     {"1": "BENCH_5V1_RAW", "2": "BENCH_GND"}),
    ("Q1", "Device", "Q_PMOS", 81.28, 71.12, 90,
     "IPP80P03P4L-04", {"MPN": "Infineon IPP80P03P4L-04 (TO-220, pin 1 G, 2 D, 3 S, tab D)"},
     {"D": "BENCH_5V1_RAW", "S": "PROTECTED_5V1", "G": "Q1_GATE"}),
    ("R8", "Device", "R", 81.28, 96.52, 0,
     "10k 1%", {"MPN": "Vishay MRS25000C1002FCT00"},
     {"1": "Q1_GATE", "2": "BENCH_GND"}),
    ("F1", "Device", "Fuse", 127.0, 71.12, 90,
     "6.3A F 5x20", {"MPN": "Littelfuse 021706.3MXP in Schurter 0031.8201.G (FH1)"},
     {"1": "PROTECTED_5V1", "2": "FUSED_5V1"}),
    ("R1", "Device", "R_Shunt", 203.2, 71.12, 90,
     "5m 1% 1W", {"MPN": "Bourns MSR1-0R005F1"},
     {"1": "FUSED_5V1", "4": "DUT_5V_POST_SHUNT",
      "2": "KELVIN_PLUS_SRC", "3": "KELVIN_MINUS_SRC"}),
    ("R2", "Device", "R", 165.1, 109.22, 90,
     "82 5% 1W", {"MPN": "Vishay PR01000108209JR500"},
     {"1": "KELVIN_PLUS_SRC", "2": "SHUNT_KELVIN_PLUS"}),
    ("R3", "Device", "R", 165.1, 127.0, 90,
     "82 5% 1W", {"MPN": "Vishay PR01000108209JR500"},
     {"1": "KELVIN_MINUS_SRC", "2": "SHUNT_KELVIN_MINUS"}),
    ("R4", "Device", "R", 165.1, 144.78, 90,
     "82 5% 1W", {"MPN": "Vishay PR01000108209JR500"},
     {"1": "DUT_5V_POST_SHUNT", "2": "DUT_VBUS_SENSE"}),
    ("NT1", "Device", "NetTie_2", 165.1, 162.56, 0,
     "NetTie", {"Note": "Single-point tie at DUT-header ground pickup"},
     {"1": "BENCH_GND", "2": "MEAS_GND_REF"}),
    ("J5", "Connector_Generic", "Conn_01x04", 243.84, 127.0, 0,
     "Sense to carrier", {"MPN": "JST B4B-XH-A"},
     {"1": "SHUNT_KELVIN_PLUS", "2": "SHUNT_KELVIN_MINUS",
      "3": "DUT_VBUS_SENSE", "4": "MEAS_GND_REF"}),
    ("R5", "Device", "R", 165.1, 210.82, 90,
     "470 1%", {"MPN": "Vishay MRS25000C4700FCT00"},
     {"1": "PI_GPIO14_TXD", "2": "PI_TX_TO_PICO"}),
    ("R6", "Device", "R", 165.1, 228.6, 90,
     "470 1%", {"MPN": "Vishay MRS25000C4700FCT00"},
     {"1": "PI_GPIO23_MARKER", "2": "PI_TASK_MARKER"}),
    ("R7", "Device", "R", 165.1, 246.38, 90,
     "100k 1%", {"MPN": "Vishay MRS25000C1003FCT00"},
     {"1": "PI_GPIO15_RXD", "2": "BENCH_GND"}),
    ("NT2", "Device", "NetTie_2", 165.1, 264.16, 0,
     "NetTie", {"Note": "Single-point tie at DUT-header ground pickup"},
     {"1": "BENCH_GND", "2": "SIGNAL_GND"}),
    ("J6", "Connector_Generic", "Conn_01x05", 243.84, 228.6, 0,
     "UART/marker to carrier", {"MPN": "JST B5B-XH-A"},
     {"1": "SIGNAL_GND", "2": "PI_TX_TO_PICO", "3": "PI_GPIO15_RXD",
      "4": "PI_TASK_MARKER", "5": None}),
    ("J2", "Connector_Generic", "Conn_02x20_Odd_Even", 335.28, 134.62, 0,
     "Pi 40-pin stacking", {"MPN": "Adafruit 2223 (square-pin)"},
     {str(k): v for k, v in PI_PINS.items()}),
]

# Conventional reference -> project role name used in the BOM and review docs.
ROLES = {"J1": "J_POWER", "F1": "F1+FH1", "Q1": "Q_RP", "R8": "R_RP_GATE",
         "R1": "RSH1", "R2": "R_SENSE_PLUS", "R3": "R_SENSE_MINUS", "R4": "R_VBUS",
         "NT1": "NT_MEAS", "J5": "J_SENSE", "R5": "R_PI_TX", "R6": "R_PI_MARK",
         "R7": "R_PI_RX_PD", "NT2": "NT_SIG", "J6": "J_UART", "J2": "J2"}

FOOTPRINTS = {
    "J1": "picopower-proto:TerminalBlock_WE_691137710002_P5.00mm_D1.35mm",
    "F1": "picopower-proto:Fuseholder_Schurter_0031.8201_P22.5mm_D1.35mm",
    "Q1": "picopower-proto:TO-220-3_Horizontal_TabDown_GDS_D1.2mm",
    "R8": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P2.54mm_Vertical_1.8mm",
    "R1": "picopower-proto:R_Shunt_Bourns_MSR1_P11.40mm_Kelvin",
    "R2": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "R3": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "R4": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "R5": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "R6": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "R7": "picopower-proto:R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
    "NT1": "picopower-proto:NetTie-2_SMD_Pad0.5mm",
    "NT2": "picopower-proto:NetTie-2_SMD_Pad0.5mm",
    "J5": "picopower-proto:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical_1.8mm",
    "J6": "picopower-proto:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical_1.8mm",
    "J2": "picopower-proto:PiStack_Adafruit2223_2x20_P2.54mm_D1.10mm",
}

NOTES = [
    (20.32, 25.4, "INTERPOSER - power path and observation taps (generated by gen_interposer_sch.py; do not edit by hand)"),
    (20.32, 30.48, "DUT current path: J1 -> Q1 (P-MOSFET reverse-polarity switch) -> F1 (cartridge in Schurter holder FH1) -> R1 shunt -> J2 pins 2/4 -> Pi -> J2 GND pins -> J1 pin 2"),
    (20.32, 35.56, "Everything upstream of R1 pin 1 is outside the DUT measurement. Q1 conducts only with correct bench polarity (gate held at ground by R8); it does not block reverse current from the Pi side."),
    (20.32, 40.64, "R1 pins 2/3 are separate Kelvin pickups at the shunt lead pads; route KELVIN_* as a coupled pair, never through the 5A copper."),
    (20.32, 86.36, "Observation resistors sit at the source, before the exposed cable (docs/sense-interface-options.md). C_SENSE_DIFF (100nF) is on the carrier."),
    (20.32, 91.44, "NT1 / NT2: tie MEAS_GND_REF and SIGNAL_GND to BENCH_GND at one point next to the Pi-header ground pins."),
    (20.32, 185.42, "UART/marker (docs/uart-interface-qualification.md): 470R source resistors for Pi outputs here; Pico->Pi 470R and Pi-output 100k pull-downs are on the carrier."),
    (20.32, 190.5, "R7 (100k Pi-RX pull-down) is on the interposer. Pi GPIO choice (TX GPIO14, RX GPIO15, marker GPIO23) is a default pending AI HAT confirmation."),
    (20.32, 195.58, "The carrier pull-downs on PI_TX_TO_PICO/PI_TASK_MARKER and R7 load Pi pins under the approved UART-bias measurement-boundary exception. J6 pin 5 empty."),
    (299.72, 96.52, "J2: all 40 contacts pass through unchanged to the HAT above"),
]


# ---------------------------------------------------------------- emitters
def embedded_lib_symbol(libname, sym):
    L = lib(libname)
    if L.parent_of(sym):
        raise ValueError(f"{libname}:{sym} uses extends; resolve before embedding")
    block = L.resolve(sym)
    head = f'(symbol "{sym}"'
    if not block.lstrip().startswith(head):
        raise ValueError(f"unexpected block head for {sym}")
    return block.replace(head, f'(symbol "{libname}:{sym}"', 1)


def prop(name, value, x, y, hide=False, angle=0):
    eff = "(effects (font (size 1.27 1.27))" + (" (hide yes)" if hide else "") + ")"
    return f"(property {q(name)} {q(value)} (at {x:.2f} {y:.2f} {angle}) {eff})"


def wire(x1, y1, x2, y2):
    for v in (x1, y1, x2, y2):
        if not ongrid(v):
            raise ValueError(f"off-grid endpoint {(x1, y1, x2, y2)}")
    if not (abs(x1 - x2) < 1e-9 or abs(y1 - y2) < 1e-9):
        raise ValueError(f"diagonal wire {(x1, y1, x2, y2)}")
    return (f"(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) "
            f"(stroke (width 0) (type default)) (uuid {q(uid('w', x1, y1, x2, y2))}))")


def label(net, x, y, angle):
    justify = {0: "left", 180: "right", 90: "left", 270: "right"}[angle]
    return (f"(label {q(net)} (at {x:.2f} {y:.2f} {angle}) "
            f"(effects (font (size 1.27 1.27)) (justify {justify} bottom)) "
            f"(uuid {q(uid('l', net, x, y))}))")


def outward(pin_angle, sym_angle):
    a = math.radians(pin_angle)
    vx, vy = -round(math.cos(a)), -round(math.sin(a))
    return transform_pin(vx, vy, sym_angle)


def vec_angle(dx, dy):
    if dx > 0:
        return 0
    if dx < 0:
        return 180
    return 270 if dy > 0 else 90


def build():
    body = []
    used = set()
    pinmap = {}
    owners = {}
    for part in PARTS:
        for net in part[8].values():
            if net:
                owners.setdefault(net, set()).add(part[0])
    for ref, libname, sym, x, y, ang, value, fields, nets in PARTS:
        if not (ongrid(x) and ongrid(y)):
            raise ValueError(f"{ref} placement off grid")
        used.add((libname, sym))
        pins = lib(libname).require_pins(sym)
        numbers = {p[0] for p in pins}
        if set(nets) != numbers:
            raise ValueError(f"{ref}: net map pins {sorted(nets)} != symbol pins {sorted(numbers)}")
        tys = [y + transform_pin(p[2], p[3], ang)[1] for p in pins]
        top, bot = min(tys + [y - 2.54]), max(tys + [y + 2.54])
        up = any(outward(p[4], ang)[1] < 0 and abs(y + transform_pin(p[2], p[3], ang)[1] - top) < 1e-6
                 and top < y for p in pins)
        ry = (bot + 3.81) if up else (top - 3.81)
        vy = (bot + 6.35) if up else (bot + 3.81)
        props = [prop("Reference", ref, x, ry, angle=ang),
                 prop("Value", value, x, vy, angle=ang),
                 prop("Role", ROLES[ref], x, vy + 2.54, angle=ang),
                 prop("Footprint", FOOTPRINTS.get(ref, ""), x, y, hide=True),
                 prop("Datasheet", "", x, y, hide=True)]
        for i, (k, v) in enumerate(fields.items()):
            props.append(prop(k, v, x, y + 2.54 * i, hide=True))
        pin_uuids = " ".join(f"(pin {q(p[0])} (uuid {q(uid(ref, 'pin', p[0]))}))" for p in pins)
        body.append(
            f"(symbol (lib_id {q(libname + ':' + sym)}) (at {x:.2f} {y:.2f} {ang}) (unit 1) "
            f"(exclude_from_sim no) (in_bom {'no' if ref.startswith('NT') else 'yes'}) (on_board yes) (dnp no) "
            f"(uuid {q(uid(ref))}) {' '.join(props)} {pin_uuids} "
            f"(instances (project {q(PROJECT)} (path {q('/' + ROOT_UUID)} (reference {q(ref)}) (unit 1)))))")
        for num, _name, px, py, pang, _et in pins:
            dx, dy = transform_pin(px, py, ang)
            ex, ey = round(x + dx, 4), round(y + dy, 4)
            net = nets[num]
            pinmap[(ref, num)] = net
            ox, oy = outward(pang, ang)
            if net is None or owners[net] == {"J2"}:
                # Unused on this board (nets that touch only J2 pass straight
                # through the stacking header, or the empty UART
                # cavity): explicit no-connect; the contract name is kept as
                # plain text so the drawing still says what the pin carries.
                body.append(f"(no_connect (at {ex:.2f} {ey:.2f}) (uuid {q(uid('nc', ref, num))}))")
                if net:
                    tx = ex + ox * 1.27
                    just = "left" if ox > 0 else "right"
                    body.append(f"(text {q(net + ' (pass-through)')} (exclude_from_sim no) (at {tx:.2f} {ey:.2f} 0) "
                                f"(effects (font (size 1.0 1.0)) (justify {just})) (uuid {q(uid('pt', ref, num))}))")
                continue
            sx, sy = round(ex + ox * STUB, 4), round(ey + oy * STUB, 4)
            body.append(wire(ex, ey, sx, sy))
            body.append(label(net, sx, sy, vec_angle(ox, oy)))
    for x, y, text in NOTES:
        body.append(f"(text {q(text)} (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) "
                    f"(effects (font (size 1.524 1.524)) (justify left bottom)) (uuid {q(uid('t', text))}))")
    libsyms = "\n".join(embedded_lib_symbol(l, s) for l, s in sorted(used))
    out = (f"(kicad_sch (version 20250114) (generator \"eeschema\") (generator_version \"9.0\")\n"
           f"(uuid {q(ROOT_UUID)}) (paper \"A3\")\n"
           f"(title_block (title \"Interposer\") (company \"picopower-proto\") (comment 1 \"Prototype - not released\"))\n"
           f"(lib_symbols\n{libsyms}\n)\n" + "\n".join(body) +
           "\n(sheet_instances (path \"/\" (page \"1\")))\n(embedded_fonts no)\n)\n")
    return out, pinmap


def main():
    text, pinmap = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    pm = OUT.with_name("interposer.pinmap.tsv")
    pm.write_text("".join(f"{r}\t{n}\t{net or 'NC'}\n" for (r, n), net in sorted(pinmap.items())))
    print(f"wrote {OUT} sha256={hashlib.sha256(text.encode()).hexdigest()} pins={len(pinmap)}")


if __name__ == "__main__":
    main()
