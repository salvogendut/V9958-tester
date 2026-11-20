# V9958-Tester validation, revision 0.4

Checked on 2026-11-20 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Board | 232 × 141 mm, two copper layers and two filled ground zones |
| Layout | 109 footprints, 475 pads, 2260 track segments and vias including 137 vias |

The layout audit located the DIN face on the top board edge. The ten copper flashes on each copper layer coincide with the plated drills, and the two alignment holes coincide with the non-plated drill file. The cable approaches from outside the board.

The exported netlist passed the independent pin-21 supply, sync receiver, switch-contact and pin-26 checks. The Pico firmware compiled with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester.uf2](../firmware/v9958_tester.uf2). SHA-256 `183095236de97ed0596dc7efb1447e5f6b24492c213e010776b26c111c45b933`.

The fabrication archive is [V9958-Tester-rev0.4-gerbers.zip](../fabrication/V9958-Tester-rev0.4-gerbers.zip). SHA-256 `a6ac0c550e198c88a79f9af78ea0ad8240817ad370d2e7d5ed3c550949e8969e`.

Physical qualification with known-good and known-faulty examples of each model is pending. Check the selector resistance with the socket empty before installing a VDP.
