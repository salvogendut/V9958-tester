# V9958-Tester-RevB validation, revision B1.1

Checked on 2026-11-27 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Populated component references and BOM values in front Gerber | 82 of 82 pairs |
| Polarity verified on the PCB and in the front Gerber | 1 radial capacitor, 2 LEDs |
| Board | 170 × 118 mm, two copper layers and two filled ground zones |
| Layout | 93 footprints, 409 pads, 1838 track segments and vias including 75 vias |

The exported netlist passed checks for switch contacts, U3 pins 21 and 26, the two LM393P input dividers, pull-ups, SN74HC14N polarity, and the paths to U4 and the video output. The [shared design notes](../../docs/DESIGN-NOTES.md#model-selector-and-sync) give the calculated trip thresholds.

The existing Pico firmware was built with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester_revb.uf2](../firmware/v9958_tester_revb.uf2). SHA-256 `826f2566cb332a4429cbb08eea7491cd00bfa5de1e7930c7a94dc476f72dde3a`.

The fabrication archive is [V9958-Tester-RevB-B1.1-gerbers.zip](../fabrication/V9958-Tester-RevB-B1.1-gerbers.zip). SHA-256 `1de083052d694b57cdcc5556400f773bfdd97399e471798ae3704ff699227bc6`.

Physical qualification with known-good and known-faulty examples of each model is pending. The [test procedure](TEST-PROCEDURE.md) covers empty-socket reference checks and pulse-width measurements with a 75 Ω terminated display input.
