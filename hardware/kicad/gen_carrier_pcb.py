#!/usr/bin/python3
"""Generate hardware/kicad/carrier/carrier.kicad_pcb (KiCad 9, 2 layers).

    /usr/bin/python3 -I hardware/kicad/gen_carrier_pcb.py

Fixed geometry inherited from ../picopower (docs/mechanical-baseline.md):
78 x 54 mm outline, M2.5 NPTH holes at (4,4), (74,4), (4,50), (74,50), Pico
pad 1 at (44, 3), pad 20 at (44, 51.26), pad 21 at (61.78, 51.26), pad 40 at
(61.78, 3). MikroE and microSD positions follow docs/carrier-module-fit.md.
Signal copper is produced by gridroute.py (deterministic, part of this
generator). Floorplan rationale: docs/carrier-layout.md.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pcbnew  # noqa: E402
import gridroute as gr  # noqa: E402
from pcblib import Board, V  # noqa: E402

OUT = HERE / "carrier" / "carrier.kicad_pcb"
NET = HERE / "carrier" / "carrier.net"
W, H = 78.0, 54.0
SIG_W = 0.25
PWR_W = 0.4

LED_ROWS = [19.51, 24.59, 29.67, 34.75, 39.83]
UART_R_ROWS = [5.0, 8.5, 12.0, 15.5, 19.0]


def place(bd):
    for ref, (x, y) in {"H1": (4, 4), "H2": (74, 4), "H3": (4, 50), "H4": (74, 50)}.items():
        bd.place(ref, x, y, fpname="MountingHole_2.7mm_M2.5", board_only=True)
    bd.place("J1", 44.0, 3.0)                    # Pico 1-20
    bd.place("J2", 61.78, 51.26, rot=180)        # Pico 21-40 (pin 21 at bottom)
    bd.place("J3", 9.27, 26.836)                 # MikroE 1-8
    bd.place("J4", 32.13, 44.616, rot=180)       # MikroE 9-16 (pin 9 at bottom)
    bd.place("J6", 12.0, 2.5)                    # wire pads to MikroE terminals
    bd.place("C1", 24.5, 2.5)                    # sense differential 100n
    bd.place("J7", 3.5, 22.0, rot=90)            # sense cable, pins upward
    bd.place("J8", 3.5, 40.0, rot=90)            # UART cable, pins upward
    # SN74LV125AN socket on the BACK (owner request 2026-10-17: no part under the
    # MikroE module). Rot 180 on the back puts pins 1-7 at x 20.62 and 8-14 at x 13.
    bd.place("U1", 20.62, 26.0, rot=180, back=True)
    bd.place("C2", 24.5, 26.0, rot=270, back=True)   # U1 bypass, back side
    for k, ref in enumerate(["R1", "R2", "R3", "R4", "R5"]):
        bd.place(ref, 36.0, UART_R_ROWS[k])      # standing resistors, gap strip
    for k in range(5):
        y = LED_ROWS[k]
        bd.place(f"R{6 + k}", 65.3, y)           # LED resistor, right strip
        bd.place(f"D{k + 1}", 74.3, y, rot=180)  # LED, cathode (pad 1) at right
    # microSD socket on the back; pin 1 at (31.36, 21.32), pin 9 at (11.04, 21.32).
    fp = bd.place("J5", 31.36, 21.32, back=True)
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(V(31.36, 21.32))
        x9, y9 = bd.pad_xy("J5", "9")
        if abs(x9 - 11.04) < 0.01 and abs(y9 - 21.32) < 0.01:
            break
    else:
        raise SystemExit("could not orient J5")


def check_fixed(bd):
    want = {("J1", "1"): (44, 3), ("J1", "20"): (44, 51.26), ("J2", "1"): (61.78, 51.26),
            ("J2", "20"): (61.78, 3), ("J3", "1"): (9.27, 26.836), ("J4", "8"): (32.13, 26.836),
            ("J5", "1"): (31.36, 21.32), ("J5", "9"): (11.04, 21.32)}
    for (ref, pad), (x, y) in want.items():
        gx, gy = bd.pad_xy(ref, pad)
        if abs(gx - x) > 0.005 or abs(gy - y) > 0.005:
            raise SystemExit(f"{ref}.{pad} at {(gx, gy)}, expected {(x, y)}")


def pad_cells(pad):
    pos = pad.GetPosition()
    x, y = gr.mm(pos.x), gr.mm(pos.y)
    r = min(gr.mm(pad.GetSize().x), gr.mm(pad.GetSize().y)) / 2 * 0.6
    cells = set()
    layers = [L for L, lay in ((0, pcbnew.F_Cu), (1, pcbnew.B_Cu)) if pad.IsOnLayer(lay)]
    for i in range(int((x - r) / gr.STEP) - 1, int((x + r) / gr.STEP) + 2):
        for j in range(int((y - r) / gr.STEP) - 1, int((y + r) / gr.STEP) + 2):
            if math.hypot(i * gr.STEP - x, j * gr.STEP - y) <= r:
                for L in layers:
                    cells.add((L, i, j))
    return cells, (x, y)


def split_at(bd, net, layer, x, y):
    """Split a same-net track that passes through (x, y) so the new route meets an endpoint."""
    P = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
    for t in list(bd.b.GetTracks()):
        if t.GetClass() != "PCB_TRACK" or t.GetNetname() != net or t.GetLayer() != layer:
            continue
        a, b = t.GetStart(), t.GetEnd()
        if P == a or P == b:
            return
        cross = (b.x - a.x) * (P.y - a.y) - (b.y - a.y) * (P.x - a.x)
        dot = (P.x - a.x) * (b.x - a.x) + (P.y - a.y) * (b.y - a.y)
        L2 = (b.x - a.x) ** 2 + (b.y - a.y) ** 2
        if abs(cross) <= 2 * max(abs(b.x - a.x), abs(b.y - a.y)) and 0 < dot < L2:
            t2 = pcbnew.PCB_TRACK(bd.b)
            t2.SetStart(P)
            t2.SetEnd(b)
            t2.SetWidth(t.GetWidth())
            t2.SetLayer(layer)
            t2.SetNet(t.GetNet())
            t.SetEnd(P)
            bd.b.Add(t2)
            return


def route_all(bd, order):
    grid = gr.Grid(bd.b, W, H)
    for fp in bd.b.GetFootprints():
        for p in fp.Pads():
            grid.add_pad(p)
    pads_by_net = {}
    for fp in bd.b.GetFootprints():
        for p in fp.Pads():
            n = p.GetNetname()
            if n and not n.startswith("unconnected"):
                pads_by_net.setdefault(n, []).append(p)
    failures = []
    for net in order:
        width = PWR_W if net in ("/INSTR_3V3", "/INSTR_GND") else SIG_W
        pads = pads_by_net[net]
        tree_cells, _ = pad_cells(pads[0])
        for p in pads[1:]:
            cells, centre = pad_cells(p)
            if cells & tree_cells:
                continue
            grids = grid.build(width / 2)
            path = grid.route(net, cells, tree_cells, width / 2, grids=grids)
            if path is None:
                failures.append((net, p.GetParentFootprint().GetReference(), p.GetNumber()))
                continue
            polys, vias = gr.path_to_copper(path)
            e = path[-1]  # meets existing copper: split that track first
            split_at(bd, net, pcbnew.F_Cu if e[0] == 0 else pcbnew.B_Cu, e[1] * gr.STEP, e[2] * gr.STEP)
            # stub from the start cell to the pad centre, on the pad
            first = polys[0] if polys else None
            for layer, pts in polys:
                lay = pcbnew.F_Cu if layer == 0 else pcbnew.B_Cu
                bd.track(net, pts, width, layer=lay)
                for a, b in zip(pts, pts[1:]):
                    grid.add_segment(layer, a, b, width, net)
            for (vx, vy) in vias:
                bd.via(net, vx, vy, size=gr.VIA_D, drill=gr.VIA_DRILL)
                grid.add_via(vx, vy, net)
            s = path[0]
            lay = pcbnew.F_Cu if s[0] == 0 else pcbnew.B_Cu
            bd.track(net, [centre, (s[1] * gr.STEP, s[2] * gr.STEP)], width, layer=lay)
            for c in path:
                tree_cells.add(c)
            tree_cells |= cells
    return failures


def main():
    bd = Board(NET)
    bd.rules()
    bd.outline([(0, 0), (W, 0), (W, H), (0, H)])
    place(bd)
    check_fixed(bd)

    # Sense pair and VBUS first (short, direct), then UART, I2C, SD, LEDs, power.
    order = ["/SHUNT_KELVIN_PLUS", "/SHUNT_KELVIN_MINUS", "/DUT_VBUS_SENSE",
             "/PICO_UART_TX", "/PICO_UART_RX", "/PICO_MARK_RX", "/UART_OE_N",
             "/PI_TX_CABLE", "/PI_MARK_CABLE", "/PICO_TX_DRV", "/PI_RX_CABLE",
             "/PM_SDA", "/PM_SCL", "/PM_ALERT_N",
             "/SD_SCLK", "/SD_MISO", "/SD_MOSI", "/SD_CS_N", "/SD_CARD_PRESENT"]
    order += [f"/LED{k}_DRIVE" for k in range(1, 6)] + [f"/LED{k}_A" for k in range(1, 6)]
    # INSTR_GND is carried by the two pours; DRC reports any pad they miss.
    order += ["/INSTR_3V3", "/INSTR_GND"]
    # Rip-up-and-retry: a net that fails moves to the front of the order and the
    # whole board is re-placed and re-routed from scratch (deterministic).
    for attempt in range(6):
        failures = route_all(bd, order)
        if not failures:
            break
        print(f"attempt {attempt}: unrouted {failures}", flush=True)
        failed = []
        for f in failures:
            if f[0] not in failed:
                failed.append(f[0])
        order = failed + [n for n in order if n not in failed]
        bd = Board(NET)
        bd.rules()
        bd.outline([(0, 0), (W, 0), (W, H), (0, H)])
        place(bd)
        check_fixed(bd)
    print("routing order:", order)

    # Ground pours on both layers (instrument ground, low current).
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        bd.zone("/INSTR_GND", lay, [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)],
                clearance=0.3, spoke=0.5)

    T = bd.text
    for ref in ("H1", "H2", "H3", "H4", "J1", "J2", "J6", "J7", "J8", "C1", "C2"):
        bd.ref_at(ref, hide=True)
    for k in range(5):
        bd.ref_at(f"R{6 + k}", hide=True)
        bd.ref_at(f"D{k + 1}", hide=True)
        T(f"LED{k + 1}", 70.0, LED_ROWS[k] - 2.0, 0.8)
        bd.ref_at(f"R{k + 1}", 41.4, UART_R_ROWS[k])
    # Pour spokes cannot form at these ground pads; they are also tied by routed copper.
    for ref, pad in (("U1", "7"), ("J1", "8"), ("J1", "13"), ("R2", "2"), ("J3", "8"), ("J4", "1"), ("J5", "2")):
        bd.solid_pads(ref, {pad})
    T("J7 SENSE", 3.6, 10.6, 0.8)
    T("J8 UART", 3.6, 26.2, 0.8)
    T("J6 IN+ IN- VBUS", 15.8, 5.0, 0.8)
    T("C1", 25.77, 5.0, 0.8)
    T("PICO 2 WH", 52.9, 27.0, 1.0, rot=90)
    T("MIKROE-4810 ABOVE", 21.0, 47.2, 0.8)
    T("SD ON BACK", 21.0, 18.6, 0.8)
    T("U1 C2 ON BACK", 16.8, 44.6, 0.8)
    T("C2", 27.0, 27.27, 0.8, layer=pcbnew.B_SilkS)
    T("picopower-proto carrier r1", 52.9, 27.0, 0.8, layer=pcbnew.B_SilkS, rot=90)
    bd.fill_and_save(OUT)
    print("wrote", OUT)
    if failures:
        sys.exit(2)


if __name__ == "__main__":
    main()
