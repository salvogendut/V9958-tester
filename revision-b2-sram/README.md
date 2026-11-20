# V9958 Tester Revision B2 SRAM

**Use PCB B2.1 for V9938 or V9958.** Disconnect USB, set SW2 to the package marking, then insert the DUT. Earlier boards without SW2 connect pin 21 directly to 5 V and can damage a V9938. See the [selector checks](docs/TEST-PROCEDURE.md).

Revision B2 is an experimental all-through-hole variant of the V9938/V9958 tester.
It replaces Revision B's four 41464 DRAMs with one AS6C1008-55PCN 128Kx8
asynchronous SRAM, one SN74AHCT573N row-address latch and one SN74AHCT08N
CAS-to-output-enable gate. The Pico still performs the test; it does not
emulate cycle-accurate video RAM.

![Revision B2.1 tester with a single SRAM socket](docs/V9958-Tester-RevB2-SRAM-3D.png)

![Top view of the revision B2.1 SRAM tester showing the V9938/V9958 selector](docs/V9958-Tester-RevB2-SRAM-top.png)

The V9958 presents each memory address in two halves. U6 captures the row
address when `/RAS` falls. The live address becomes SRAM A0-A7, the latched
row becomes A8-A15, and `/CAS0` becomes A16. U7 asserts SRAM `/OE` when either
`/CAS0` or `/CAS1` is active. SRAM `/CE` is held low and V9958 `R/W` drives
SRAM `/WE` through a 47-ohm damping resistor.

This adaptation is intentionally marked **EXPERIMENTAL PROTOTYPE**. Static
ERC/DRC and connectivity checks cannot prove that the SRAM interface meets
the V9958's dynamic memory timing. Before trusting it as a chip tester, build
one unit and qualify TP8-TP12 with known-good chips of both models over supply and
temperature. Do not substitute slower SRAM.

J1 has the same keyed 2x3 video expansion pinout as Revision B: 1 GND, 2 +5 V,
3 red, 4 green, 5 blue and 6 CSYNC. It works with the existing optional RGB
DIN daughterboard.

The grouped [BOM](docs/BOM.csv), [schematic PDF](docs/V9958-Tester-RevB2-SRAM-Schematic.pdf),
[test procedure](docs/TEST-PROCEDURE.md), [design notes](docs/DESIGN-NOTES.md)
and [validation record](docs/VALIDATION.md) are included.
