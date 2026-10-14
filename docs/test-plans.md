# Test-plan workflow

Planned software interface, not executable firmware yet.

A campaign declares the workload, actual hardware/software configuration, setup and cleanup commands, warm-up, baseline, task timeout, cooldown, repetitions and application metrics. The initial target is generic Linux commands, one attached Pi at a time and manual board/HAT swapping.

Default idle baseline: 10 seconds. Default repetitions: five. Default maximum measured task duration: 300 seconds. Software configuration variants execute automatically; OS image provisioning and power-cycle recovery are outside the first software milestone.

The sequence is identify -> setup -> warm-up -> baseline -> task -> cooldown -> cleanup. Preserve exit codes, logs, timeouts, measurements and cleanup results. Never treat a command timeout, power fault, lost sample batch or buffer overflow as a successful complete run.

Power profiles include absolute energy, baseline statistics, signed excess energy, duration, average/peak power and configuration identity. The initial predictive model estimates 100 ms average power from runtime metrics/configuration, with whole-run validation groups and comparisons against a mean-power baseline.
