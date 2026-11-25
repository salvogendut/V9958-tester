# V9958-Video-Daughterboard validation, revision B1

Checked on 2026-11-25 with KiCad 10.0.8.

| Check | Result |
|---|---|
| Schematic ERC | 0 violations |
| PCB DRC with filled zones | 0 violations |
| Unconnected items / schematic parity issues | 0 / 0 |
| Populated component references and BOM values in front Gerber | 26 of 26 pairs |
| Polarity verified on the PCB and in the front Gerber | 6 radial capacitors, 0 LEDs |
| Board | 120 × 80 mm, two copper layers and two filled ground zones |
| Layout | 36 footprints, 98 pads, 216 track segments and vias including 1 vias |

The layout audit located the DIN face on the top board edge. The ten copper flashes on each copper layer coincide with the plated drills, and the two alignment holes coincide with the non-plated drill file. The cable approaches from outside the board.

The fabrication archive is [V9958-Video-Daughterboard-B1-silk2-gerbers.zip](../fabrication/V9958-Video-Daughterboard-B1-silk2-gerbers.zip). SHA-256 `d64642aea64091ee003636d9e74bbf8a991bca2b238baee704bc3bd28b31446b`.

Cable fit and terminated output levels still require a physical prototype.
