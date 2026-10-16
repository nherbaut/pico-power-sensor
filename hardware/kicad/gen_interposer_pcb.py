#!/usr/bin/python3
"""Generate hardware/kicad/interposer/interposer.kicad_pcb (KiCad 9, 2 layers).

Source of truth for placement and copper. Run with KiCad's Python after the
schematic netlist is current:
    /usr/bin/python3 -I hardware/kicad/gen_interposer_pcb.py

Fixed geometry is inherited from ../picopower (docs/mechanical-baseline.md):
stepped 66 x 46 outline, NPTH M2.5 holes at (5.13, 41.27) and (63.13, 41.27),
Pi header pad 1 at (10, 42.54), pad 2 at (10, 40).
Floorplan rationale: docs/interposer-layout.md.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pcbnew  # noqa: E402
from pcblib import Board  # noqa: E402

OUT = HERE / "interposer" / "interposer.kicad_pcb"
NET = HERE / "interposer" / "interposer.net"

B_PWR = 2.5     # 5 A tracks, top copper (see layout doc for the resistance check)
B_PWR_NECK = 2.0  # where a 2.5 mm track would violate clearance to a neighbour pad
SIG = 0.3


def main():
    bd = Board(NET)
    bd.rules()
    outline = [(0, 0), (66, 0), (66, 37), (67.13, 37), (67.13, 46), (0, 46)]
    bd.outline(outline)
    bd.place("H1", 5.13, 41.27, fpname="MountingHole_2.7mm_M2.5", board_only=True)
    bd.place("H2", 63.13, 41.27, fpname="MountingHole_2.7mm_M2.5", board_only=True)

    # ---------------------------------------------------------- placement
    bd.place("J2", 10.0, 42.54)               # Pi stacking header (inherited)
    bd.place("J1", 61.0, 4.5, rot=270)        # bench terminal, wire entry at right edge
    bd.place("F1", 53.5, 6.0, rot=180)        # pad1 right (raw), pad2 left (fused)
    bd.place("J3", 24.0, 8.54, rot=180)       # Pololu VIN (pin1 low) / GND
    bd.place("J4", 13.84, 8.54, rot=180)      # Pololu VOUT (pin1 low) / GND
    bd.place("R1", 6.5, 15.0, rot=270)        # shunt: pad1 top, pad4 bottom
    bd.place("R2", 12.0, 19.0)                # Kelvin+ 82R
    bd.place("R3", 12.0, 22.81)               # Kelvin- 82R
    bd.place("R4", 12.54, 27.5)               # VBUS 82R
    bd.place("J5", 48.0, 15.0, rot=270)       # sense cable, pins 1-4 downward
    bd.place("J6", 30.0, 26.0)                # UART cable, pins 1-5 rightward
    bd.place("R5", 19.5, 31.5)                # Pi TX 470R
    bd.place("R6", 28.66, 35.0)               # marker 470R
    bd.place("R7", 35.0, 31.5)                # Pi RX 100k pull-down
    bd.place("NT1", 50.64, 37.0, rot=180)     # MEAS_GND_REF tie at pin 34
    bd.place("NT2", 45.56, 37.0, rot=180)     # SIGNAL_GND tie at pin 30

    P = bd.pad_xy
    bd.solid_pads("J2", {"6", "9", "14", "20", "25", "30", "34", "39"})

    # ---------------------------------------------------------- 5 A path (top)
    bd.track("/BENCH_5V1_RAW", [P("J1", "1"), (57.0, 6.0), P("F1", "1")], B_PWR)
    bd.track("/FUSED_5V1", [P("F1", "2"), (28.5, 6.0), (26.0, 8.54)], B_PWR)
    bd.track("/FUSED_5V1", [(26.0, 8.54), P("J3", "1")], B_PWR_NECK)
    bd.track("/PROTECTED_5V1", [P("J4", "1"), (10.0, 8.54)], B_PWR_NECK)
    bd.track("/PROTECTED_5V1", [(10.0, 8.54), (6.5, 12.04), (6.5, 14.4)], B_PWR)
    bd.track("/DUT_5V_POST_SHUNT", [(6.5, 27.0), (6.5, 36.0), (8.5, 38.0)], B_PWR)
    bd.track("/DUT_5V_POST_SHUNT", [(8.5, 38.0), P("J2", "2"), P("J2", "4")], B_PWR_NECK)

    # ---------------------------------------------------------- Kelvin and VBUS observation
    bd.track("/KELVIN_PLUS_SRC", [P("R1", "2"), (6.5, 19.0), P("R2", "1")], SIG)
    bd.track("/KELVIN_MINUS_SRC", [P("R1", "3"), (6.5, 22.81), P("R3", "1")], SIG)
    bd.track("/SHUNT_KELVIN_PLUS", [P("R2", "2"), (26.16, 15.0), P("J5", "1")], SIG)
    bd.track("/SHUNT_KELVIN_MINUS", [P("R3", "2"), (27.5, 22.81), (32.81, 17.5), P("J5", "2")], SIG)
    # VBUS picked up at header pin 4 on the bottom layer, under the 5 A top copper.
    bd.track("/DUT_5V_POST_SHUNT", [P("J2", "4"), P("R4", "1")], SIG, layer=pcbnew.B_Cu)
    bd.track("/DUT_VBUS_SENSE", [P("R4", "2"), (26.0, 24.16), (36.0, 24.16), (40.16, 20.0), P("J5", "3")], SIG)
    bd.track("/MEAS_GND_REF", [P("J5", "4"), (48.0, 35.5), (49.5, 37.0), P("NT1", "2")], SIG)
    bd.track("/BENCH_GND", [P("NT1", "1"), (51.14, 38.5), P("J2", "34")], 0.5)

    # ---------------------------------------------------------- UART / marker
    bd.track("/PI_GPIO14_TXD", [P("J2", "8"), (17.62, 32.5), (18.62, 31.5), P("R5", "1")], SIG)
    bd.track("/PI_TX_TO_PICO", [P("R5", "2"), (32.5, 31.5), P("J6", "2")], SIG)
    bd.track("/PI_GPIO15_RXD", [P("J2", "10"), (20.16, 33.0), (35.0, 33.0), P("R7", "1"), P("J6", "3")], SIG)
    bd.track("/PI_GPIO23_MARKER", [P("J2", "16"), (27.78, 35.88), P("R6", "1")], SIG)
    bd.track("/PI_TASK_MARKER", [P("R6", "2"), (37.5, 33.68), P("J6", "4")], SIG)
    # SIGNAL_GND leaves J6 pin 1 on the bottom layer and joins at NT2.
    bd.track("/SIGNAL_GND", [P("J6", "1"), (31.25, 27.25), (31.25, 37.0), (43.6, 37.0)], SIG, layer=pcbnew.B_Cu)
    bd.via("/SIGNAL_GND", 43.6, 37.0)
    bd.track("/SIGNAL_GND", [(43.6, 37.0), P("NT2", "2")], SIG)
    bd.track("/BENCH_GND", [P("NT2", "1"), (46.06, 38.5), P("J2", "30")], 0.5)

    # ---------------------------------------------------------- 5 A pours (top)
    # Pours widen the 5 A path beyond the guaranteed track widths above; the
    # filler keeps clearance from other nets (J3/J4 GND, Kelvin pickups, H1).
    Z = bd.zone
    F = pcbnew.F_Cu
    Z("/BENCH_5V1_RAW", F, [(50.5, 0.5), (65.5, 0.5), (65.5, 7.2), (50.5, 9.5)], spoke=1.0)
    Z("/FUSED_5V1", F, [(21.6, 7.4), (21.6, 11.2), (33.5, 11.2), (33.5, 1.0), (26.5, 1.0), (26.5, 7.4)], spoke=1.0)
    Z("/PROTECTED_5V1", F, [(2.5, 7.4), (16.2, 7.4), (16.2, 11.2), (9.6, 11.2), (9.6, 15.4), (2.5, 15.4)], spoke=1.0)
    Z("/DUT_5V_POST_SHUNT", F, [(2.5, 25.9), (10.0, 25.9), (10.0, 34.0), (14.2, 38.0), (14.2, 41.0),
                                 (2.5, 41.0)], spoke=1.0)

    # ---------------------------------------------------------- ground plane (bottom)
    bd.zone("/BENCH_GND", pcbnew.B_Cu, [(0.3, 0.3), (65.7, 0.3), (65.7, 37.3), (66.83, 37.3),
                                        (66.83, 45.7), (0.3, 45.7)])

    # ---------------------------------------------------------- silkscreen
    T = bd.text
    for ref in ("J1", "F1", "J3", "J4", "J5", "J6", "H1", "H2"):
        bd.ref_at(ref, hide=True)
    for ref in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
        bd.ref_at(ref)
    bd.ref_at("J2", 33.0, 37.6)
    bd.ref_at("NT1", 51.9, 35.6)
    bd.ref_at("NT2", 44.2, 35.6)
    T("+", 58.6, 4.5, 1.0)
    T("-", 58.6, 9.5, 1.0)
    T("J1 BENCH 5.1V", 63.3, 20.0, 0.8, rot=90)
    T("F1 6.3A F", 40.0, 11.9, 0.8)
    T("J4 VOUT", 13.84, 11.6, 0.8)
    T("J3 VIN", 24.0, 11.6, 0.8)
    T("GND", 19.0, 6.0, 0.8)
    T("I", 3.0, 20.7, 0.8)
    T("J5 SENSE", 52.6, 18.75, 0.8, rot=90)
    T("J6 UART", 35.0, 22.0, 0.8)
    T("PI 40-PIN", 33.0, 45.1, 0.8)
    T("picopower-proto interposer r1", 33.0, 20.0, 0.8, layer=pcbnew.B_SilkS)
    bd.fill_and_save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
