# Understanding the two boards

The **interposer** sits between the lab power supply and the Raspberry Pi under test. The **carrier** holds the Pico and connects it to the measurement module. They have different jobs and separate power supplies.

| Item | Job | What it means for you |
|---|---|---|
| Korad U202 | Supplies the Pi through the interposer | Keep this supply; no voltage-converter HAT is needed |
| Interposer | Routes power, provides protection and carries the shunt | This is the board whose power path must be tested before connecting a Pi |
| Shunt | A small, accurately specified resistor used to infer current from its voltage drop | Its four connections separate current flow from voltage sensing |
| INA229EVM | Reads the shunt voltage and supply voltage | It connects to the carrier for power/data and to the interposer for sensing |
| Pico carrier | Supports the Pico, five programmable LEDs, microSD and connectors | Its USB supply powers the instrument independently |
| Raspberry Pi and HAT | Run the task being measured | Their power is the measurement target, or DUT: device under test |

The interposer's power LED and protection electronics sit before the shunt, so their consumption is excluded from the DUT reading. The Pi-side communication buffer is an explicitly documented small additional load on the measured side. The instrument is not powered from the measured 5 V rail.

## Why a board can pass KiCad and still need work

**ERC** checks schematic wiring rules. **DRC** checks PCB geometry and connections. These checks can detect many mistakes, but they do not know whether a connector physically mates, whether a component overheats, or whether a Pi fits underneath a HAT.

An **MPN** is the exact manufacturer's part number. A **footprint** is the pattern of copper pads where a component is soldered. "0805" describes a package size; we still need the manufacturer's pad dimensions. A **BOM** is the parts list. A **Gerber package** is the set of manufacturing drawings sent to a PCB factory. Our current ZIP files are review packages, not permission to manufacture.

## What the latest work changes

Selected passive components now have exact references in the CAD and parts lists. The capacitor that controls power startup has manufacturer-based solder pads. Regeneration tests check that those references and corrected pads survive rebuilding the files.

The [assembly list](../hardware/assembly-review.csv) separates factory-soldered components from connectors you will fit manually. In particular, the Pico plugs into two socket strips; it is not listed as a module for the factory to solder directly to the board. The fuse holder and its removable fuse are separate items.

## The main unresolved issue: voltage lost on the way to the Pi

Every fuse, connector and copper track loses some voltage while carrying current. Our target is at most **0.10 V lost at 5 A** between the board input and the Pi header, including the return path. The external Korad cables add their own loss.

The component reference subtotal is already about **0.097 V**. The complete six-branch copper calculation adds about **0.036 V**, including the return path. Together these give roughly **0.133 V**, before several other contributions. This supersedes the earlier 0.118 V subtotal, which counted only one copper branch. These are calculations, not measurements, and they do not establish the complete worst case. They do show why the present design cannot yet demonstrate the 0.10 V target.

The [electronic protection study](electronic-protection.md) investigates a detector that commands the existing power switches. It could remove the fuse/holder loss while retaining the measurement shunt, but cutoff, reset and power-loss behavior must be designed first. Raising the supply voltage is not a substitute for resolving that design requirement.

## What happens next

The remaining desk work is to resolve that power budget, finish component footprint reviews, check startup stress on the power switches, and verify the microSD power behavior. These are engineering tasks; you do not need to choose resistor values or interpret transistor graphs yourself.

Your practical contribution is the unpowered mechanical fit with real connectors and supports, followed later by supervised tests at the fablab using a load in place of the Pi. More paper-only photographs are not needed. The [fablab worksheet](fablab-validation.md) explains the sequence and the [release checklist](../hardware/release-checklist.csv) tracks the evidence.

**Neither board is released for fabrication or connection to a Pi.** Equipment access is confirmed; physical fit and electrical test results still have to be recorded.
