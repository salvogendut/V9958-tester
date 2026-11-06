# Design notes

## Architecture

The Pico data bus reaches the V9958 through U1, an SN74LVC245A powered at 3.3 V. Its inputs tolerate the VDP's 5 V data outputs, while its 3.3 V outputs satisfy the V9958 TTL input threshold. U2 is a 5 V SN74AHCT244 translating Pico control outputs to 5 V logic. U4 is a 3.3 V SN74LVC244A translating CPUCLK, HSYNC, CSYNC, WAIT and INT back to the Pico.

Four 41464 DRAMs provide two 64 KiB x 8 banks. Their connection follows the Omega V9958 memory topology: shared A0–A7/RAS/WE, CAS0 for U5/U6, CAS1 for U7/U8, and low/high data nibbles split between each pair.

The crystal network follows the Omega PAL circuit: 21.477270 MHz crystal, 470 kΩ parallel resistor, 30 pF trimmer, 22 pF capacitor, and a 5.6 µH filtered VDP supply. The oscillator parts are placed immediately beside U3 pins 63/64.

RGB outputs each see a 470 Ω load. A 22 kΩ/22 kΩ divider and 10 nF filter feed a Pico ADC channel. This is deliberately a response/relative-level check, not a calibrated video measurement.

The same raw RGB channels are AC-coupled into U9, a through-hole CXA1645P. U9 supplies the low-impedance cable drivers used by the Omega rather than loading a monitor directly from the V9958 DAC pins. Each output has the datasheet-recommended 75 Ω series resistor located near U9 and a 220 µF coupling capacitor. J1 uses the Omega DIN-8 assignments; pin 4 receives active-low CSYNC through 1 kΩ, which produces about 0.35 V into the display's 75 Ω termination. The tester does not generate composite colour or audio.

The CXA1645 is strapped for PAL and its unused composite/Y/C outputs are left unconnected. SCIN is intentionally unused: the subcarrier is needed only for composite/chroma encoding, while the RGB clamp and output path is timed from the TTL composite-sync input. The firmware selects PAL timing and leaves a 40-column result screen visible after the electrical tests.

## PCB constraints

- Two copper layers, 1.6 mm nominal thickness.
- 0.25 mm minimum signal track; 0.60 mm power-net nominal track.
- 0.20 mm released clearance; routing was performed with a 0.30 mm margin.
- 0.70/0.35 mm default vias and 0.80/0.40 mm power vias.
- Ground pours on both layers.
- All populated carrier-board parts are through-hole or through-hole modules.
- Board outline: 231 mm x 140 mm.
- The Pico USB end sits at x=228 mm, leaving 3 mm of PCB to the right edge and an unobstructed plug/cable path.

The V9958 footprint uses 1.40 mm x 1.80 mm pads with 0.90 mm drills. Along the 1.778 mm pitch this leaves 0.378 mm copper gap and 0.25 mm annular copper at the narrow side.

## Validation status

KiCad 10.0.6 reports zero ERC violations, zero PCB DRC violations, zero unconnected items, and zero schematic/PCB parity issues. Firmware C syntax was checked with warnings-as-errors and its Pico API names were checked against official Pico SDK 2.3.1. An ARM cross-compiler was not available in the design environment, so the UF2 has not been built here. No physical prototype has yet been assembled.

