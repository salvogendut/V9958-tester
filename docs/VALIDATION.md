# Validation record — revision 0.2

Date: 2026-11-06

- KiCad version: 10.0.8.
- Schematic ERC: 0 violations (`erc.json`).
- PCB DRC: 0 violations (`drc.json`).
- PCB unconnected items: 0.
- Schematic/PCB parity issues: 0.
- Final board: 101 footprints, 449 pads, and 0 SMD pads (pcbnew audit).
- Router completion: 303 initial unrouted connections to 0; final acceptance is based on KiCad DRC, not the router score.
- Final route: 1,957 tracks/vias and two filled GND zones.
- Gerber archive SHA-256: `c74ef7d55a457f2fe9da9fa46cd0f6ac6915b1206ec3ec3a485737730483eae3`.
- Firmware C11 source passed a host warnings-as-errors syntax check; Pico API names were checked against official Pico SDK 2.3.1.
- ARM/UF2 build: not performed because the embedded ARM toolchain was unavailable.
- Physical assembly and known-good/known-bad V9958 qualification: not yet performed.

The design must remain labelled **PROTOTYPE / UNVALIDATED** until physical testing confirms oscillator start-up, bus timing, VRAM behavior, RGB thresholds, CXA1645/DIN video levels, cable compatibility, socket fit, and thermal/current margins.

