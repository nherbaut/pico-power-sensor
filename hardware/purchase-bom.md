# BOM d'achat

Quantités pour un exemplaire de chaque carte. Les PCB et une carte microSD ne sont pas inclus.

**Ligne 4 (Q1) : Vishay Si4143DY-T1-GE3 (SO-8), choisi le 2026-10-17** après l'arrêt de l'IPP80P03P4L-04 ; Farnell 3470713 (lot de 5). Voir [la revue Q1](../docs/q1-resolution-2026-10-17.md).

| # | Carte | Repères schéma | Qté | Fabricant | Référence | Description | Distributeur | Réf. distributeur |
|---|---|---|---|---|---|---|---|---|
| 1 | interposer | J1 | 1 | Würth Elektronik | 691137710002 | Bornier à vis 2 pos., pas 5,00 mm, entrée bench | Farnell | 3767630 |
| 2 | interposer | F1 (cartouche) | 1 | Littelfuse | 021706.3MXP | Fusible rapide 6,3 A, 5×20 mm | Farnell | 1354579 |
| 3 | interposer | F1 (porte-fusible) | 1 | Schurter | 0031.8201.G | Porte-fusible 5×20 ouvert, traversant (OGN) | Farnell | 4763851 |
| 4 | interposer | Q1 | 1 (lot de 5) | Vishay | Si4143DY-T1-GE3 | MOSFET canal P 30 V, SO-8 (remplace le module Pololu 5383) | Farnell | 3470713 (lot de 5) |
| 5 | interposer | — | 0 | — | — | Ligne supprimée (module Pololu remplacé par Q1, ligne 4) |  |  |
| 6 | interposer | — | 0 | — | — | Ligne supprimée (module Pololu remplacé par Q1, ligne 4) |  |  |
| 7 | interposer | R1 | 1 | Bourns / Riedon | MSR1-0R005F1 | Shunt 5 mΩ 1 % 1 W traversant | Farnell | 4582734 |
| 8 | interposer | R2, R3, R4 | 3 | Vishay | PR01000108209JA100 (ou JR500) | Résistance 82 Ω 5 % 1 W axiale | Farnell | 3547179 |
| 9 | interposer + carrier | interposer R5, R6 ; carrier R1 | 3 | Vishay | MRS25000C4700FCT00 | Résistance 470 Ω 1 % axiale | Farnell | 9468463 |
| 10 | interposer + carrier | interposer R7 ; carrier R2, R3 | 3 | Vishay | MRS25000C1003FCT00 | Résistance 100 kΩ 1 % axiale | Farnell | 9463895 |
| 11 | interposer + carrier | interposer J5 ; carrier J7 | 2 | JST | B4B-XH-A | Embase JST-XH 4 pos. verticale | Mouser | 306-B4BXHALFSN |
| 12 | interposer + carrier | interposer J6 ; carrier J8 | 2 | JST | B5B-XH-A | Embase JST-XH 5 pos. verticale | Mouser | 306-B5BXHALFSN |
| 13 | interposer + HAT | interposer J2 ; rehausse HAT | 2 | Adafruit | 2223 | Connecteur empilable 2×20 (version broches carrées) | Mouser | 485-2223 |
| 14 | carrier | J1, J2 | 2 | Harwin | M20-7822042 | Support femelle 20 pos., 2,54 mm (Pico) | Farnell | 3755879 |
| 15 | carrier | J3, J4 | 2 | Harwin | M20-7820842 | Support femelle 8 pos., 2,54 mm (MikroE) | Farnell | 3225927 |
| 16 | carrier | J5 | 1 | Harwin | M20-7820942 | Support femelle 9 pos., 2,54 mm (microSD) | Farnell | 4169557 |
| 17 | carrier | C1, C2 | 2 | KEMET | C315C104K5R5TA | Condensateur céramique 100 nF 50 V X7R radial | Farnell | 4552016 |
| 18 | carrier | U1 (circuit) | 1 | Texas Instruments | SN74LV125AN | Buffer 4 voies 3 états, DIP-14 | Mouser | 595-SN74LV125AN |
| 19 | carrier | U1 (support) | 1 | TE Connectivity | 1-2199298-3 | Support DIP-14 | Farnell | 2445621 |
| 20 | carrier | interposer R8 ; carrier R4, R5 | 3 | Vishay | MRS25000C1002FCT00 | Résistance 10 kΩ 1 % axiale | Farnell | 9463976 |
| 21 | carrier | R6 à R10 | 5 | Vishay | MRS25000C1801FCT00 | Résistance 1,8 kΩ 1 % axiale | Farnell | 9465448 |
| 22 | carrier | D1 à D5 | 5 | Vishay | TLLR4401 | LED rouge 3 mm faible courant | Farnell | 1045504 |
| 23 | carrier | (enfiché sur J1/J2) | 1 | Raspberry Pi | Pico 2 WH | Pico 2 W avec connecteurs soudés | Farnell | 4667138 |
| 24 | carrier | (enfiché sur J3/J4) | 1 | MikroElektronika | MIKROE-4810 | Power Monitor Click (INA228) | Farnell | 4922643 |
| 25 | carrier | (enfiché sur J5, dessous) | 1 | Adafruit | 4682 | Module microSD SPI/SDIO | Mouser | 485-4682 |
| 26 | câbles | boîtiers câble capteur | 2 | JST | XHP-4 | Boîtier femelle JST-XH 4 pos. | Mouser | 306-XHP-4 |
| 27 | câbles | boîtiers câble UART | 2 | JST | XHP-5 | Boîtier femelle JST-XH 5 pos. | Mouser | 306-XHP-5 |
| 28 | câbles | fils serti-serti | 8 | JST | ASXHSXH22K152 | Fil pré-serti XH-XH 22 AWG, 152 mm | Mouser | 306-ASXHSXH22K152 |
| 29 | mécanique | entretoises HAT | 1 | Adafruit | 3658 | Kit entretoises/vis nylon M2,5 (longueurs à ajuster au montage) | Mouser | 485-3658 |
