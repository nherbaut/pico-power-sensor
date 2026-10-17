# Footprint review, revision 1

Date: 2026-10-16. Library: `hardware/kicad/lib/picopower-proto.pretty`, built by `hardware/kicad/gen_footprints.py` from KiCad 9.0.9 stock footprints or from the cited drawing. This is a documentary comparison by Claude, not a check against delivered parts. Every footprint below still needs a test fit with the actual part before fabrication release.

| Footprint | Used by | Derived from | Changes and basis | Status |
|---|---|---|---|---|
| Fuseholder_Schurter_0031.8201_P22.5mm_D1.35mm | interposer F1 | Stock `Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open` | Drill 1.30→1.35 mm, pads 3.00 mm (owner exception); central 2.7 mm NPTH removed (exception does not authorise it); courtyard set to the 25 × 10.8 mm installation envelope + 0.25 mm (docs/protection-options.md) | Documentary match |
| TerminalBlock_WE_691137710002_P5.00mm_D1.35mm | interposer J1 | Drawn from Würth drawing rev 001.002 | 2 pads, 5.00 mm pitch, 1.35 mm holes / 3.00 mm pads (owner exception); body 10 × 7.5 mm with pins 4.0 mm from the wire-entry face | Documentary; maximum lead size unverified |
| TO-220-3_Horizontal_TabDown_GDS_D1.2mm | interposer Q1 | Stock `TO-220-3_Horizontal_TabDown` | Pads renamed G/D/S (Infineon TO-220 pinout 1 G, 2 D, 3 S); drill 1.10 → 1.20 mm for a calculated maximum lead diagonal of about 1.05 mm (0.86 × 0.6 mm, Infineon PG-TO220-3 drawing values to confirm); pads 2.0 mm; tab mounting hole removed | Documentary; **1.2 mm drill needs an owner hole exception** |
| Socket_Samtec_SSQ-102_1x02_P2.54mm_D1.10mm (no longer used) | — | Stock `PinSocket_1x02_P2.54mm_Vertical` | Drill 1.10 mm, pads 2.00 mm (owner exception) | Documentary |
| R_Shunt_Bourns_MSR1_P11.40mm_Kelvin | interposer R1 | Drawn from Bourns MSR datasheet | Leads 11.4 mm apart, 1.30 mm holes / 3.00 mm pads (owner exception); pads 2/3 are 1.0 mm top-copper Kelvin pickups at the inner edge of each lead pad, declared as net-tie pad groups 1+2 and 3+4. Lead spacing tolerance +1.0/−0.5 mm means leads may need forming | Documentary |
| PiStack_Adafruit2223_2x20_P2.54mm_D1.10mm | interposer J2 | Inherited `picopower` Stack_2x20 | Pad centres unchanged; drill 1.00→1.10 mm, pads 2.00 mm (owner exception) | Pad centres match the inherited board |
| Socket_Harwin_M20-782_1x08/1x09/1x20_P2.54mm | carrier J1–J5 | Stock `PinSocket_1xNN_P2.54mm_Vertical` | Drill 1.00 mm (Harwin recommends 1.02 ±0.05; calculated tail diagonal 0.783 mm), pads 1.8 mm | Documentary |
| JST_XH_B4B/B5B-XH-A_…_1.8mm | both boards | Stock JST XH vertical | Pads grown from 1.7 × 1.95 to 1.8 × 1.95 mm; drill 0.95 mm kept | Stock land, pad grown |
| R_Axial_L6.5mm_D2.5mm_P10.16mm_Horizontal_1.8mm | interposer R2–R7 | Stock DIN0207 10.16 mm | Pads 1.6→1.8 mm, drill 0.8 mm (PR01 leads 0.58 ±0.05 mm, MRS25 0.6 mm nominal) | Documentary |
| R_Axial_L6.5mm_D2.5mm_P2.54mm_Vertical_1.8mm | carrier R1–R10 | Stock DIN0207 2.54 mm vertical | Pads 1.6→1.8 mm. Resistors stand upright; one lead is bent back | Documentary |
| DIP-14_W7.62mm_Socket_1.8mm | carrier U1 | Stock DIP-14 socket | Pads 1.6→1.8 mm. TE 1-2199298-3 drawing was not recovered | Tail size unverified |
| LED_D3.0mm | carrier D1–D5 | Stock | None; pad 1 = cathode (square) | Stock |
| C_Radial_KEMET_C315_P2.54mm | carrier C1, C2 | Stock C_Disc_D3.8mm_W2.6mm | Pitch 2.50→2.54 mm, drill 0.9 mm (lead 0.61 mm max), pads 1.8 mm; body outline assumed | Body size unverified |
| WirePads_1x03_P3.81mm_D1.0mm | carrier J6 | New | Three 1.0 mm / 2.0 mm pads for short wires | n/a |
| MountingHole_2.7mm_M2.5, NetTie-2_SMD_Pad0.5mm | both | Stock | None. Net ties are copper only; nothing is soldered there | Stock |

Pin-to-pad identity: every symbol pin number equals the footprint pad number (connectors, DIP, LED pad 1 = K = symbol pin 1, shunt pins 1/4 current and 2/3 sense). Confirmed by KiCad schematic parity with no pad mismatches on both boards.
