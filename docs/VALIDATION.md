# V9958-Tester validation, revision 0.5

Checked on 2026-11-27 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Populated component references and BOM values in front Gerber | 104 of 104 pairs |
| Polarity verified on the PCB and in the front Gerber | 7 radial capacitors, 2 LEDs |
| Board | 232 × 141 mm, two copper layers and two filled ground zones |
| Layout | 117 footprints, 503 pads, 2357 track segments and vias including 119 vias |

The layout audit located the DIN face on the top board edge. The ten copper flashes on each copper layer coincide with the plated drills, and the two alignment holes coincide with the non-plated drill file. The cable approaches from outside the board.

The exported netlist passed checks for switch contacts, U3 pins 21 and 26, the two LM393P input dividers, pull-ups, SN74HC14N polarity, and the paths to U4 and the video output. The [shared design notes](DESIGN-NOTES.md#model-selector-and-sync) give the calculated trip thresholds.

The existing Pico firmware was built with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester.uf2](../firmware/v9958_tester.uf2). SHA-256 `183095236de97ed0596dc7efb1447e5f6b24492c213e010776b26c111c45b933`.

The fabrication archive is [V9958-Tester-rev0.5-gerbers.zip](../fabrication/V9958-Tester-rev0.5-gerbers.zip). SHA-256 `7e02a6ec98cc515bca9bcd2b4b677f34a4e0e8576bb3405300a9387de73b33c9`.

Physical qualification with known-good and known-faulty examples of each model is pending. The [test procedure](TEST-PROCEDURE.md) covers empty-socket reference checks and pulse-width measurements with a 75 Ω terminated display input.
