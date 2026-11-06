#!/usr/bin/env python3
"""Print fabrication-relevant counts for the two auxiliary boards."""

from pathlib import Path
import pcbnew as p

root = Path(__file__).resolve().parents[1]
for board_path in (
    root / "revision-b" / "V9958-Tester-RevB.kicad_pcb",
    root / "video-daughterboard" / "V9958-Video-Daughterboard.kicad_pcb",
):
    board = p.LoadBoard(str(board_path))
    footprints = list(board.GetFootprints())
    pads = [pad for footprint in footprints for pad in footprint.Pads()]
    smd = [pad for pad in pads if pad.GetAttribute() == p.PAD_ATTRIB_SMD]
    tracks = list(board.GetTracks())
    vias = [track for track in tracks if isinstance(track, p.PCB_VIA)]
    print(
        f"{board_path.name}: footprints={len(footprints)} pads={len(pads)} "
        f"smd_pads={len(smd)} tracks_vias={len(tracks)} vias={len(vias)} "
        f"zones={len(list(board.Zones()))}"
    )
