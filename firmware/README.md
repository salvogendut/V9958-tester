# Firmware

`main.c` targets an original RP2040 Raspberry Pi Pico. It runs the complete test at startup and whenever SW1 is pressed. Results are shown on D1/D2, printed over USB CDC serial, and rendered as a 40-column PAL text screen through the Omega-compatible DIN RGB output.

The same source also builds Revision B when `V9958_REV_B=1`; that variant
repeats the test when `R` is received over USB serial because Revision B omits
the external TEST button.

The source passed a host C11 syntax check with `-Wall -Wextra -Werror`; the hardware API calls were checked against official Pico SDK 2.3.1. This environment did not contain the ARM embedded compiler, so no UF2 is checked in.

Build with a normal Pico SDK toolchain as shown in the project README. Do not power the tester from both the Pico USB connector and another 5 V source.

