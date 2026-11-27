# V9958-Tester-RevB2-SRAM validation, revision B2.2

Checked on 2026-11-27 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Populated component references and BOM values in front Gerber | 80 of 80 pairs |
| Polarity verified on the PCB and in the front Gerber | 1 radial capacitor, 2 LEDs |
| Board | 160 × 110 mm, two copper layers and two filled ground zones |
| Layout | 96 footprints, 406 pads, 1754 track segments and vias including 88 vias |

The exported netlist passed checks for switch contacts, U3 pins 21 and 26, the two LM393P input dividers, pull-ups, SN74HC14N polarity, and the paths to U4 and the video output. The [shared design notes](../../docs/DESIGN-NOTES.md#model-selector-and-sync) give the calculated trip thresholds.

The existing Pico firmware was built with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester_revb2.uf2](../firmware/v9958_tester_revb2.uf2). SHA-256 `6b28ea2da0371b219dc8ad83acdeecabd55cea1fcb067daad56b7ffed16f150e`.

U5 pin 31 (CE2) connects to VCCVDP and pin 22 (/CE) to GND. SRAM bus timing still requires scope measurements at TP8–TP12 with a known-good sample of each model.

The fabrication archive is [V9958-Tester-RevB2-SRAM-B2.2-gerbers.zip](../fabrication/V9958-Tester-RevB2-SRAM-B2.2-gerbers.zip). SHA-256 `84192ff2aaf9ca102685277d2638c6eb01fba8ca43af7420382d09cd61f5a5a5`.

Physical qualification with known-good and known-faulty examples of each model is pending. The [test procedure](TEST-PROCEDURE.md) covers empty-socket reference checks and pulse-width measurements with a 75 Ω terminated display input.
