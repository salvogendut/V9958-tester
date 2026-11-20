# V9958-Tester-RevB2-SRAM validation, revision B2.1

Checked on 2026-11-20 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Board | 160 × 110 mm, two copper layers and two filled ground zones |
| Layout | 88 footprints, 378 pads, 1667 track segments and vias including 65 vias |

The exported netlist passed the independent pin-21 supply, sync receiver, switch-contact and pin-26 checks. The Pico firmware compiled with Pico SDK 2.2.0 and Arm GNU 14.3.1. Picotool identified the RP2040 image with USB serial. A host model exercised 16 cases across both IDs, unsupported IDs and injected clock, sync, bus/WAIT, memory, interrupt and RGB faults.

The firmware image is [v9958_tester_revb2.uf2](../firmware/v9958_tester_revb2.uf2). SHA-256 `6b28ea2da0371b219dc8ad83acdeecabd55cea1fcb067daad56b7ffed16f150e`.

U5 pin 31 (CE2) connects to VCCVDP and pin 22 (/CE) to GND. SRAM bus timing still requires scope measurements at TP8–TP12 with a known-good sample of each model.

The fabrication archive is [V9958-Tester-RevB2-SRAM-B2.1-gerbers.zip](../fabrication/V9958-Tester-RevB2-SRAM-B2.1-gerbers.zip). SHA-256 `fddde5d5ec509d91d45c4dbbdbefcac226b953c19f847f08d71e578856ff9df4`.

Physical qualification with known-good and known-faulty examples of each model is pending. Check the selector resistance with the socket empty before installing a VDP.
