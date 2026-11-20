# Design notes

## Architecture

The Pico data bus reaches the V9958 through U1, an SN74LVC245A powered at 3.3 V. Its inputs tolerate the VDP's 5 V data outputs, while its 3.3 V outputs satisfy the V9958 TTL input threshold. U2 is a 5 V SN74AHCT244 translating Pico control outputs to 5 V logic. U4 is a 3.3 V SN74LVC244A translating CPUCLK, HSYNC, CSYNC, WAIT and INT back to the Pico.

Four 41464 DRAMs provide two 64 KiB x 8 banks. Their connection follows the Omega V9958 memory topology: shared A0–A7/RAS/WE, CAS0 for U5/U6, CAS1 for U7/U8, and low/high data nibbles split between each pair.

The crystal network follows the Omega PAL circuit: 21.477270 MHz crystal, 470 kΩ parallel resistor, 30 pF trimmer, 22 pF capacitor, and a 5.6 µH filtered VDP supply. The oscillator parts are placed immediately beside U3 pins 63/64.

RGB outputs each see a 470 Ω load. A 22 kΩ/22 kΩ divider and 10 nF filter feed a Pico ADC channel. This is deliberately a response/relative-level check, not a calibrated video measurement.

The same raw RGB channels are AC-coupled into U9, a through-hole CXA1645P. U9 supplies the low-impedance cable drivers used by the Omega rather than loading a monitor directly from the V9958 DAC pins. Each output has the datasheet-recommended 75 Ω series resistor located near U9 and a 220 µF coupling capacitor. J1 uses the Omega DIN-8 assignments; pin 4 receives active-low CSYNC through 1 kΩ, which produces about 0.35 V into the display's 75 Ω termination. The tester does not generate composite colour or audio.

The CXA1645 is strapped for PAL and its unused composite/Y/C outputs are left unconnected. SCIN is intentionally unused: the subcarrier is needed only for composite/chroma encoding, while the RGB clamp and output path is timed from the TTL composite-sync input. The firmware selects PAL timing and leaves a 40-column result screen visible after the electrical tests.

All footprint references are printed on the front silkscreen. D1/D2 use the KiCad LED convention of pad 1 cathode and pad 2 anode; the explicit `+` is beside the anode. Polarized capacitors C6, C21, C23, C25, and C26–C28 use pad 1 positive and each has an explicit `+` assembly mark.


## Model selector and sync

SW2 is a two-pole slide switch. Disconnect USB before moving it. On all three tester layouts the actuator moves toward the corresponding V9938 or V9958 legend.

| DUT connection | V9938 position | V9958 position |
|---|---|---|
| U3 pin 21 | Composite VIDEO, pulled up to VCCVDP through R43 (470 Ω) | DAC supply, SW2 bypasses R43 |
| U3 pins 5 and 6 | U10 compares tri-level HSYNC/CSYNC against 4.11 V nominal | U10 compares logic-level HSYNC/CSYNC against 1.59 V nominal |
| U3 pin 26 | R47 holds the unused light-pen switch input high | Buffered WAIT output to GP18, enabled after identification |
| U3 pins 4, 8 and 27 | VDS sees a 10 kΩ pull-up, pin 8 supplies CPUCLK, LPD is pulled high | VRESET and HRESET are pulled high, pin 8 defaults to CPUCLK |

R44/R45/R46 (2.2 kΩ, 6.2 kΩ, 3.9 kΩ, all 1%) derive both thresholds from VCCVDP. The V9938 specifies 2.7–3.7 V for the middle sync level and at least 4.5 V for high at nominal supply. U10 is a rail-to-rail dual MAX942 with push-pull outputs. Its outputs feed the Pico monitor buffer and its CSYNC output also drives the cable circuit. The DIN carries attenuated CSYNC on contact 4 in both modes. The V9938 composite encoder and light-pen inputs are outside the automated test coverage. [Yamaha V9938 data book](https://www.bitsavers.org/pdf/yamaha/Yamaha_V9938_MSX-Video_Technical_Data_Book_Aug85.pdf) · [Yamaha V9958 data book, section 6](https://map.grauw.nl/resources/video/yamaha_v9958.pdf) · [MAX942 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max941-max944.pdf) · [Omega pin-21 selection](https://github.com/skiselev/omega/blob/master/Mainboard.md#jp3-jp4---v9938v9958)

The DIN footprint origin is the connector face. J1 on the full board and J2 on the daughterboard sit at y = 0 with the contact tails at positive y. The cable approaches from outside the top edge. The two shield tabs are grounded with DIN contact 1. Use the post-March-2022 SDF-80J mounting pattern. [Connector drawing, page 7](https://www.sameskydevices.com/product/resource/sdf-j.pdf)

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
