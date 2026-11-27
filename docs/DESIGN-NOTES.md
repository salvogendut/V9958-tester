# Design notes

## Architecture

The Pico data bus reaches the V9958 through U1, an SN74LVC245A powered at 3.3 V. Its inputs tolerate the VDP's 5 V data outputs, while its 3.3 V outputs satisfy the V9958 TTL input threshold. U2 is a 5 V SN74AHCT244 translating Pico control outputs to 5 V logic. U4 is a 3.3 V SN74LVC244A translating CPUCLK, HSYNC, CSYNC, WAIT and INT back to the Pico.

Four 41464 DRAMs provide two 64 KiB x 8 banks. Their connection follows the Omega V9958 memory topology: shared A0–A7/RAS/WE, CAS0 for U5/U6, CAS1 for U7/U8, and low/high data nibbles split between each pair.

The crystal network follows the Omega PAL circuit: 21.477270 MHz crystal, 470 kΩ parallel resistor, 30 pF trimmer, 22 pF capacitor, and a 5.6 µH filtered VDP supply. The oscillator parts are placed immediately beside U3 pins 63/64.

RGB outputs each see a 470 Ω load. A 22 kΩ/22 kΩ divider and 10 nF filter feed a Pico ADC channel. This is deliberately a response/relative-level check, not a calibrated video measurement.

The same raw RGB channels are AC-coupled into U9, a through-hole CXA1645P. U9 supplies the low-impedance cable drivers used by the Omega rather than loading a monitor directly from the V9958 DAC pins. Each output has the datasheet-recommended 75 Ω series resistor located near U9 and a 220 µF coupling capacitor. J1 uses the Omega DIN-8 assignments; pin 4 receives active-low CSYNC through 1 kΩ, which produces about 0.35 V into the display's 75 Ω termination. The tester does not generate composite colour or audio.

The CXA1645 is strapped for PAL and its unused composite/Y/C outputs are left unconnected. SCIN is intentionally unused: the subcarrier is needed only for composite/chroma encoding, while the RGB clamp and output path is timed from the TTL composite-sync input. The firmware selects PAL timing and leaves a 40-column result screen visible after the electrical tests.

All footprint references are printed on the front silkscreen. The radial capacitor footprints carry one `+` at pad 1 (positive). On the LED footprints the `+` follows pad 2 (anode). Both marks follow their footprint when it moves or rotates.

Board generation checks the markings against the schematic pin assignments. After packaging a release, run `python3 tools/polarity.py` with KiCad's Python environment and `kicad-cli` on PATH. It checks all four boards and compares a fresh front silkscreen export with the loose Gerber and the copy inside each fabrication ZIP.


## Model selector and sync

SW2 is a two-pole slide switch. Disconnect USB before moving it. On all three tester layouts the actuator moves toward the corresponding V9938 or V9958 legend.

| DUT connection | V9938 position | V9958 position |
|---|---|---|
| U3 pin 21 | Composite VIDEO, pulled up to VCCVDP through R43 (470 Ω) | DAC supply, SW2 bypasses R43 |
| U3 pins 5 and 6 | Raw sync trip point 4.12 V (U10 reference 2.06 V) | Raw sync trip point 1.69 V (U10 reference 0.84 V) |
| U3 pin 26 | R47 holds the unused light-pen switch input high | Buffered WAIT output to GP18, enabled after identification |
| U3 pins 4, 8 and 27 | VDS sees a 10 kΩ pull-up, pin 8 supplies CPUCLK, LPD is pulled high | VRESET and HRESET are pulled high, pin 8 defaults to CPUCLK |

Full-size 0.5, compact DRAM B1.1 and SRAM B2.2 use TI’s LM393P in PDIP-8. R48/R49 and R50/R51 divide each raw sync voltage by two. Each pair uses two 47 kΩ 1% resistors and loads its VDP pin by 94 kΩ. Even a signal reaching the supply rail stays inside the comparator’s input range. R44/R45/R46 (15 kΩ, 6.2 kΩ and 4.3 kΩ, all 1%) provide the two references from VCCVDP. SW2 selects the reference on U10 pins 3 and 5. [TI LM393P status](https://www.ti.com/product/LM393/part-details/LM393P) · [TI LM393 electrical and switching characteristics](https://www.ti.com/lit/ds/symlink/lm393.pdf)

At 5.00 V, allowing independent 1% resistor tolerances and ±25 mV at the comparator for offset and input bias, the calculated raw trip ranges are 3.98–4.26 V (V9938) and 1.59–1.78 V (V9958). Across a 4.75–5.25 V VCCVDP range, these extend to 3.78–4.47 V and 1.51–1.87 V. Yamaha specifies the V9938 middle level as 2.7–3.7 V and high as at least 4.5 V with no load. Measure both levels with the divider attached when qualifying the fixture. [Yamaha V9938 data book, electrical characteristics](https://map.grauw.nl/resources/video/yamaha_v9938.pdf) · [Yamaha V9958 data book, section 6](https://map.grauw.nl/resources/video/yamaha_v9958.pdf)

R52 and R53 pull the LM393P’s open-collector outputs up to VCCVDP through 2.2 kΩ. Two SN74HC14N Schmitt inverters restore sync polarity and drive U4, the Pico monitor buffer. The CSYNC gate also drives the video circuit. Its 1 kΩ series resistor and the display’s 75 Ω termination give a nominal 0.35 V sync swing at DIN contact 4. The buffer’s minimum falling threshold is 0.9 V at 4.5 V, above the LM393P’s 0.7 V maximum low at 4 mA. The comparator’s specified response times at 25 °C are typical only (0.3 µs for a TTL step and 1.3 µs at 5 mV overdrive). Check horizontal and vertical pulse widths on both VDPs during bring-up. [TI SN74HC14N status](https://www.ti.com/product/SN74HC14/part-details/SN74HC14N) · [TI SN74HC14 datasheet](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf)

Full-size 0.4, DRAM B1 and SRAM B2.1 use a MAX942CPA+ with different input wiring, reference voltages and output drive. Fit the comparator listed for the PCB marking. The V9938 composite encoder and light-pen inputs are outside the automated test coverage. [MAX942 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max941-max944.pdf) · [Omega pin-21 selection](https://github.com/skiselev/omega/blob/master/Mainboard.md#jp3-jp4---v9938v9958)

J1 on the full board and J2 on the daughterboard take a Same Sky SDS-80J. The mating face sits at y = 0 with the contact tails inside the board. Both E terminals connect to ground with contact 1. The SDS-80J and the shielded SDF-80J with a date code after 03/03/2022 share the same eight numbered contact positions, two ground terminals and two locating pegs. Both use ten 1.3 mm plated holes and two 2.4 mm non-plated holes. The footprint courtyard accommodates both bodies. [SDS-80J drawing, p. 5](https://www.sameskydevices.com/product/resource/sds-j.pdf) · [SDF-80J drawing, p. 7](https://www.sameskydevices.com/product/resource/sdf-j.pdf)

## PCB constraints

- Two copper layers, 1.6 mm nominal thickness.
- 0.25 mm minimum signal track; 0.60 mm power-net nominal track.
- 0.20 mm released clearance; routing was performed with a 0.30 mm margin.
- 0.70/0.35 mm default vias and 0.80/0.40 mm power vias.
- Ground pours on both layers.
- All populated carrier-board parts are through-hole or through-hole modules.
- Board outline: 232 mm x 141 mm.
- The Pico USB end sits at x=228 mm, leaving 4 mm of PCB to the right edge and an unobstructed plug/cable path.

The V9958 footprint uses 1.40 mm x 1.80 mm pads with 0.90 mm drills. Along the 1.778 mm pitch this leaves 0.378 mm copper gap and 0.25 mm annular copper at the narrow side.

## Validation status

The release checks and firmware build are recorded in [validation](VALIDATION.md). Qualification on physical samples of both chips is pending.
