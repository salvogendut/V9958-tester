# Revision B validation record

Date: 2026-11-06

- KiCad version: 10.0.8.
- Schematic ERC: 0 violations.
- PCB DRC: 0 violations.
- Unconnected PCB items: 0.
- Schematic/PCB parity issues: 0.
- Board: 170 x 118 mm, 77 footprints, 355 pads and 0 SMD pads.
- Route: 1,709 tracks/vias, including 75 vias, and two filled GND zones.
- All populated carrier-board parts are through-hole or through-hole modules.
- 3D/top renders and the assembly SVG were visually inspected.
- Revision B and revision 0.3 firmware variants passed host C11 syntax checks
  with warnings treated as errors; no ARM/UF2 build was available here.
- Gerber archive SHA-256: `25b8768c1a7d2a0bb50880ec7a6e165449d2701acaad91a271968e23a9ee9cec`.

The board is still **PROTOTYPE / UNVALIDATED**. Physical assembly must confirm
socket fit, oscillator start-up, USB current margin, bus timing, RGB thresholds,
IDC orientation and known-good/known-bad V9958 discrimination.
