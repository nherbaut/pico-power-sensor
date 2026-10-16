# Selected UART interface qualification

Date: 2026-10-16. Status: **PARTIAL — owner-selected circuit, documentary review only**. The owner accepted the single SN74LV125AN option with "ok", then instructed continuation. One IC is in the provisional BOM. This review develops that authorized circuit; it does not reopen the choice. The earlier MOSFET return remains unselected.

## Circuit and implementation change

Use three channels of the socketed, USB-powered SN74LV125AN: Pi TX to Pico RX, Pi marker to Pico input, and Pico TX to Pi RX. The fourth channel is unused with its input grounded and enable inactive. The [pin contract](../hardware/review/uart-buffer-pin-contract.csv) records all fourteen pins from TI's explicit top-view diagram and pin-function table. Independent CAD corroboration and the eventual schematic-to-footprint check remain open.

The owner accepted **470 Ω nominal for all three source-side series resistors** with the subsequent "ok". The candidate specification remains 1%, replacing the preliminary 220 Ω; exact supporting MPNs remain unselected. Keep them before the exposed cable: two on the interposer and one on the carrier. This records the prototype value direction within the selected topology; it does not establish electrical qualification. Keep two carrier-side 100 kΩ pull-downs on the Pi-driven inputs, one interposer-side 100 kΩ pull-down on Pi RX, two instrument-side 10 kΩ pull-ups (Pico TX and common active-low enable), and local radial 100 nF decoupling.

The two Pi-output pull-downs use the approved measurement-boundary exception. Their nominal conservative load remains 0.2178 mW at 3.3 V with both outputs high, ignoring series resistance. The Pi RX pull-down is driven by the instrument during normal reception. The earlier allowed Pi 3.3 V pull-up is omitted. Internal pulls, leakage, switching and Pi conversion losses are additional; no fixed energy correction is adopted.

## Electrical review

TI SCES124O tables 6.3–6.5 specify an 8 mA recommended output drive limit in the 3–3.6 V supply range. At an **assumed**, unverified 3.465 V maximum rail, 220 Ω −1% permits 15.91 mA in an ideal high-output-to-ground short. A 470 Ω −1% resistor limits that scenario to **7.447 mA** and dissipates **25.80 mW**. This checks the TI output's simple ground-short case only. Pi output limits, shorts to positive supplies, opposing drivers, transient overshoot and lost ground remain unresolved.

For an ideal step into an **assumed 200 pF** lumped load, TI's 100 ns/V input-transition criterion gives a nominal series-resistance interval of approximately **437.5–490.1 Ω**, combining the preceding short-current target with ±1% resistance tolerance and a conservative instantaneous slope throughout a chosen 30–70% transition window at 3.3 V. This window is a review assumption, not an independently verified TI test method. The proposed 470 Ω fits that conditional interval: calculated 10–90% rise is 208.6 ns and average 30–70% slope is 60.94 ns/V at +1% resistance; the slowest instantaneous slope within that window is 95.90 ns/V. At 200 pF, only 20.3 Ω of additional source resistance fits that latter screen. At a hypothetical low rail of 3.135 V, the same 200 pF / 470 Ω +1% case reaches 100.95 ns/V and misses that instantaneous screen. With zero source impedance, capacitance must be below about 198.1 pF for this lower-rail scenario; real source impedance reduces the allowance further. The 470 Ω proposal therefore remains conditional on a smaller verified load or a revised edge analysis. Source impedance, distributed cable behavior, capacitance and actual transition limits must be checked; this is neither a measured waveform nor a guaranteed baud rate.

| Path/check | Finding | Remaining evidence |
|---|---|---|
| Pico TX to buffer | Nominal 3.3 V table comparison gives 0.31 V high and 0.49 V low margin | Complete rail/temperature/load comparison; actual GPIO configuration |
| Buffer to Pico RX/marker | Same local supply; configure receivers for driven signals, not floating inputs | Output loading, enabled/disabled states and A2 erratum handling |
| Pi TX/marker to buffer; buffer to Pi RX | RP1 documentation identifies fault-tolerant pads and their off-state voltage condition | Numerical RP1 logic limits were not found in the retained GPIO/pad document or targeted official-source search; manufacturer evidence is still needed for guaranteed margins |
| Common enable default | At 3.3 V, 10 kΩ +1%, a 36 kΩ Pico pull-down and an assumed total 4 µA sink leakage give 2.545 V, 0.235 V above the buffer's 2.31 V high threshold | Leakage endpoint conditions do not establish a full intermediate-voltage bound; verify the actual default pad state, control capacitance and rail ramp |
| Pi powered off, Pico on | RP1 describes low-current input operation below 3.63 V with IOVDD=0 | Actual rail maximum, ringing, off-rail rise and all supply transitions |
| Pi on, Pico off | TI's VCC=0 input/output leakage specification supports partial-power-down screening | Actual off-rail voltage, receiver bias and cable-return behavior |

The 100 kΩ Pi-RX pull-down does **not** establish a guaranteed low level while the buffer is disabled. The Pi's internal pulls and both devices' leakage matter; disable unintended Pi pulls and qualify this state. If the receiver is low, interpret it as break/link unavailable. Avoid a serial console or break-triggered command on this port. The RP1 draft's qualitative off-current wording is not a zero-current guarantee.

## Startup and shutdown contract

1. Keep common `UART_OE_N` high during initialization. Preload its GPIO output latch high before enabling that output. Keep the buffer's fourth enable tied directly to instrument 3.3 V.
2. Configure normal, non-inverted Pico UART TX and establish idle high before enabling the buffer. The earlier transistor circuit's output inversion must not be used.
3. Configure Pico receiver pins while the buffer is disabled. On RP2350 A2, erratum E9 can defeat a weak pull-down on an enabled input; use disabled input buffers or the documented pull-up behavior until a valid driven level exists. A3 fixes E9, but actual board silicon remains unverified. The 100 kΩ resistors are on TI inputs and do not solve a Pico-pad erratum.
4. Enable the used channels by driving `UART_OE_N` low, then enable valid packet/marker capture. Discard initialization edges and framing errors; require a successful link exchange before accepting task markers.
5. On controlled shutdown, stop acquisition, mark the link invalid and disable the buffer before changing peripheral pin functions. Unexpected power loss and brownout require separate testing; software cannot guarantee those transitions.

The [carrier integration map](carrier-integration.md) allocates Pico GP0 TX, GP1 RX, GP2 marker and GP3 active-low enable. Pi-side GPIO numbers remain open pending the exact HAT and UART configuration. Keep receiving pins in the documented digital FT set. A firmware reset is not a substitute for a hardware power-state check.

| Pi | Pico USB | Intended state; still to qualify |
|---|---|---|
| On | On | Normal three-channel communication after initialization/link exchange |
| On | Off | Buffer unpowered; no valid communication; determine Pi RX level and Pico off-rail rise |
| Off | On | Pi-driven inputs biased toward reference; instrument return may be high only within RP1's off-state conditions; data invalid |
| Off | Off | No intended positive source; check any other connected peripheral or earth paths |
| Transitioning | Either | Data invalid; observe all receiver pins, enables and rails during ramps, reset and decay |

## Supporting-part screen

The [candidate CSV](../hardware/uart-support-candidates.csv) contains exact codes and quantities for the eight resistors, capacitor and socket. They are **unselected candidates**, not extra approved BOM entries. The resistor and capacitor primary documents are retained in `hardware/evidence/uart/`.

| Role | Candidate | Documentary result |
|---|---|---|
| Three 470 Ω series resistors | Vishay MRS25000C4700FCT00 | Axial MRS25, 1%; family drawing gives 6.5 mm maximum body length, 2.5 mm diameter and 10 mm minimum mounting pitch. Use a proposed 10.16 mm pitch; 0.6 mm lead dimension is nominal, so maximum lead fit remains open |
| Two 10 kΩ pull-ups | Vishay MRS25000C1002FCT00 | Same family and mechanical screen |
| Three 100 kΩ pull-downs | Vishay MRS25000C1003FCT00 | Same family and mechanical screen |
| One 100 nF bypass | KEMET C315C104K5R5TA | Exact-code sheet: radial X7R, ±10%, 50 V, 2.54 mm nominal pitch, 0.61 mm maximum lead diameter. A proposed 0.9 mm finished hole with assumed ±0.05 mm tolerance leaves 0.24 mm diametral clearance; actual insertion and placement remain open |
| One DIP-14 socket | TE 1-2199298-3 | Manufacturer exact-code page says Active, 2.54 mm pitch and 7.62 mm row spacing. Customer drawing was located but not visually recovered: direct downloads returned 403, and the web text extraction has no drawing text. Maximum tail envelope and board footprint remain unverified; no dimensions inferred from the retail photograph |

Use pads at least 1.8 mm across and maintain solder-tip access; no custom footprint or hole exception is established here. The family resistor datasheet and exact capacitor sheet do not independently establish current exact-code lifecycle status. The socket's manufacturer lifecycle status is distinct from its direct-store availability. Distributor listings corroborate that the proposed resistor ordering codes exist; do not promote their Active labels to manufacturer evidence. No purchasing or inventory-account access was performed.

Reserve **1 mA provisionally within the existing 10 mA carrier/interface allocation**, rather than adding it twice to the 235 mA carrier budget. A conservative independent sum of the two 10 kΩ pull-up loads and the Pi-RX 100 kΩ load is 0.735 mA at the assumed +5% rail/−1% resistance. This is not a complete current bound: buffer switching, internal pulls, faults and actual signal activity remain to be included.

## Completion status

The owner choice, proposed connectivity, reset sequence, resistor calculation and candidate list are now recorded. [Qualification rows](../hardware/review/uart-interface-qualification.csv) keep source gaps, unverified footprints and hardware checks visible. Exact support-part lifecycle/fit, RP1 margins, complete pin allocation and fault/transition validation remain open. No schematic, ERC, DRC, parity, simulation or physical measurement has been performed in this review. Fabrication and Pi connection remain subject to AGENTS.md's completed-release-checklist requirement.

## Owner decision on supporting parts

On 2026-10-16 the owner approved the supporting-part set listed above ("yes"): three MRS25000C4700FCT00, two MRS25000C1002FCT00, three MRS25000C1003FCT00, one additional C315C104K5R5TA and one TE 1-2199298-3 socket. They are in the [provisional BOM](../hardware/bom.csv). Lifecycle, lead-fit and socket-drawing gaps above remain open.
