# Design decisions

Decisions record what is selected, why, and what still needs evidence. A draft drawing is not a validated implementation.

| Decision | Status |
|---|---|
| English NoiseNet-style site and hardware tracking | Selected |
| Pico 2 W, direct INA229 SPI, Linux development | Selected |
| Korad U202 supplies Pi 5 at 5.1 V | User equipment; bench validation pending |
| Custom side-wing interposer with fuse and four-terminal shunt | Selected |
| Preserve AI HAT+ / AI HAT+ 2 and Active Cooler use | Required; fit pending |
| No voltage converter in measured supply path | Selected |
| Upstream LTC4367 protection switch | Recommended draft default; preference can still be revised |
| Separate INA229EVM and Pico for first revision | Superseded 2026-10-14 by the on-carrier INA229 |
| INA229 soldered on the carrier; no evaluation board | Selected 2026-10-14; carrier grows to 78 x 54 mm; layout and footprint review pending |
| Generic commands, software matrix, short connected runs | Planned software milestone |
| PostgreSQL metadata/metrics and raw trace files | Planned software milestone |

For a revision, record date, alternatives, evidence, chosen behavior and affected calibration/assembly records. Do not overwrite historical results after changing hardware.

The user accepted a Pi-powered side of the dual-supply UART/marker buffer on 2026-10-14. Its overhead is included in DUT current and must be characterized. J4 changes to five-pin JST-XH to carry the independent Pico 3.3 V supply and distinguish it from J3. A Pico carrier is a subsequent hardware addition using this interface.
