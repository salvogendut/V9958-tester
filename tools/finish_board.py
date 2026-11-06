#!/usr/bin/env python3
"""Import the Freerouting session and add the two grounded copper pours."""

from pathlib import Path
import sys

import pcbnew as p


ROOT = Path(__file__).resolve().parents[1]
NAME = "V9958-Tester"
BOARD = ROOT / f"{NAME}.kicad_pcb"
PROJECT = ROOT / f"{NAME}.kicad_pro"
SESSION = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "routed.ses"
M = p.FromMM


def V(x, y):
    return p.VECTOR2I(M(x), M(y))


project_bytes = PROJECT.read_bytes()
board = p.LoadBoard(str(BOARD))
if not p.ImportSpecctraSES(board, str(SESSION)):
    raise RuntimeError(f"Could not import {SESSION}")

# The DSN is routed with a conservative 0.30 mm margin.  The delivered board
# rule remains 0.20 mm, so small coordinate quantization in SES import cannot
# create a marginal DRC result.
settings = board.GetDesignSettings()
settings.m_NetSettings.GetDefaultNetclass().SetClearance(M(0.20))
try:
    settings.m_NetSettings.GetNetclass("Power").SetClearance(M(0.20))
except Exception:
    pass

# Enforce the fabrication minimum used by the project even if an imported
# route segment inherited a smaller legacy width.
for track in board.GetTracks():
    if not isinstance(track, p.PCB_VIA) and track.GetWidth() < M(0.25):
        track.SetWidth(M(0.25))

# These three pads sit in locally fragmented plane areas after routing.  A
# direct local connection avoids misleading "thermal spoke to island" DRC
# results while the many other THT ground pads retain normal thermal relief.
for ref, number in (("A1", "13"), ("A1", "23"),
                    ("U8", "1"), ("U8", "18"), ("C10", "2")):
    fp = board.FindFootprintByReference(ref)
    pad = next(x for x in fp.Pads() if x.GetNumber() == number)
    pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)

gnd = board.FindNet("/GND")
if gnd is None:
    raise RuntimeError("GND net not found")
for layer in (p.F_Cu, p.B_Cu):
    zone = p.ZONE(board)
    zone.SetZoneName("GND plane")
    zone.SetLayer(layer)
    zone.SetNet(gnd)
    zone.SetLocalClearance(M(0.25))
    zone.SetMinThickness(M(0.20))
    zone.SetThermalReliefGap(M(0.25))
    zone.SetThermalReliefSpokeWidth(M(0.35))
    zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    poly = zone.Outline()
    poly.NewOutline()
    for x, y in ((0.5, 0.5), (230.5, 0.5), (230.5, 139.5), (0.5, 139.5)):
        poly.Append(M(x), M(y))
    board.Add(zone)

p.SaveBoard(str(BOARD), board)
PROJECT.write_bytes(project_bytes)
print(f"Imported {SESSION.name}; board now has {len(list(board.GetTracks()))} tracks/vias and two GND planes")
