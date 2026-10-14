# Electrical acceptance

Perform initial tests with an appropriately rated dummy/electronic load, not a Pi.

1. Verify every header contact and input polarity against the [pinout](../../hardware/pcb/interposer/pinout.csv). Both 5 V contacts must be connected; no 3V3/GPIO contact may join the supply path.
2. Verify that the only path from PROTECTED to PI_5V is through RSH1. Check all Kelvin leads and ensure no other resistor or shunt is connected across the sense pair.
3. Measure input-fault disconnect and recovery thresholds slowly. Compare against resistor/comparator tolerance, leakage and hysteresis calculations. Observe output overshoot with a scope.
4. Test reversed input and excessive voltage incrementally within the reviewed circuit envelope. First verify with no load and then a resistor load. Stop if any rating or behavior is uncertain. Never perform fault injection with a Pi attached.
5. Check startup/inrush, output-off behavior and reconnect. Verify the gate slew branch against actual output capacitance and MOSFET SOA; no high-voltage hot-plug guarantee is claimed.
6. At 0.5, 1, 3 and 5 A, measure power-path drop and individual contact temperature. Provisional targets (decision 2026-10-15, to be confirmed on the bench): at least 4.8 V at the header with the Korad at 5.10 V and 5 A, with the measured input-to-header drop recorded, less than 30 C temperature rise at contacts/copper, and every part below its derated temperature/power rating after thermal stabilization. Revise the design if these cannot be met.
7. Check fault coordination: a 6.3 A fuse need not open with the Korad limited to 5 A. Record constant-current behavior and voltage collapse; reject such operation during measurement runs.
8. Verify no alternate supply path from USB devices, instrument signal lines or ground/reference equipment. UART must not power an unpowered Pi.

Record scope captures and measured data. A source-level check is not a passed electrical acceptance test.

## Power-off buffer acceptance

These are pending physical tests; ERC/DRC cannot establish power-off performance. Start with a fixture representing the two 3.3 V domains and logic endpoints, before connecting a Pi.

- Verify separate PICO_3V3 and PI_3V3 nets, all J4 contacts, fixed bank directions, local bias and lack of direct UART/marker bypasses. Confirm the five-pin connector cannot mate with the measurement cable.
- With both sides powered, loop commands/replies at 115200 baud, 8N1. Scope the Pi-to-Pico marker and verify UART idle-high and marker idle-low. Check normal levels and propagation without spurious pulses.
- Exercise Pi-only, Pico-only and both-off states, both startup orders and repeated power cycles. Drive powered-side signals high and low. Scope naturally decaying off-side rails: demonstrate that the rail falls below 100 mV without externally clamping it, and does not remain partially powered through the cable. Record decay time and observed UART/marker transitions. Linux shutdown with 3.3 V still present is not an off-rail test.
- Separately measure off-state per-signal leakage with the relevant supply held at 0 V in a controlled fixture. Compare with the applicable datasheet limit (up to 8 uA per signal over the full rated temperature range); do not confuse intentional bias current with leakage. The forced-zero fixture does not replace the natural rail-decay test.
- Test slow ramp-down/brownout as well as abrupt removal. Flag communication and marker edges during transitions as invalid; the design does not promise valid logic throughout brownout.
- Measure Pi-side and Pico-side idle and active interface consumption. Record overhead with both idle and representative UART/marker traffic; retain raw energy. Fail release if the off-side rail remains powered, signals inject excess leakage, or the buffers do not disconnect as specified.
