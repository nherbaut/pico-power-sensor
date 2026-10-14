# Assembly and first power-up

## Before ordering

Complete the [release checks](../hardware/pcb/interposer/README.md), including full routing, reviewed footprints, KiCad ERC/DRC and the physical mock-up. Draft placement previews are not fabrication data. Do not populate an unreviewed protection circuit and assume it protects a Pi.

Use 1.6 mm FR4 and the reviewed copper stack-up, initially targeting two layers with 70 um copper. Verify fabrication clearances, plated-hole sizes and connector pad soldering. Measure the assembled shunt rather than relying only on its nominal value.

## Assembly sequence

1. Assemble small SMD parts, MOSFETs and shunt first. Inspect polarity, pin 1 and solder joints under magnification. The shunt's sense pads must not be shorted to current pads by external copper or solder.
2. Fit the keyed power connector, fuse holder, signal connectors and stacking socket. Confirm that the lower socket mates with the Pi and the upper tails engage the AI HAT correctly.
3. Mount the side wing to a nonconductive support. Add cable strain relief. The fuse and power plug must remain accessible with the HAT fitted.
4. With no Pi or instrument attached, check ground continuity, both 5 V contacts, each individual pass-through signal and power-to-ground resistance. Verify the series power path and absence of any shunt bypass.
5. Set the Korad output off, voltage 5.10 V and a low initial current limit. Verify polarity on the detached mating plug before insertion.
6. Test with a dummy load first. Sweep through the input protection thresholds, reversed input and startup behavior without a Pi. Test at nominal voltage up to 5 A with an appropriately rated electronic load.
7. Record supply voltage, header-bus voltage, current, contact/fuse/shunt/MOSFET temperatures and settling behavior. Do not raise supply voltage to hide excessive harness drop.
8. Connect instrument sensing only after the power path passes. Calibrate against reference measurements and check sensor range and conversion coherence.
9. Power off and fit the Pi/Active Cooler/HAT. Verify clearance, mating depth, support and PCIe cable routing. Start with the Pi alone before fitting the AI HAT, always while unpowered.
10. Run idle and sustained workload tests; reject undervoltage, supply current limiting or thermal faults. Save results in the instrument record.

Never hot-plug the power connector or swap a HAT while powered. A disconnected USB-C supply does not rule out back-powering from other attached USB devices; characterize the actual peripheral arrangement.
