# V9958-Video-Daughterboard validation, revision B1

Checked on 2026-11-20 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Board | 120 × 80 mm, two copper layers and two filled ground zones |
| Layout | 36 footprints, 98 pads, 216 track segments and vias including 1 vias |

The layout audit located the DIN face on the top board edge. The ten copper flashes on each copper layer coincide with the plated drills, and the two alignment holes coincide with the non-plated drill file. The cable approaches from outside the board.

The fabrication archive is [V9958-Video-Daughterboard-B1-gerbers.zip](../fabrication/V9958-Video-Daughterboard-B1-gerbers.zip). SHA-256 `dc69e9fefc03e0307ed6db2286e335fc77b4c41f7d61959857542e21f74352c0`.

Cable fit and terminated output levels still require a physical prototype.
