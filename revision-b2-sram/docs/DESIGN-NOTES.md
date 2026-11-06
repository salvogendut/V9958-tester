# Revision B2 SRAM design notes

## Purpose

Revision B2 asks whether the V9958 tester can retain real external video RAM
while using fewer and more available parts than four 41464 DRAMs. It is not a
Pico RAM emulator. A Pico cannot directly cover the V9958's eight multiplexed
address lines, eight data lines and four control lines with sufficient timing
margin while also running the tester firmware.

## Address and control translation

- U6, SN74AHCT573N: D0-D7 receive V9958 AD0-AD7. Its latch enable receives
  `/RAS`; the latch is transparent while `/RAS` is high and captures the row
  on the falling edge. Q0-Q7 drive SRAM A8-A15.
- U5, AS6C1008-55PCN: A0-A7 receive the live V9958 AD0-AD7 column address.
  A8-A15 receive the latched row. A16 receives `/CAS0`, selecting the lower
  64 KiB when `/CAS0` is low and the upper 64 KiB when `/CAS1` is low.
- U7, SN74AHCT08N: `SRAM_OE_N = CAS0_N AND CAS1_N`. Either active-low CAS
  therefore enables the SRAM outputs. Unused gate inputs are tied to GND.
- SRAM `/CE` is tied to GND and its active-high `CE2` is tied to VCCVDP. This
  is deliberate: putting U7 in `/CE` would add
  gate propagation time to the SRAM chip-enable access time. With `/CE` low,
  the direct 55 ns address path is the limiting published read path; the
  gated output-enable path is shorter.
- V9958 `R/W` drives SRAM `/WE`. R21-R24 are 47-ohm source damping resistors.

## Timing status

The selected AS6C1008-55 grade specifies 55 ns maximum address access and
30 ns maximum output-enable access. The V9958 memory timing leaves only a
small read-data setup margin, so the `-55` speed grade is mandatory for this
prototype and long flying leads are not acceptable. The logic choice is AHCT,
not LS: AHCT accepts the V9958's TTL-level highs with low input loading and
has much less propagation delay.

The arithmetic above is a datasheet-level feasibility check, not hardware
qualification. Probe TP8 `/RAS`, TP9 `/CAS0`, TP10 `/CAS1`, TP11 SRAM `/OE`
and TP12 SRAM `/WE` at the SRAM pins. Confirm data validity and bus turn-around
with a known-good V9958 before using B2 to judge unknown devices.

## Remaining tester architecture

The CPU data-bus translator, Pico control resistors, buffered VDP monitor
signals, crystal network, filtered 5 V rail, RGB loads/ADC dividers, pass/fail
LEDs and optional video daughterboard header are unchanged from Revision B.
All populated carrier-board parts and sockets are through-hole.

## Primary component sources

- Alliance Memory, AS6C1008 128Kx8 low-power CMOS SRAM datasheet:
  <https://www.alliancememory.com/wp-content/uploads/pdf/AS6C1008_Mar_2023V1.2.pdf>
- Texas Instruments, SN74AHCT573 octal transparent latch:
  <https://www.ti.com/product/SN74AHCT573>
- Texas Instruments, SN74AHCT08 quad two-input AND gate:
  <https://www.ti.com/product/SN74AHCT08>
