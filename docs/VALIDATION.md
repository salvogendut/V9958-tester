# Validation record — revision 0.1

Date: 2026-11-06

- KiCad version: 10.0.6.
- Schematic ERC: 0 violations (`erc.json`).
- PCB DRC: 0 violations (`drc.json`).
- PCB unconnected items: 0.
- Schematic/PCB parity issues: 0.
- Final board: 76 footprints and 0 SMD pads (pcbnew audit).
- Router completion: 251 initial unrouted connections to 0; final acceptance is based on KiCad DRC, not the router score.
- Gerber archive SHA-256: `7a8486fc084fe9858ea8323f533854a72635af125022cf68e02027f45767e991`.
- Firmware C11 source passed a host warnings-as-errors syntax check; Pico API names were checked against official Pico SDK 2.3.1.
- ARM/UF2 build: not performed because the embedded ARM toolchain was unavailable.
- Physical assembly and known-good/known-bad V9958 qualification: not yet performed.

The design must remain labelled **PROTOTYPE / UNVALIDATED** until physical testing confirms oscillator start-up, bus timing, VRAM behavior, RGB thresholds, socket fit, and thermal/current margins.

