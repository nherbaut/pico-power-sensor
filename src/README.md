# Firmware and services

Implementation is deferred until the interposer design is reviewed. Intended components are C/C++ Pico SDK firmware, a Linux/systemd Pi daemon, an ingestion service and server-side analysis. See the [architecture](../docs/architecture.md) and [experiment workflow](../docs/test-plans.md).

The firmware must own acquisition timestamps independently of Wi-Fi, isolate hardware-specific drivers and expose missed-sample and power-fault status. A simulator will exercise the pipeline before claims of hardware accuracy.
