# Revision B2 SRAM test procedure

## Confirm the model selector before fitting a chip

With USB disconnected and U3 empty, measure resistance between U3 pins 21 and 58. In the V9938 position expect about 470 Ω. In the V9958 position expect switch continuity (near zero ohms). A direct connection in the V9938 position can damage the video output. With the socket still empty, power up and measure U10 pin 2 against pin 4. Expect about 4.11 V for V9938 or 1.59 V for V9958 at a 5 V rail. Disconnect USB again before moving SW2 or fitting the DUT.

Use known-good samples of **both models** to qualify the fixture. Select the marked model before each insertion. Confirm that USB and the monitor report V9938 (ID 0) or V9958 (ID 2) as expected and that all stages pass. Check the red LED, serial stage and repeatability with a known-faulty sample. Recheck a known-good chip on the same fixture before attributing a failure to the DUT.

If V9938 composite video is required, probe U3 pin 21 with a high-impedance scope and compare with a known-good chip under the same display settings. The automatic verdict covers the shared RGB path.

## Before applying power

1. Leave A1 and all socketed ICs out. Inspect the board for shorts, offset
   sockets and reversed polarized parts. Confirm U5 is specifically an
   AS6C1008-55PCN or an electrically verified 55 ns-or-faster JEDEC-compatible
   128Kx8 5 V SRAM.
2. Confirm RN1 is a bussed 10 kOhm network with common pin 1 at the marked end.
3. Check resistance between +5 V and GND. Investigate a near short.
4. Power from a current-limited USB source. Confirm about 5 V at TP1 and 3.3 V
   on Pico pin 36, then power off and discharge the board.
5. Fit U1, U4–U7 and U10, the Pico and a known-good VDP matching SW2. Match every notch and pin-1
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

Confirm any failing V9938 or V9958 on a qualified DRAM-based fixture or a working Omega configured for that chip.
