# Revision B design notes

## Architecture

A1 is the CPU and test controller. U1, an SN74LVC245AN powered from 3.3 V,
translates the bidirectional CD0-CD7 bus. The Pico drives MODE0, MODE1, `/CSW`,
`/CSR` and `/RESET` through R3-R7. R8-R14 establish harmless power-up states.

U4 is an SN74LVC244AN powered from 3.3 V. Its 5 V-tolerant inputs buffer
CPUCLK, HSYNC, CSYNC, WAIT and the open-drain interrupt before those signals
reach the Pico. Passive dividers were deliberately rejected: the V9958 only
guarantees some output-high levels at 2.4-2.7 V under light load, leaving poor
Pico threshold margin after division.

U5-U8 are four 64Kx4 DRAMs arranged as two 64 KiB x 8 banks. The Pico cannot
reliably emulate the V9958 multiplexed DRAM cycles and refresh timing, so real
VRAM remains part of the minimum fixture.

Each RGB output has its specified 470-ohm load and a divided, filtered Pico ADC
input. J1 exports the raw loaded RGB, TTL CSYNC, +5 V and GND to the optional
daughterboard. J1 is not a monitor connector and must not be wired directly to
a 75-ohm display input.

The 21.477270 MHz crystal, trimmer and 22 pF capacitor follow the Omega PAL
clock circuit. F1 protects USB VBUS and L1 filters the V9958/VRAM supply.
Every active device has a local 100 nF bypass capacitor.

## PCB

- 170 x 118 mm, two copper layers, nominally 1.6 mm thick.
- 0.25 mm minimum signal tracks; 0.60 mm power tracks.
- 0.20 mm copper clearance and 0.40 mm copper-to-edge clearance.
- Ground pours on both sides.
- 77 footprints, 355 pads and zero SMD pads.
- Pico USB connector faces the right board edge with an unobstructed cable path.
- All component references, LED anodes and the electrolytic positive lead are
  identified on the front silkscreen.
