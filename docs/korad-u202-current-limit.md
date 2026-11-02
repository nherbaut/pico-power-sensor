# Korad U202 current limit and proposed fuse omission

Date: 2026-10-17. Scope: source review responding to the owner's question about relying exclusively on the Korad U202. No hardware test or circuit change has been performed by this review.

## Verified documentation

The [Korad U200-series English manual](https://priniotakiselectronics.gr/image/KORAD/U202Englishusermanual.pdf), manufacturer's document hosted by a distributor, lists U202 current adjustment from **0 to 5 A**, with **1 mA setting resolution**. Its specification table gives current-setting accuracy of **≤0.5% + 5 mA**, under the stated three-minute warm-up and 25 ±5 °C conditions. At a 5 A setting, interpreting the percentage against the set value gives a calculated ±30 mA setting-accuracy allowance. This is not a guaranteed peak short-circuit current or OCP trip bound.

The same manual shows CV/CC indicators, an adjustable current control, a separate OCP button and an OCP status indicator. It instructs the user to enable OCP with that button. The [manufacturer's current U200 product page](https://www.koradtechnology.com/ProductDetail/2.html) also advertises overcurrent protection.

The manual does **not** quantify OCP trip timing, overshoot, stored-output-capacitor discharge, trip hysteresis or automatic restart/latching. It also does not define a separate numeric OCP threshold in the reviewed instructions. Do not import another Korad model's behavior or a third-party generated manual's shutdown description as a verified U202 specification. The adjustable current setting and existence of OCP are established; detailed fault response remains unmeasured.

## Engineering conclusion

For this supervised prototype, supplied only by the U202's main DC output with an appropriate current setting, **omitting the interposer's 6.3 A fuse and holder is a reasonable design option**. The U202 supports the required adjustable current setting. A 6.3 A fuse does not provide a guaranteed disconnect for a sustained 5 A current-limited fault, so it is not the primary protection for that scenario. Omission intentionally gives up its independent backup protection against other sources or abnormal source behavior.

The scoped operating arrangement would require the Korad as the sole positive DUT source, an appropriate current limit no greater than the qualified power-path current, and OCP enabled. No simultaneous Pi USB-C supply or separately powered HAT/USB backfeed is permitted. The carrier's independent USB power remains part of the existing mixed-power interface qualification, not an alternative intended Pi supply.

Before hardware use, the release review still needs the actual unit's current-limit/OCP behavior, startup and short-transient response, and tolerance of the complete power path to the resulting fault. Current limiting alone is not a promise that a 5 A fault is harmless to every component or branch. Do not declare the prototype safe, released or physically tested from the manual alone.

The expected electrical benefit is removal of the fuse's existing calculated nominal cold loss of approximately **47.5 mV at 5 A**, plus the unverified holder loss. Those are design calculations, not measured savings. Do not replace the fuse's removed resistance allowance with an unreviewed MOSFET or increase the supply voltage silently.

The current AGENTS.md and generated CAD still require/include the fuse. This source review establishes that fuse omission can be proposed for the specified bench-only arrangement; implementing it requires keeping the instruction, generator, schematic, board, BOMs, assembly guide and release evidence consistent. No fabrication or energizing is authorized by this review.
