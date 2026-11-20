# Firmware

`main.c` targets an original RP2040 Raspberry Pi Pico. It runs the complete test at startup and whenever SW1 is pressed. Results are shown on D1/D2, printed over USB CDC serial, and rendered as a 40-column PAL text screen through the Omega-compatible DIN RGB output.

The same source also builds Revision B when `V9958_REV_B=1`; that variant
repeats the test when `R` is received over USB serial because Revision B omits
the external TEST button.

S#1 bits 5–1 select the model. ID 0 uses fixed bus timing for V9938. ID 2 enables R#25.WTE and checks GP18 for V9958. Both paths select 64K DRAM geometry, run two full 128 KiB passes, check clock/sync and VBlank acknowledgement, and compare each RGB channel against its own low levels. USB and the result screen report the detected model.

The supplied [RP2040 UF2](v9958_tester.uf2) was built with Pico SDK 2.2.0 and Arm GNU 14.3.1. Set SW2 with USB disconnected before testing either chip.

Build with a normal Pico SDK toolchain as shown in the project README. Do not power the tester from both the Pico USB connector and another 5 V source.

