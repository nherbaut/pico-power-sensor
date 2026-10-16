#!/usr/bin/env python3
"""Generate the carrier schematic (KiCad 9) from the approved part set.

Source of truth for hardware/kicad/carrier/carrier.kicad_sch.
Do not edit the generated schematic in the GUI; edit this file and rerun.

Connectivity is expressed with local net labels on short wire stubs at every
pin. Net names follow hardware/review/carrier-pico-pin-contract.csv,
carrier-module-connections.csv and uart-buffer-pin-contract.csv; deviations
are listed in docs/carrier-schematic.md.

Run:  python3 -I hardware/kicad/gen_carrier_sch.py
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
OUT = Path(__file__).resolve().parent / "carrier" / "carrier.kicad_sch"
PROJECT = "carrier"
GRID = 1.27
STUB = 2.54

ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "picopower-proto/carrier/root"))


def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "picopower-proto/carrier/" + "/".join(map(str, parts))))


def ongrid(v):
    return abs(v / GRID - round(v / GRID)) < 1e-6


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


_libs = {}


def lib(name):
    if name not in _libs:
        _libs[name] = SymbolLib(SYMDIR / f"{name}.kicad_sym")
    return _libs[name]


# ---------------------------------------------------------------- module pin maps
# Pico 2 WH physical pin -> net (hardware/review/carrier-pico-pin-contract.csv).
PICO = {
    1: "PICO_UART_TX", 2: "PICO_UART_RX", 3: "INSTR_GND", 4: "PICO_MARK_RX",
    5: "UART_OE_N", 6: "PM_SDA", 7: "PM_SCL", 8: "INSTR_GND", 9: "PM_ALERT_N",
    10: "LED1_DRIVE", 11: "LED2_DRIVE", 12: "LED3_DRIVE", 13: "INSTR_GND",
    14: "LED4_DRIVE", 15: "LED5_DRIVE", 16: "NC_GP12", 17: "NC_GP13",
    18: "INSTR_GND", 19: "NC_GP14", 20: "NC_GP15", 21: "SD_MISO", 22: "SD_CS_N",
    23: "INSTR_GND", 24: "SD_SCLK", 25: "SD_MOSI", 26: "SD_CARD_PRESENT",
    27: "NC_GP21", 28: "INSTR_GND", 29: "NC_GP22", 30: "NC_RUN", 31: "NC_GP26",
    32: "NC_GP27", 33: "NC_AGND", 34: "NC_GP28", 35: "NC_ADC_VREF",
    36: "INSTR_3V3", 37: "NC_3V3_EN", 38: "INSTR_GND", 39: "NC_VSYS", 40: "NC_VBUS",
}
# MIKROE-4810 mikroBUS pin -> net (hardware/review/carrier-module-connections.csv).
PM = {1: "NC_AN", 2: "NC_RST", 3: "NC_CS", 4: "NC_SCK", 5: "NC_MISO", 6: "NC_MOSI",
      7: "INSTR_3V3", 8: "INSTR_GND", 9: "INSTR_GND", 10: "NC_5V", 11: "PM_SDA",
      12: "PM_SCL", 13: "NC_TX", 14: "NC_RX", 15: "PM_ALERT_N", 16: "NC_PWM"}
# Adafruit 4682 header pin -> net.
SD = {1: "INSTR_3V3", 2: "INSTR_GND", 3: "SD_SCLK", 4: "SD_MISO", 5: "SD_MOSI",
      6: "SD_CS_N", 7: "NC_SD_DAT1", 8: "NC_SD_DAT2", 9: "SD_CARD_PRESENT"}


def span(m, lo, n):
    """Socket pin k (1..n) carries module pin lo+k-1."""
    return {str(k): m[lo + k - 1] for k in range(1, n + 1)}


# (ref, lib, symbol, x, y, angle, value, fields, {pin: net or None}, [unit])
PARTS = [
    ("J1", "Connector_Generic", "Conn_01x20", 50.8, 88.9, 0, "Pico pins 1-20",
     {"MPN": "Harwin M20-7822042"}, span(PICO, 1, 20)),
    ("J2", "Connector_Generic", "Conn_01x20", 50.8, 160.02, 0, "Pico pins 21-40",
     {"MPN": "Harwin M20-7822042"}, span(PICO, 21, 20)),
    ("J3", "Connector_Generic", "Conn_01x08", 127.0, 76.2, 0, "MikroE pins 1-8",
     {"MPN": "Harwin M20-7820842"}, span(PM, 1, 8)),
    ("J4", "Connector_Generic", "Conn_01x08", 127.0, 109.22, 0, "MikroE pins 9-16",
     {"MPN": "Harwin M20-7820842"}, span(PM, 9, 8)),
    ("J5", "Connector_Generic", "Conn_01x09", 127.0, 152.4, 0, "Adafruit 4682 microSD",
     {"MPN": "Harwin M20-7820942"}, span(SD, 1, 9)),
    ("J6", "Connector_Generic", "Conn_01x03", 190.5, 76.2, 0, "Wire pads to MikroE IN1+/IN1-/IN2 VBUS",
     {"Note": "Three plated wire pads; short wires to the module screw terminals"},
     {"1": "SHUNT_KELVIN_PLUS", "2": "SHUNT_KELVIN_MINUS", "3": "DUT_VBUS_SENSE"}),
    ("C1", "Device", "C", 215.9, 99.06, 90, "100n X7R 50V",
     {"MPN": "KEMET C315C104K5R5TA"},
     {"1": "SHUNT_KELVIN_PLUS", "2": "SHUNT_KELVIN_MINUS"}),
    ("J7", "Connector_Generic", "Conn_01x04", 254.0, 78.74, 0, "Sense from interposer",
     {"MPN": "JST B4B-XH-A"},
     {"1": "SHUNT_KELVIN_PLUS", "2": "SHUNT_KELVIN_MINUS", "3": "DUT_VBUS_SENSE", "4": "INSTR_GND"}),
    ("U1", "74xx", "74LS125", 215.9, 157.48, 0, "SN74LV125AN",
     {"MPN": "TI SN74LV125AN in TE 1-2199298-3 socket"},
     {"1": "UART_OE_N", "2": "PI_TX_CABLE", "3": "PICO_UART_RX"}, 1),
    ("U1", "74xx", "74LS125", 215.9, 185.42, 0, "SN74LV125AN", {},
     {"4": "UART_OE_N", "5": "PI_MARK_CABLE", "6": "PICO_MARK_RX"}, 2),
    ("U1", "74xx", "74LS125", 215.9, 213.36, 0, "SN74LV125AN", {},
     {"10": "UART_OE_N", "9": "PICO_UART_TX", "8": "PICO_TX_DRV"}, 3),
    ("U1", "74xx", "74LS125", 215.9, 241.3, 0, "SN74LV125AN", {},
     {"13": "INSTR_3V3", "12": "INSTR_GND", "11": None}, 4),
    ("U1", "74xx", "74LS125", 167.64, 190.5, 0, "SN74LV125AN", {},
     {"14": "INSTR_3V3", "7": "INSTR_GND"}, 5),
    ("C2", "Device", "C", 167.64, 228.6, 90, "100n X7R 50V",
     {"MPN": "KEMET C315C104K5R5TA"}, {"1": "INSTR_3V3", "2": "INSTR_GND"}),
    ("R1", "Device", "R", 279.4, 200.66, 90, "470 1%",
     {"MPN": "Vishay MRS25000C4700FCT00"}, {"1": "PICO_TX_DRV", "2": "PI_RX_CABLE"}),
    ("R2", "Device", "R", 279.4, 152.4, 90, "100k 1%",
     {"MPN": "Vishay MRS25000C1003FCT00"}, {"1": "PI_TX_CABLE", "2": "INSTR_GND"}),
    ("R3", "Device", "R", 279.4, 170.18, 90, "100k 1%",
     {"MPN": "Vishay MRS25000C1003FCT00"}, {"1": "PI_MARK_CABLE", "2": "INSTR_GND"}),
    ("R4", "Device", "R", 279.4, 233.68, 90, "10k 1%",
     {"MPN": "Vishay MRS25000C1002FCT00"}, {"1": "UART_OE_N", "2": "INSTR_3V3"}),
    ("R5", "Device", "R", 279.4, 251.46, 90, "10k 1%",
     {"MPN": "Vishay MRS25000C1002FCT00"}, {"1": "PICO_UART_TX", "2": "INSTR_3V3"}),
    ("J8", "Connector_Generic", "Conn_01x05", 340.36, 220.98, 0, "UART/marker from interposer",
     {"MPN": "JST B5B-XH-A"},
     {"1": "INSTR_GND", "2": "PI_TX_CABLE", "3": "PI_RX_CABLE", "4": "PI_MARK_CABLE", "5": None}),
    ("#FLG01", "power", "PWR_FLAG", 63.5, 223.52, 0, "PWR_FLAG", {}, {"1": "INSTR_3V3"}),
    ("#FLG02", "power", "PWR_FLAG", 88.9, 223.52, 0, "PWR_FLAG", {}, {"1": "INSTR_GND"}),
]
for i in range(5):
    y = 106.68 + 20.32 * i
    PARTS.append((f"R{6 + i}", "Device", "R", 320.04, y, 90, "1k8 1%",
                  {"MPN": "Vishay MRS25000C1801FCT00"},
                  {"1": f"LED{i + 1}_DRIVE", "2": f"LED{i + 1}_A"}))
    PARTS.append((f"D{i + 1}", "Device", "LED", 360.68, y, 180, "TLLR4401 red",
                  {"MPN": "Vishay TLLR4401"},
                  {"2": f"LED{i + 1}_A", "1": "INSTR_GND"}))

ROLES = {"J1": "J_PICO_LEFT", "J2": "J_PICO_RIGHT", "J3": "J_PM_LEFT", "J4": "J_PM_RIGHT",
         "J5": "J_SD", "J6": "J_PM_ANALOG", "C1": "C_SENSE_DIFF", "J7": "J_SENSE",
         "U1": "U_UART", "C2": "C_UART", "R1": "R_PICO_TX", "R2": "R_PI_TX_PD",
         "R3": "R_PI_MARK_PD", "R4": "R_UART_OE_PU", "R5": "R_PICO_TX_PU", "J8": "J_UART"}
ROLES.update({f"R{6 + i}": f"R_LED{i + 1}" for i in range(5)})
ROLES.update({f"D{i + 1}": f"LED{i + 1}" for i in range(5)})

NOTES = [
    (20.32, 25.4, "CARRIER - instrument side (generated by gen_carrier_sch.py; do not edit by hand). Everything here is powered by the Pico's own USB; nothing is fed from the DUT."),
    (20.32, 30.48, "INSTR_3V3 comes only from Pico pin 36 (3V3_OUT). Pico VBUS (40) and VSYS (39) are left unconnected. Pico, MikroE and microSD plug into Harwin sockets J1-J5."),
    (20.32, 35.56, "J2 pin k = Pico pin 20+k; J4 pin k = MikroE pin 8+k. Physical socket order is fixed at footprint stage (Pico pin 21 is opposite pin 20)."),
    (20.32, 40.64, "Sense: J7 -> C1 (100n across the Kelvin pair, close to the module) -> J6 wire pads -> MikroE IN1+ / IN1- / IN2 VBUS screw terminals. J7 pin 4 is the shared ground reference."),
    (20.32, 264.16, "UART (docs/uart-interface-qualification.md): U1 is USB-powered. Keep UART_OE_N high (R4) until the Pico has set up its pins. Pico TX is normal polarity (R5 idle-high)."),
    (20.32, 269.24, "R2/R3 load the Pi outputs (approved UART-bias exception). R1 is the 470R source resistor for Pico->Pi. U1 channel 4 unused: input low, enable high."),
    (297.18, 96.52, "Indicators: Pico GP7-GP11 -> 1.8k -> red LED -> ground."),
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
    for part in PARTS:
        ref, libname, sym, x, y, ang, value, fields, nets = part[:9]
        unit = part[9] if len(part) > 9 else 1
        first_unit = unit == min(p[9] if len(p) > 9 else 1 for p in PARTS if p[0] == ref)
        if not (ongrid(x) and ongrid(y)):
            raise ValueError(f"{ref} placement off grid")
        used.add((libname, sym))
        pins = lib(libname).require_pins(sym, unit=unit)
        numbers = {p[0] for p in pins}
        if set(nets) != numbers:
            raise ValueError(f"{ref}: net map pins {sorted(nets)} != symbol pins {sorted(numbers)}")
        tys = [y + transform_pin(p[2], p[3], ang)[1] for p in pins]
        top, bot = min(tys + [y - 2.54]), max(tys + [y + 2.54])
        up = any(outward(p[4], ang)[1] < 0 and abs(y + transform_pin(p[2], p[3], ang)[1] - top) < 1e-6
                 and top < y for p in pins)
        down = any(outward(p[4], ang)[1] > 0 and abs(y + transform_pin(p[2], p[3], ang)[1] - bot) < 1e-6
                   and bot > y for p in pins)
        ry = (bot + 3.81) if up else (top - 3.81)
        vy = (bot + 6.35) if up else (top - 8.89 if down else bot + 3.81)
        ang = 0 if ang == 180 else ang  # field text stays upright; symbol angle restored below
        sym_ang = part[5]
        flag = ref.startswith("#")
        rx = x
        if up and down:
            rx, ry = x + 7.62, y
        props = [prop("Reference", ref, rx, ry, hide=flag, angle=ang),
                 prop("Value", value, x, vy, hide=flag or not first_unit, angle=ang)]
        if not flag:
            props.append(prop("Role", ROLES[ref], x, (top - 6.35) if (down and not up) else vy + 2.54, hide=not first_unit, angle=ang))
        props += [
                 prop("Footprint", "", x, y, hide=True),
                 prop("Datasheet", "", x, y, hide=True)]
        for i, (k, v) in enumerate(fields.items()):
            props.append(prop(k, v, x, y + 2.54 * i, hide=True))
        pin_uuids = " ".join(f"(pin {q(p[0])} (uuid {q(uid(ref, 'pin', p[0]))}))" for p in pins)
        bom = "no" if flag else "yes"
        body.append(
            f"(symbol (lib_id {q(libname + ':' + sym)}) (at {x:.2f} {y:.2f} {sym_ang}) (unit {unit}) "
            f"(exclude_from_sim no) (in_bom {bom}) (on_board {bom}) (dnp no) "
            f"(uuid {q(uid(ref, unit))}) {' '.join(props)} {pin_uuids} "
            f"(instances (project {q(PROJECT)} (path {q('/' + ROOT_UUID)} (reference {q(ref)}) (unit {unit})))))")
        for num, _name, px, py, pang, _et in pins:
            dx, dy = transform_pin(px, py, sym_ang)
            ex, ey = round(x + dx, 4), round(y + dy, 4)
            net = nets[num]
            pinmap[(ref, num)] = net
            ox, oy = outward(pang, sym_ang)
            if net is None or net.startswith("NC_"):
                # Intentionally unused pin: explicit no-connect; the contract
                # name is kept as plain text so the drawing says what it is.
                body.append(f"(no_connect (at {ex:.2f} {ey:.2f}) (uuid {q(uid('nc', ref, num))}))")
                if net:
                    tx = ex + ox * 1.27
                    just = "left" if ox > 0 else "right"
                    body.append(f"(text {q(net[3:] + ' (unused)')} (exclude_from_sim no) (at {tx:.2f} {ey:.2f} 0) "
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
           f"(title_block (title \"Carrier\") (company \"picopower-proto\") (comment 1 \"Prototype - not released\"))\n"
           f"(lib_symbols\n{libsyms}\n)\n" + "\n".join(body) +
           "\n(sheet_instances (path \"/\" (page \"1\")))\n(embedded_fonts no)\n)\n")
    return out, pinmap


def main():
    text, pinmap = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    pm = OUT.with_name("carrier.pinmap.tsv")
    pm.write_text("".join(f"{r}\t{n}\t{net or 'NC'}\n" for (r, n), net in sorted(pinmap.items())))
    print(f"wrote {OUT} sha256={hashlib.sha256(text.encode()).hexdigest()} pins={len(pinmap)}")


if __name__ == "__main__":
    main()
