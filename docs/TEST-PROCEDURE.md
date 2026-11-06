# Test procedure

## Before applying power

1. Confirm no chips or sockets are offset by one pin and all notches match the silkscreen.
2. Confirm RN1 is a **bussed/common** 10 kΩ network and its common pin 1 is in the marked end.
3. Check resistance from 5 V to GND. Investigate a near short before continuing.
4. Leave U3 and U5–U8 out. Power from a current-limited 5 V USB source and verify TP1 is about 5 V and TP2 about 3.3 V.
5. Power off and discharge the board before inserting parts.

## First functional run

1. Fit four known-good 41464 DRAMs in U5–U8.
2. Fit a known-good V9958 in U3, observing pin 1.
3. Connect the Pico USB port to a serial-capable host and open its CDC serial device.
4. Apply power. Do not touch or move socketed parts while powered.
5. The test starts automatically after about 1.5 seconds. It takes several seconds because it writes and reads all 128 KiB twice.
6. Green means all stages passed. Red means failure; read the serial stage and measurements.
7. Press SW1 to repeat without cycling power. Power off before changing the DUT.

## Stage codes

| Code | Meaning | First probes |
|---:|---|---|
| 1 | Master clock | TP4 should be about 3.58 MHz; inspect Y1, R4, C1, C2 and U3 pins 63/64. |
| 2 | V9958 identification | CPU bus works but status ID is not V9958; a V9938 or incompatible/counterfeit part is possible. |
| 3 | CPU bus or WAIT | Check U1, U2, GP0–GP14 paths, `/CSR`, `/CSW`, MODE0/1, and WAIT. |
| 4 | VRAM | Serial gives the first address; inspect U5–U8, their sockets, address/data nets, CAS0/1, RAS and WE. |
| 5 | Sync | TP5 and TP6 should be around 15.6 kHz. A value around 127 kHz is a fail. |
| 6 | Interrupt | Check U3 pin 25, R3, U4 and Pico GP20. |
| 7 | RGB response | Probe TP7–TP9 and check the 470 Ω loads, 22 kΩ dividers, 10 nF filters, and Pico ADC pins. |

## Oscillator adjustment

C1 is included because the reference Omega circuit uses a trimmer. Start near mid-range. On a known-good V9958, adjust only if CPUCLK is outside tolerance or the crystal fails to start. Use a x10 probe with a short ground spring; probing pins 63/64 directly can load the oscillator, so TP4 (buffered CPUCLK) is preferred for frequency checks.

