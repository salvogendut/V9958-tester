# Revision B2 SRAM validation record

Date: 2026-11-06

This file records CAD checks performed on the generated design. Electrical
timing remains unvalidated until a physical prototype is measured.

- KiCad version: 10.0.8.
- Schematic ERC: 0 violations.
- PCB DRC: 0 violations.
- Unconnected PCB items: 0.
- Schematic/PCB parity issues: 0.
- Board: 160 x 110 mm, 80 footprints, 352 pads and 0 SMD pads.
- Route: 1,263 tracks/vias, including 77 vias, and two filled GND zones.
- All populated carrier-board parts are through-hole or through-hole modules.
- The schematic explicitly ties AS6C1008 pin 31 `CE2` to VCCVDP and pin 22
  active-low `/CE` to GND.
- 3D/top renders and the assembly SVG were visually inspected.
- The B2 firmware variant shares the already syntax-checked Revision B source.
- Gerber archive SHA-256:
  `6241d84ab1d5765b144ae080452002d44856cb0155e9f4e38ddbd97a70f7515b`.
- SRAM/V9958 timing: **not physically qualified**.

The board remains **EXPERIMENTAL / UNBUILT / UNVALIDATED**. Passing ERC, DRC
and the firmware memory test does not by itself establish worst-case timing.
