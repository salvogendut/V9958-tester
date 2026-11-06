# Revision B2 SRAM test procedure

## Before applying power

1. Leave A1 and all socketed ICs out. Inspect the board for shorts, offset
   sockets and reversed polarized parts. Confirm U5 is specifically an
   AS6C1008-55PCN or an electrically verified 55 ns-or-faster JEDEC-compatible
   128Kx8 5 V SRAM.
2. Confirm RN1 is a bussed 10 kOhm network with common pin 1 at the marked end.
3. Check resistance between +5 V and GND. Investigate a near short.
4. Power from a current-limited USB source. Confirm about 5 V at TP1 and 3.3 V
   on Pico pin 36, then power off and discharge the board.
5. Fit U1, U4-U7, the Pico and a known-good V9958. Match every notch and pin-1
   mark. Never insert or remove a chip while powered.

## First SRAM-interface qualification

1. Use a 10x probe with the ground spring, not a long clip lead. Probe at the
   IC/test point named below while running the VRAM test.
2. TP8 must show active-low `/RAS`. U6 outputs must retain the row address after
   the falling edge.
3. TP9 and TP10 must show alternating active-low bank selects. TP11 must go low
   whenever either TP9 or TP10 goes low.
4. TP12 is high for reads and low for writes. Check that SRAM data outputs are
   not driving while TP11 is high or TP12 is low.
5. Verify SRAM data at U5 is stable before the end of each V9958 read cycle.
   Repeat at the lowest and highest intended 5 V supply and after warm-up.

## Functional run

1. Open the Pico USB CDC serial port and apply power. The test begins after
   approximately 1.5 seconds.
2. Green D1 indicates all stages passed. Red D2 indicates failure; serial output
   reports the stage and first VRAM mismatch.
3. Send `R` or `r` over USB serial to repeat. Run repeated full-memory passes;
   an intermittent VRAM failure is a B2 timing failure until proven otherwise.
4. Expected monitor signals include CPUCLK near 3.58 MHz at TP3 and CSYNC near
   15.6 kHz at TP4. TP5-TP7 expose loaded raw RGB, not direct monitor outputs.
5. For an on-screen result, power off and attach the existing RGB DIN
   daughterboard with a keyed straight-through 2x3 IDC cable.

Do not use an unqualified B2 board to reject an expensive V9958. Confirm any
failure on the proven DRAM-based Revision B or a working Omega computer.
