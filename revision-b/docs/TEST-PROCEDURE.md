# Revision B test procedure

## Confirm the model selector before fitting a chip

With USB disconnected and U3 empty, measure resistance between U3 pins 21 and 58. In the V9938 position expect about 470 Ω. In the V9958 position expect switch continuity (near zero ohms). A direct connection in the V9938 position can damage the video output. With the socket still empty, power up and measure U10 pin 2 against pin 4. Expect about 4.11 V for V9938 or 1.59 V for V9958 at a 5 V rail. Disconnect USB again before moving SW2 or fitting the DUT.

Use known-good samples of **both models** to qualify the fixture. Select the marked model before each insertion. Confirm that USB and the monitor report V9938 (ID 0) or V9958 (ID 2) as expected and that all stages pass. Check the red LED, serial stage and repeatability with a known-faulty sample. Recheck a known-good chip on the same fixture before attributing a failure to the DUT.

If V9938 composite video is required, probe U3 pin 21 with a high-impedance scope and compare with a known-good chip under the same display settings. The automatic verdict covers the shared RGB path.

## Before applying power

1. Leave A1, U1, U3, U4 and U5-U8 out. Inspect for shorts, reversed polarized
   parts and offset sockets. RN1 must be a bussed 10 kOhm network with common
   pin 1 at the marked end.
2. Check resistance between +5 V and GND. Investigate a near short.
3. Power from a current-limited USB source. Confirm about 5 V at TP1 and 3.3 V
   on Pico pin 36, then power off and discharge the board.
4. Fit U1, U4 and U10, the four known-good 41464s, the Pico and a known-good VDP matching SW2.
   Match every socket notch and pin-1 mark.

## Functional run

1. Open the Pico USB CDC serial port and apply power. The test begins after
   approximately 1.5 seconds.
2. Green D1 indicates all stages passed. Red D2 indicates failure; serial output
   reports the stage and measured values.
3. Send `R` or `r` over USB serial to repeat the test. Power off before changing
   the V9958, VRAM or logic devices.
4. For monitor output, power off and attach the optional daughterboard using a
   keyed straight-through 2x3 IDC cable. Align the pin-1 stripe at both ends.

Expected signals include CPUCLK near 3.58 MHz at TP3 and CSYNC near 15.6 kHz at
TP4. TP5-TP7 expose raw loaded red, green and blue. These RGB points include a
large DC offset and are not direct 75-ohm monitor outputs.
