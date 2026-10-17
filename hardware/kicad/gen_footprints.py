#!/usr/bin/python3
"""Build the project footprint library hardware/kicad/lib/picopower-proto.pretty.

Run with KiCad's Python:  /usr/bin/python3 -I hardware/kicad/gen_footprints.py

Each footprint is derived from a stock KiCad 9.0.9 footprint (or drawn from
the manufacturer drawing cited below) and adjusted to AGENTS.md: pads >= 1.8 mm,
drills 0.8-1.0 mm except the owner-approved scoped exceptions. Every change
is listed in docs/footprint-review.md.
"""
import sys
from pathlib import Path

import pcbnew

KLIB = Path("/usr/share/kicad/footprints")
OUT = Path(__file__).resolve().parent / "lib" / "picopower-proto.pretty"
OLD = Path("/home/nherbaut/workspace/picopower/hardware/pcb/interposer/PicoPower.pretty")
MM = pcbnew.FromMM


def load(lib, name):
    fp = pcbnew.FootprintLoad(str(lib), name)
    if fp is None:
        raise SystemExit(f"missing footprint {lib}:{name}")
    return fp


def set_pads(fp, drill, size, numbers=None):
    for p in fp.Pads():
        if numbers is not None and p.GetNumber() not in numbers:
            continue
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            continue
        p.SetDrillSize(pcbnew.VECTOR2I(MM(drill), MM(drill)))
        sx, sy = pcbnew.ToMM(p.GetSize())
        p.SetSize(pcbnew.VECTOR2I(MM(max(size, sx) if size is None else size),
                                  MM(max(size, sy) if size is None else size)))


def grow_pads(fp, minimum):
    for p in fp.Pads():
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            continue
        sx, sy = pcbnew.ToMM(p.GetSize())
        p.SetSize(pcbnew.VECTOR2I(MM(max(minimum, sx)), MM(max(minimum, sy))))


def clear_layer(fp, layer):
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() == layer:
            fp.Remove(item)


def rect(fp, layer, x1, y1, x2, y2, width=0.05):
    for (a, b) in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        s = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(layer)
        s.SetWidth(MM(width))
        fp.Add(s)


def courtyard(fp, x1, y1, x2, y2):
    clear_layer(fp, pcbnew.F_CrtYd)
    rect(fp, pcbnew.F_CrtYd, x1, y1, x2, y2, 0.05)


def tht_pad(fp, num, x, y, drill, size, square=False):
    p = pcbnew.PAD(fp)
    p.SetNumber(num)
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_RECT if square else pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    p.SetDrillSize(pcbnew.VECTOR2I(MM(drill), MM(drill)))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    p.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    fp.Add(p)
    return p


def smd_pad(fp, num, x, y, size):
    p = pcbnew.PAD(fp)
    p.SetNumber(num)
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    p.SetLayerSet(ls)
    p.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    fp.Add(p)
    return p


def new_fp(name, descr):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("", name))
    fp.SetLibDescription(descr)
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
    fp.Reference().SetText("REF**")
    fp.Reference().SetLayer(pcbnew.F_SilkS)
    fp.Value().SetText(name)
    fp.Value().SetLayer(pcbnew.F_Fab)
    return fp


def save(fp, name, descr=None):
    fp.SetFPID(pcbnew.LIB_ID("", name))
    if descr:
        fp.SetLibDescription(descr)
    fp.Value().SetText(name)
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    io.FootprintSave(str(OUT), fp)
    print("saved", name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.kicad_mod"):
        f.unlink()

    # Schurter 0031.8201 holder: exception 1.35 mm / 3.00 mm, no central NPTH,
    # courtyard = 25 x 10.8 installation envelope (docs/protection-options.md) + 0.25.
    fp = load(KLIB / "Fuse.pretty", "Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open")
    for p in list(fp.Pads()):
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            fp.Remove(p)
    set_pads(fp, 1.35, 3.0)
    courtyard(fp, 11.25 - 12.5 - 0.25, -5.4 - 0.25, 11.25 + 12.5 + 0.25, 5.4 + 0.25)
    save(fp, "Fuseholder_Schurter_0031.8201_P22.5mm_D1.35mm",
         "Schurter 0031.8201 5x20 open holder; owner-approved 1.35 mm holes / 3.00 mm pads; no fastening hole")

    # Wurth 691137710002, drawn from WE drawing rev 001.002: pitch 5.00, body
    # L=10 (2.5 each side of the outer pins), depth 7.5 with pins 4.0 from the
    # wire-entry face (-y) and 3.5 from the rear face.
    fp = new_fp("TerminalBlock_WE_691137710002_P5.00mm_D1.35mm", "")
    tht_pad(fp, "1", 0, 0, 1.35, 3.0, square=True)
    tht_pad(fp, "2", 5.0, 0, 1.35, 3.0)
    rect(fp, pcbnew.F_Fab, -2.5, -4.0, 7.5, 3.5, 0.1)
    rect(fp, pcbnew.F_SilkS, -2.62, -4.12, 7.62, 3.62, 0.12)
    courtyard(fp, -3.0, -4.5, 8.0, 4.0)
    save(fp, "TerminalBlock_WE_691137710002_P5.00mm_D1.35mm",
         "Wurth WR-TBL 691137710002, 2 pos 5.00 mm; wire entry toward -Y; owner-approved 1.35/3.00 mm")

    # Samtec SSQ-102-01-G-S socket: exception 1.10 mm / 2.00 mm.
    fp = load(KLIB / "Connector_PinSocket_2.54mm.pretty", "PinSocket_1x02_P2.54mm_Vertical")
    set_pads(fp, 1.10, 2.0)
    save(fp, "Socket_Samtec_SSQ-102_1x02_P2.54mm_D1.10mm",
         "Samtec SSQ-102-01-G-S; owner-approved 1.10 mm holes / 2.00 mm pads")

    # Bourns MSR1 with Kelvin pickups: leads 11.4 mm, 1.30/3.00 exception.
    # Pads 2/3 are F.Cu-only pickups inside the lead pads (net-tie groups 1+2, 3+4),
    # on the inner side so load current enters from the outer side of each pad.
    fp = new_fp("R_Shunt_Bourns_MSR1_P11.40mm_Kelvin", "")
    tht_pad(fp, "1", 0, 0, 1.30, 3.0)
    smd_pad(fp, "2", 1.9, 0, 1.0)
    smd_pad(fp, "3", 9.5, 0, 1.0)
    tht_pad(fp, "4", 11.4, 0, 1.30, 3.0)
    fp.AddNetTiePadGroup("1,2")
    fp.AddNetTiePadGroup("3,4")
    rect(fp, pcbnew.F_Fab, -0.5, -2.4, 11.9, 2.4, 0.1)
    rect(fp, pcbnew.F_SilkS, 1.7, -2.5, 9.7, 2.5, 0.12)
    courtyard(fp, -1.8, -2.9, 13.2, 2.9)
    save(fp, "R_Shunt_Bourns_MSR1_P11.40mm_Kelvin",
         "Bourns MSR1 5 mOhm, leads 11.4 mm, owner-approved 1.30/3.00 mm; Kelvin pickups pads 2/3")

    # Adafruit 2223 stacking header: inherited Stack_2x20 pad centres,
    # owner-approved 1.10 mm / 2.00 mm.
    fp = load(OLD, "Stack_2x20_P2.54")
    set_pads(fp, 1.10, 2.0)
    save(fp, "PiStack_Adafruit2223_2x20_P2.54mm_D1.10mm",
         "Adafruit 2223 square-pin stacking socket; inherited picopower pad centres; 1.10/2.00 mm")

    # Harwin M20-782 sockets: 1.00 mm holes, 1.8 mm pads (no exception).
    for n in (8, 9, 20):
        fp = load(KLIB / "Connector_PinSocket_2.54mm.pretty", f"PinSocket_1x{n:02d}_P2.54mm_Vertical")
        set_pads(fp, 1.00, 1.8)
        save(fp, f"Socket_Harwin_M20-782_1x{n:02d}_P2.54mm",
             f"Harwin M20-782 {n}-pos socket, 1.00 mm holes, 1.8 mm pads")

    # JST XH vertical: keep 0.95 mm drill, grow pads to >= 1.8 mm.
    for n in (4, 5):
        fp = load(KLIB / "Connector_JST.pretty", f"JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical")
        grow_pads(fp, 1.8)
        save(fp, f"JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical_1.8mm",
             f"JST B{n}B-XH-A; stock land with pads grown to 1.8 mm")

    # Axial resistors: horizontal 10.16 mm and vertical 2.54 mm, 0.8 mm drill.
    fp = load(KLIB / "Resistor_THT.pretty", "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    grow_pads(fp, 1.8)
    save(fp, "R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm",
         "Axial 6.5 x 2.5 mm body (PR01 / MRS25), 10.16 mm pitch")
    fp = load(KLIB / "Resistor_THT.pretty", "R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical")
    grow_pads(fp, 1.8)
    save(fp, "R_Axial_L6.5mm_D2.5mm_P2.54mm_Vertical_1.8mm",
         "Axial MRS25 standing, 2.54 mm pitch")

    # DIP-14 socket.
    fp = load(KLIB / "Package_DIP.pretty", "DIP-14_W7.62mm_Socket")
    grow_pads(fp, 1.8)
    save(fp, "DIP-14_W7.62mm_Socket_1.8mm", "DIP-14 socket TE 1-2199298-3 (drawing not recovered)")

    # 3 mm LED.
    fp = load(KLIB / "LED_THT.pretty", "LED_D3.0mm")
    save(fp, "LED_D3.0mm", "3 mm LED, pad 1 = cathode")

    # KEMET C315 radial, 2.54 mm pitch, 0.61 mm max lead -> 0.9 mm drill.
    fp = load(KLIB / "Capacitor_THT.pretty", "C_Disc_D3.8mm_W2.6mm_P2.50mm")
    for p in fp.Pads():
        if p.GetNumber() == "2":
            p.SetPosition(pcbnew.VECTOR2I(MM(2.54), 0))
    set_pads(fp, 0.9, 1.8)
    save(fp, "C_Radial_KEMET_C315_P2.54mm", "KEMET C315 radial ceramic, 2.54 mm pitch; body assumed 3.8 x 2.6 mm")

    # Infineon IPP80P03P4L-04 (PG-TO220-3) lying flat, tab down. Pads renamed to
    # the symbol's pin names: 1 = G, 2 = D, 3 = S (Infineon TO-220 pinout; tab = D).
    # Drill 1.2 mm: maximum lead diagonal about 1.05 mm (0.86 x 0.6 mm). Tab
    # mounting hole removed (no screw; dissipation below 0.2 W).
    fp = load(KLIB / "Package_TO_SOT_THT.pretty", "TO-220-3_Horizontal_TabDown")
    for p in list(fp.Pads()):
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            fp.Remove(p)
    names = {"1": "G", "2": "D", "3": "S"}
    for p in fp.Pads():
        p.SetNumber(names[p.GetNumber()])
    set_pads(fp, 1.2, 2.0)
    save(fp, "TO-220-3_Horizontal_TabDown_GDS_D1.2mm",
         "TO-220-3 lying flat, tab down, pads G/D/S, 1.2 mm drill (needs owner hole exception)")

    # Three wire pads for the MikroE analog leads.
    fp = new_fp("WirePads_1x03_P3.81mm_D1.0mm", "")
    for i in range(3):
        tht_pad(fp, str(i + 1), 3.81 * i, 0, 1.0, 2.0, square=(i == 0))
    courtyard(fp, -1.5, -1.5, 3.81 * 2 + 1.5, 1.5)
    save(fp, "WirePads_1x03_P3.81mm_D1.0mm", "Three solder pads for short wires")

    fp = load(KLIB / "MountingHole.pretty", "MountingHole_2.7mm_M2.5")
    save(fp, "MountingHole_2.7mm_M2.5")
    fp = load(KLIB / "NetTie.pretty", "NetTie-2_SMD_Pad0.5mm")
    save(fp, "NetTie-2_SMD_Pad0.5mm")


if __name__ == "__main__":
    main()
