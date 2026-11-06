# Validation record — revision 0.3

Date: 2026-11-06

- KiCad version: 10.0.8.
- Schematic ERC: 0 violations (`erc.json`).
- PCB DRC: 0 violations (`drc.json`).
- PCB unconnected items: 0.
- Schematic/PCB parity issues: 0.
- Final board: 101 footprints, 449 pads, and 0 SMD pads (pcbnew audit).
- Router completion: 303 initial unrouted connections to 0; final acceptance is based on KiCad DRC, not the router score.
- Final route: 1,983 tracks/vias and two filled GND zones.
- Silkscreen audit: all 101 footprint references visible; 9 explicit positive-polarity marks; copyright text present.
- Gerber archive SHA-256: `18d56275c3df7d92f1f5a603639e22bbdc78652342dfeb3d890481a9f166c59a`.
- Firmware C11 source passed a host warnings-as-errors syntax check; Pico API names were checked against official Pico SDK 2.3.1.
- ARM/UF2 build: not performed because the embedded ARM toolchain was unavailable.
- Physical assembly and known-good/known-bad V9958 qualification: not yet performed.

The design must remain labelled **PROTOTYPE / UNVALIDATED** until physical testing confirms oscillator start-up, bus timing, VRAM behavior, RGB thresholds, CXA1645/DIN video levels, cable compatibility, socket fit, and thermal/current margins.

