# V9958-Tester-RevB validation, revision B1

Checked on 2026-11-25 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Populated component references and BOM values in front Gerber | 74 of 74 pairs |
| Polarity verified on the PCB and in the front Gerber | 1 radial capacitors, 2 LEDs |
| Board | 170 × 118 mm, two copper layers and two filled ground zones |
| Layout | 85 footprints, 381 pads, 1850 track segments and vias including 84 vias |

The exported netlist passed the independent pin-21 supply, sync receiver, switch-contact and pin-26 checks. The Pico firmware compiled with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester_revb.uf2](../firmware/v9958_tester_revb.uf2). SHA-256 `826f2566cb332a4429cbb08eea7491cd00bfa5de1e7930c7a94dc476f72dde3a`.

The fabrication archive is [V9958-Tester-RevB-B1-silk2-gerbers.zip](../fabrication/V9958-Tester-RevB-B1-silk2-gerbers.zip). SHA-256 `9a2c5c3500221d9a84aea62ea38b2a928f6380cabdc0ff305174bcb10e39ac13`.

Physical qualification with known-good and known-faulty examples of each model is pending. Check the selector resistance with the socket empty before installing a VDP.
