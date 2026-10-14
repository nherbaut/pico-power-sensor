# PicoPower working instructions

- Preserve the distinction between instrument, DUT and measurement boundary.
- The user owns a Korad U202 and will begin with a Raspberry Pi 5. Do not purchase another DUT supply or substitute a voltage-converter HAT.
- The current implementation milestone is the custom interposer and project documentation. Firmware, daemon and server are planned separately.
- English documentation and code identifiers; reuse the NoiseNet documentation site layout and CSV tracking workflow.
- Power protection and its supply currents belong upstream of the shunt. No instrument supply, indicator LEDs, pull-ups to external supplies, or other auxiliary loads may be silently included in DUT current.
- Keep all 40 header pins available and verify physical compatibility with the Active Cooler and both AI HAT versions.
- Never describe design calculations or automated checks as physical measurements. Track ERC, DRC, footprint review and bench validation separately.
- Fabrication and connection to a Pi require the release checklist to be completed. Never suppress violations to make a release pass.
- No remote repository creation, publishing, ordering or hardware activation is authorized by the local scaffold task.
