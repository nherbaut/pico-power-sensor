# Calibration and measurement uncertainty

The assembled instrument measures current through a 5 mOhm shunt and voltage at a declared point near the Pi header. Energy in joules is the time integral of load voltage times load current. Watt-hours are joules divided by 3600.

## Calibration procedure

- Record shunt part/lot, instrument revision, EVM revision, ADC settings, reference meter identity and temperature.
- Measure zero-current offset and voltage offset with a controlled supply and dummy load.
- Compare at several loads, including 0.1, 0.5, 1, 3 and 5 A where equipment supports them. Use four-wire resistance measurements or fitted gain calibration; an ordinary two-lead ohmmeter cannot characterize 5 mOhm accurately.
- Fit gain/offset only from reference data, retain residuals and store coefficients per instrument. Re-test after thermal stabilization.
- Check static accuracy and energy integration separately from transient response. The target is 2% calibrated power error over a stated range, not an existing specification.
- Check 10 kHz throughput while UART and Wi-Fi are active. Preserve real timestamps and declare missed conversions; do not infer a perfect sample period from a nominal register setting.
- Use a switched load and reference oscilloscope/current measurement to estimate bandwidth, conversion skew and marker timing uncertainty.

## Boundary checks

Fuse, protection and shunt dissipation are upstream of the measured voltage bus. They do not enter computed load power, but their voltage drop can still change the Pi's behavior. Report supply and load voltage, not only watts.

The stacking header adds contact resistance after the board voltage-sense point. Characterize this drop and the ground return at 5 A. If its contribution matters to the accuracy target, add a separate high-impedance sense pair directly on the Pi rail; do not silently correct with an assumed constant resistance.

Do not add large capacitors downstream of the shunt on the interposer. A capacitor can supply short task bursts and shift current outside the event window. The Pi's existing capacitance remains part of the DUT; run windows and cooldown must account for recharge. Integrate signed current when reverse flow occurs and flag sensor saturation.

The daemon's own overhead is included in the DUT baseline. Absolute energy is always retained alongside signed baseline-relative energy. The baseline must match services, fan settings, HAT configuration and thermal conditions.

## Buffered interface overhead

U2 VCCB, C4, R10/R11 and R14 use Pi 3.3 V, so their supply, switching and charging energy is included in DUT measurements. U2 VCCA, C3, R12/R13 and R15 use the external Pico supply. Characterize idle, UART activity and marker switching separately. Retain the raw trace and total energy; no constant correction is assumed. Compare matching traffic and interface configuration in baseline and task runs.

With 100 kOhm biases and nominal 3.3 V, each actively opposed bias draws about 33 uA. The three Pi-side biases can together draw about 99 uA in an opposing logic pattern, before buffer supply and switching current. These are calculations, not measured assembled consumption or a guaranteed total bound.
