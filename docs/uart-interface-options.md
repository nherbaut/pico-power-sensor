# UART and task-marker interface: approved bias exception

Date: 2026-10-16. **Owner-approved single SN74LV125AN circuit and earlier bias exception; supporting-part selection and electrical qualification remain open.** The owner authorized interface work, then asked why powered-off behavior matters. The concern is one independently powered board driving another while it is off; both boards off with no other source is a different case. A driven input can inject current into an unpowered receiver depending on its pad design. The Pi 5 and Pico 2 have documented fault-tolerant digital pads, discussed below; the earlier generic concern alone does not establish that their ordinary 3.3 V signaling needs a transistor return. Assembled behavior has not been measured.

## Measurement-boundary decision

The owner approved a scoped exception with "ok" on 2026-10-16: **one 10 kΩ pull-up from Pi UART RX to Pi 3.3 V and two 100 kΩ pull-downs on Pi TX/task-marker inputs** may contribute to reported DUT consumption. Keep buffer operating power and the MOSFET gate-drive network on instrument USB power. Other auxiliary loads remain subject to AGENTS.md's exclusion rule; no Pi-powered buffer IC is approved.

The reported measurement boundary now includes that communication load, with the buffer IC and other active interface supplies on Pico USB power. Nominal conservative DC accounting is **1.3068 mW on the 3.3 V side**, with the UART return low and both Pi outputs high, before leakage and switching. This is a calculation, not measured bench-supply overhead or a full worst-case bound. At nominal 3.3 V the bound uses 330 µA for the 10 kΩ pull-up and 33 µA for each 100 kΩ pull-down, deliberately ignoring series resistances that reduce current. At a hypothetical +5% rail and -1% resistors, the same calculation is 1.46 mW. Those rail limits are assumptions, not established Pi limits. The Pi's conversion loss, internal pulls, input leakage and switching add uncertainty. Do not subtract a fixed value from measured energy or silently call it pure Pi consumption.

| Option | Result | Requirement consequence |
|---|---|---|
| Approved bias allowance, initially proposed for a USB-powered buffer plus open-drain return | Retains the bidirectional UART and hardware-marker design direction; DIP/TO-92/passives; no active Pi-powered IC | Named pull-up/input-bias exception approved; exact devices and electrical qualification remain open; use of every allowed resistor is not mandatory |
| Earlier alternative: retain strict boundary and investigate further | Not chosen after approval of the narrow bias exception | No completed alternative wired return path was established in this screen. Pi-powered isolators/level shifters would also add DUT consumption |
| Manual connection sequence instead of automatic mixed-power tolerance | Connect UART only after both supplies are valid; unplug before changing either supply | Changes the powered-off operating requirement and does not cover unexpected power loss; not recommended as equivalent protection |

The subsequent "ok" authorizes the named bias exception. It does not approve the manual-sequence alternative, exact devices or hardware energizing. Selected connectors and the fifth empty cable cavity remain unchanged.

## Owner-selected circuit: one buffer for all three signals

The [RP1 peripheral document](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf), build b9b6f74-clean (2023-11-07, marked DRAFT), section 3.1.3, printed page 17 / PDF page 18, describes low-current input behavior below **3.63 V with IOVDD=0**. RP1 drives the Pi 5's header GPIOs. This supports investigating an instrument-powered return driver. It is a qualitative leakage description, not a numerical off-current guarantee or a complete interface qualification.

The retained [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), build 80d627281ed5 (2026-10-01), tables 1673–1674, distinguishes fault-tolerant digital pads from analog-capable pads. QFN-60 GPIO0–25 are digital FT; GPIO26–29 are not. The FT specification also covers IOVDD=0 up to 3.63 V. Choose exposed Pico digital GPIOs and verify the module mapping; do not generalize this to ADC pins or older Raspberry Pis.

**Owner-selected prototype circuit ("ok", 2026-10-16):** use three channels of **SN74LV125AN**, powered by the Pico's USB-derived 3.3 V, for Pi TX → Pico RX, Pi marker → Pico input and Pico TX → Pi RX. Omit TN0702N3-G and the Pi-side 10 kΩ pull-up. This removes the inversion and open-drain rise-time dependency. The existing approved two 100 kΩ Pi-output pull-downs remain: their calculated nominal load is **0.2178 mW** with both Pi outputs high, plus leakage, switching, internal pulls and Pi conversion losses. The broader approved bias allowance remains permission, not a requirement to draw its full nominal amount.

Proposed connections, using the TI N-package top-view pin numbering. The follow-up [qualification review](uart-interface-qualification.md) records the owner-accepted 470 Ω nominal direction instead of the original 220 Ω series resistors for the stated short-current/edge-rate screen:

| Path/function | Proposed connection |
|---|---|
| Pi TX and marker | Each interposer output → 470 Ω before the cable → carrier input, with 100 kΩ to reference; inputs A1=2 / A2=5, outputs Y1=3 / Y2=6 to Pico RX / marker |
| Pico return | Pico TX → A3=9, with instrument-side 10 kΩ to instrument 3.3 V; Y3=8 → carrier 470 Ω before cable pin 3 → Pi RX |
| Pi RX when driver disabled | Proposed 100 kΩ to reference on interposer, powered by the USB buffer when driven high; no Pi-positive pull-up. A low receiver is a link-unavailable/break state, not UART idle; actual off-state leakage and threshold margin remain open |
| Enables | Tie used active-low enables 1, 4 and 10 together; 10 kΩ to instrument 3.3 V and a separate Pico enable GPIO. Firmware enables only after TX idle and receiver configuration are valid. Verify reset/brownout behavior; a resistor is not a complete sequencing guarantee |
| Supply / unused channel | VCC=14, GND=7, local radial 100 nF; unused A4=12 to ground, OE4=13 to instrument 3.3 V, Y4=11 unconnected |

This uses one socketed DIP-14, one radial capacitor and eight axial resistors: three 470 Ω, three 100 kΩ and two 10 kΩ. Exact passive/socket MPNs and footprints remain open. All positive bias supplies on this candidate's carrier come from USB. Pi 3.3 V is not a cable conductor.

The RP2350 document's table 1683 gives VIH≥2 V and VIL≤0.8 V at IOVDD=3.3 V; its VOH minimum is 2.62 V and VOL maximum 0.5 V under the listed drive tests. TI's 3–3.6 V input thresholds are 0.7×VCC and 0.3×VCC. Nominal comparisons support screening, but complete independent-rail margins remain unfinished, especially the numerical RP1 output/input limits, which were not located in the retained RP1 document. Do not substitute older Pi/BCM2835 limits.

RP2350 erratum **E9 affects A2**, with excessive sourcing current for enabled inputs in the undefined region; a weak pull-down may fail. A3 fixes it. Read the actual Pico revision; keep receivers disabled or suitably pulled until buffers drive valid levels. The document's external pull-down workaround is ≤8.2 kΩ, not the proposed 100 kΩ on the *TI input*. That TI-input resistor does not claim to solve an RP2350 receiver-pad erratum. No numeric graph values were extracted.

For the new return, qualify the actual USB-derived rail maximum **and signal overshoot** against the Pi's below-3.63 V off-state condition. A hypothetical 3.3 V +5% gives 3.465 V and only 165 mV of headroom; neither tolerance nor overshoot is established. At power loss, tri-state/leakage, transient rail behavior and invalid packets remain bench gates. Disable the Pi serial console and any break-triggered control for this proposed port; invalidate startup data and marker capture until ready. No firmware or GPIO allocation exists yet.

| Candidate | Comparison and current disposition |
|---|---|
| Three channels of one USB-powered SN74LV125AN | **Owner-selected for subsequent qualification**; one active DIP, no output inversion, lower nominal DUT bias; relies on Pi 5-specific pad documentation and a bounded signal voltage |
| Earlier two-channel buffer plus TN0702N3-G return | Retained alternative below; return does not actively source Pi RX, but adds a transistor, pull-up load, inversion, RC timing and temperature/leakage questions |
| Direct series-resistor GPIO links | Potentially cheaper: both chips document suitable digital FT pads under stated conditions. Not completed here; default bias, E9, transitions and waveforms still need review. The buffer is not claimed to be uniquely required for safety |

## Earlier conditional circuit: buffer plus open-drain return

The following earlier alternative is retained for comparison and is not selected. The selected BOM contains SN74LV125AN for the three-channel circuit above; it contains no TN0702N3-G. Exact passive/socket codes and schematic capture remain open.

**Pi to Pico, two paths:** Pi UART TX and task marker each feed a 220 Ω series resistor on the interposer, before the exposed cable. At the carrier, each line has a 100 kΩ pull-down to the common reference and drives one input of **TI SN74LV125AN**, powered from instrument 3.3 V. Buffer outputs feed the Pico UART RX and marker input in the same supply domain. The two used active-low enables connect to instrument ground. Unused inputs connect to ground, unused enables to instrument 3.3 V, and unused outputs are unconnected. Add 100 nF across the IC supply pins, close to the socket. The two input pull-downs are covered by the approved Pi-output loading exception; they are not pull-ups to the instrument rail.

**Pico to Pi:** a carrier-side **Microchip TN0702N3-G** has source to common reference, drain to cable pin 3, and gate driven through 220 Ω from the Pico UART TX pin. A 100 kΩ gate pull-down is instrument-side and keeps the transistor off while the Pico pin is undriven. On the interposer, connect the cable through 1 kΩ to Pi UART RX, with **10 kΩ from Pi RX to Pi 3.3 V**. That last resistor is covered by the approved Pi-side pull-up exception. Pi 3.3 V does not become a separate positive supply conductor in the cable. No instrument-powered push-pull output connects directly to Pi RX.

This transistor stage inverts the signal. The intended firmware uses the Pico SDK's `gpio_set_outover(tx_gpio, GPIO_OVERRIDE_INVERT)` so UART idle makes the gate low and Pi RX high. The [official SDK documentation](https://www.raspberrypi.com/documentation/pico-sdk/hardware.html) documents this peripheral-output override for RP-series GPIO. Actual pin assignment, startup ordering and waveform validation remain open. Initialize without a spurious gate-high interval; a reset or disabled peripheral must release the transistor. UART and marker behavior during startup must be invalidated until both ends and the monitor are ready.

Start qualification at a proposed **38,400 baud**, not an adopted performance requirement. For a deliberately assumed 200 pF return-line capacitance, 10 kΩ gives a 2 µs RC constant and 4.39 µs 10–90% rise time, compared with a 26.04 µs bit period. Capacitance, Pi input thresholds and sampling margin have not been established, so this is a planning example, not a baud-rate pass. Marker timing has two components: hardware propagation and software task-marker generation/capture. Neither is currently bounded.

## Source-grounded device screen

| Item | Documentary support | Limits of this screen |
|---|---|---|
| SN74LV125AN, PDIP-14 | TI SCES124O, May 2022, pages 3–6: 2–5.5 V operation; recommended 0–5.5 V inputs; input current ±1 µA at stated test endpoints; power-off leakage 5 µA at VCC=0 with VI/VO=0–5.5 V. Current packaging addendum explicitly lists exact N order code Active | Powered-off protection is not zero leakage. Startup/brownout between 0 and the valid supply range, Pi/Pico logic margins and actual off-rail voltage remain unverified. Ordinary CMOS inputs have a 100 ns/V input-transition limit in the 3–3.6 V supply range; cable waveform qualification is required |
| TN0702N3-G, TO-92 | Microchip DS20005941A, pages 2, 6 and 9: explicit source=1, gate=2, drain=3; 20 V minimum breakdown under stated test; maximum RDS(on)=5 Ω at VGS=2 V, ID=50 mA, 25°C pulse conditions | Gate threshold alone is not the conduction criterion. This resistance is a table reference, not an installed hot-switching bound. Gate leakage is specified at ±20 V gate/source and VDS=0; it does not prove every cross-terminal power-state leakage path |
| Exact lifecycle | TI exact SN74LV125AN [product page](https://www.ti.com/product/SN74LV125A/part-details/SN74LV125AN) and addendum identify Active. Microchip [TN0702 page](https://www.microchip.com/en-us/product/tn0702) says In Production; PDF names N3-G example | Exact Microchip ordering-code lifecycle confirmation remains incomplete; family status and distributor Active are not promoted to exact-code evidence |
| Hand assembly | Buffer is a socketable 14-pin DIP; MOSFET is TO-92; resistors axial and capacitor radial | Socket/passive MPNs, manufacturer footprint comparisons and placement remain open. TN0702's front/bottom package views must not be confused when creating a footprint |

The TI reference application on datasheet page 10 buffers a separately supplied logic source into a locally powered receiver; its supply-decoupling recommendation is on page 11. This earlier alternative uses two channels and a transistor return. The new recommendation uses a third channel, conditional on the Pi-specific pad constraints above. Neither is claimed as a complete manufacturer Pi/Pico reference circuit. No numerical graph values were read.

At nominal values, the return's 1 kΩ series resistor and a hypothetical 5 Ω MOSFET give a calculated low level of about 0.301 V with a 3.3 V / 10 kΩ pull-up. The series resistor reduces contention current if Pi RX is accidentally configured as an output, but no comprehensive misconfiguration/fault pass is claimed. The MOSFET's hot off-state drain-leakage table allows 100 µA at 125°C under its specified voltage condition; do not use the room-temperature 100 nA entry for all temperatures. Logic thresholds and the resulting worst-case high level still need a proper Pi 5 / Pico electrical comparison.

## Earlier circuit's intended power-state behavior and common remaining faults

| Pi power | Pico USB | Intended behavior; evidence still needed |
|---|---|---|
| On | On | Buffered TX/marker, open-drain return; verify both logic margins, baud rate, marker timing, pull configuration and added consumption |
| On | Off | TI input power-off specification limits the two incoming signal loads; MOSFET gate pull-down releases return and Pi pull-up maintains idle. Measure actual instrument off-rail rise and gate state |
| Off | On | No instrument-powered high driver on Pi RX; MOSFET can only pull toward common reference. Verify gate-drain capacitive transients, leakage and receiver-pin/off-rail voltages |
| Off | Off | No intended positive source; connected USB/peripherals/earth can change this assumption. Verify continuity and external return paths |
| Either transitioning | Either | No valid data assumed. Verify reset, brownout, rail decay and output behavior over transitions; static endpoint specifications alone do not qualify these cases |

This is not galvanic isolation. The signal and sense grounds can still create parallel return paths; neither cable is the intended DUT power return. The circuit is **not qualified for exposed-pin shorts to 5 V, reversed bench wiring, arbitrary connector miswiring, ESD or disconnection of the main ground**. Series resistors do not by themselves prove an unpowered rail can absorb fault current. Keep these as open design/bench gates, rather than claiming complete protection because the nominal mixed-power topology is better behaved.

Future validation starts without the Pi: continuity, equivalent source/receiver fixtures, all four static power states, slow/fast supply transitions, injected-current/off-rail measurements, UART idle and complete packets, marker edges, then the required release review before actual Pi connection. No such hardware work is authorized or performed here.

## Cost and decision scope

Indicative exact-code observations: [SN74LV125AN at Mouser Spain](https://www.mouser.es/en/ProductDetail/Texas-Instruments/SN74LV125AN?qs=sGAEpiMZZMv4BkFy%252BbL2aJtUL1iLY3rYzVkG0jFiXfo%3D), €0.817 excluding assumed VAT, about one month old; [TN0702N3-G at DigiKey France](https://www.digikey.fr/fr/products/detail/microchip-technology/TN0702N3-G/4902376), €1.33 excluding VAT, about three months old, 1,867 stock in that indexed observation. **Main devices only: €2.147 excluding VAT, €2.5764 at assumed 20% VAT.** This is not the complete interface cost: socket, capacitor, eight resistors, wire/assembly and delivery are additional and not sourced here. Cross-region estimates are not France checkout quotes; no ordering is authorized.

For the updated single-buffer candidate, the same dated observation gives **€0.817 excluding VAT / €0.9804 at assumed 20% VAT for the IC alone**, omitting the €1.33 excluding VAT transistor. Socket, capacitor, eight resistors, delivery and the complete interface price remain unquoted. These are indexed regional observations, not current France checkout quotes.

The owner approved the explicitly named small Pi-side communication-bias load in reported DUT consumption on 2026-10-16. AGENTS.md, requirements and architecture now record that scope. The owner subsequently selected the single SN74LV125AN circuit with "ok" and instructed continuation. One IC is now in the selected BOM; the two input pull-downs use a subset of the approved bias allowance. The transistor and Pi-side positive pull-up are omitted. GPIO assignment, passive/socket exact codes and baud rate remain open. See [UART qualification](uart-interface-qualification.md) for the subsequent startup, electrical-contract and support-part review. This selection is not a hardware qualification or a schematic-stage approval; do not ask the owner to choose this circuit again.
