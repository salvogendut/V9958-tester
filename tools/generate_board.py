#!/usr/bin/env python3
"""Create the placed two-layer V9958 tester board and export a DSN.

Run this script with KiCad's bundled Python/pcbnew environment.  Connectivity
comes exclusively from the ERC-clean XML netlist exported from the schematic.
"""

from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

import pcbnew as p


ROOT = Path(__file__).resolve().parents[1]
NAME = "V9958-Tester"
NETLIST = ROOT / "docs" / f"{NAME}.xml"
BOARD = ROOT / f"{NAME}.kicad_pcb"
PROJECT = ROOT / f"{NAME}.kicad_pro"
LIBROOT = Path("/app/share/kicad/footprints")
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAME}/schematic/root"))
M = p.FromMM


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAME}/{key}"))


def V(x, y):
    return p.VECTOR2I(M(round(x, 5)), M(round(y, 5)))


def add_text(board, text, x, y, size=1.0, layer=p.F_SilkS, angle=0):
    item = p.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(V(x, y))
    item.SetTextSize(V(size, size))
    item.SetTextThickness(M(0.15))
    item.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
    item.SetLayer(layer)
    if layer == p.B_SilkS:
        item.SetMirrored(True)
    board.Add(item)


project_bytes = PROJECT.read_bytes()
tree = ET.parse(NETLIST).getroot()
board = p.BOARD()
board.SetCopperLayerCount(2)
settings = board.GetDesignSettings()
settings.SetBoardThickness(M(1.6))
default = settings.m_NetSettings.GetDefaultNetclass()
default.SetClearance(M(0.30))
default.SetTrackWidth(M(0.25))
default.SetViaDiameter(M(0.70))
default.SetViaDrill(M(0.35))

title = board.GetTitleBlock()
title.SetTitle("V9958 Pico functional tester")
title.SetRevision("0.3 PROTOTYPE")
title.SetDate("2026-11-06")
title.SetCompany("Omega side project")

nets = {}
pad_net = {}
for item in tree.findall("./nets/net"):
    name = item.attrib["name"]
    net = p.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net
    for n in item.findall("node"):
        pad_net[(n.attrib["ref"], n.attrib["pin"])] = net

power_class = p.NETCLASS("Power")
power_class.SetClearance(M(0.30))
power_class.SetTrackWidth(M(0.60))
power_class.SetViaDiameter(M(0.80))
power_class.SetViaDrill(M(0.40))
settings.m_NetSettings.SetNetclass("Power", power_class)
for name in ("/+5V", "/+3V3", "/VCCVDP", "/VBUS_USB", "/GND"):
    if name in nets:
        nets[name].SetNetClass(power_class)
        settings.m_NetSettings.SetNetclassPatternAssignment(name, "Power")

# Locations are intentionally explicit: this is a human-reviewable fixture,
# not a generic placement result.  The Pico footprint origin is its USB end;
# x=228 puts the shell at the right board edge with the module extending left.
pos = {
    "A1": (228, 120, 270),
    "U1": (127, 35, 0), "U2": (143, 35, 0), "U4": (159, 35, 0),
    "U3": (88, 63, 0),
    "U5": (50, 20, 90), "U6": (80, 20, 90),
    "U7": (110, 20, 90), "U8": (140, 20, 90),
    "RN1": (63, 80, 0),
    # Oscillator loop is kept short and immediately beside V9958 pins 63/64.
    "Y1": (49, 52, 0), "R4": (49, 47, 0),
    "C1": (42, 59, 0), "C2": (51, 59, 0),
    "R1": (97, 80, 0), "R2": (108, 80, 0), "R3": (119, 80, 0),
    "R5": (50, 40, 0), "R6": (64, 40, 0),
    "R7": (78, 40, 0), "R8": (92, 40, 0),
    "R9": (121, 65, 0), "R10": (121, 70, 0), "R11": (121, 75, 0),
    "R12": (132, 65, 0), "R13": (132, 70, 0),
    "R14": (161, 75, 90), "R15": (170, 75, 90),
    "R16": (161, 86, 90), "R17": (170, 86, 90),
    "R18": (161, 97, 90), "R19": (170, 97, 90),
    "R20": (160, 108, 0),
    "R21": (18, 87, 0), "R22": (30, 87, 0), "R23": (42, 87, 0), "C3": (53, 87, 0),
    "R24": (18, 98, 0), "R25": (30, 98, 0), "R26": (42, 98, 0), "C4": (53, 98, 0),
    "R27": (18, 109, 0), "R28": (30, 109, 0), "R29": (42, 109, 0), "C5": (53, 109, 0),
    "R30": (64, 91, 0), "D1": (76, 91, 0),
    "R31": (64, 101, 0), "D2": (76, 101, 0),
    "SW1": (88, 101, 0), "R32": (86, 112, 0),
    "F1": (164, 113, 0), "L1": (116, 116, 0),
    "C6": (101, 116, 0), "C7": (90, 116, 0), "C8": (119, 60, 0),
    "C9": (128, 61, 0), "C10": (144, 61, 0), "C11": (160, 61, 0),
    "C12": (44, 31, 0), "C13": (74, 31, 0),
    "C14": (104, 31, 0), "C15": (134, 31, 0),
    # CXA1645 RGB buffer and Omega-compatible DIN output occupy the added
    # upper-right service area.  Keep 75R output resistors close to U9.
    "U9": (190, 57, 0), "J1": (205, 20, 180),
    "C16": (177, 46, 90), "C17": (177, 57, 90), "C18": (177, 68, 90),
    "C19": (174, 78, 0), "R33": (205, 85, 0), "C20": (205, 92, 0),
    "C21": (219, 84, 0), "R34": (205, 72, 0),
    "C22": (177, 88, 0), "C23": (188, 91, 0),
    "C24": (215, 90, 0), "C25": (224, 90, 0),
    "R35": (205, 41, 0), "C26": (218, 41, 0),
    "R36": (205, 51, 0), "C27": (218, 51, 0),
    "R37": (205, 61, 0), "C28": (218, 61, 0),
    "R38": (216, 68, 0),
    "R39": (179, 96, 0), "R40": (191, 96, 0),
    "R41": (203, 96, 0), "R42": (215, 96, 0),
    "TP1": (10, 15, 0), "TP2": (10, 22, 0), "TP3": (10, 29, 0),
    "TP4": (10, 45, 0), "TP5": (10, 55, 0), "TP6": (10, 65, 0),
    "TP7": (10, 87, 0), "TP8": (10, 98, 0), "TP9": (10, 109, 0),
    "H1": (5, 5, 0), "H2": (225, 5, 0),
    "H3": (5, 135, 0), "H4": (170, 135, 0),
}

components = {c.attrib["ref"]: c for c in tree.findall("./components/comp")}
if set(pos) != set(components):
    raise RuntimeError(f"Placement mismatch: missing={set(components)-set(pos)}, extra={set(pos)-set(components)}")

footprints = {}
reference_positions = {
    "A1": (174, 125), "C7": (90, 112), "F1": (164, 104.5),
    "Y1": (49, 56), "J1": (190, 30), "R38": (226, 68),
    "R41": (207, 99),
    "TP1": (6, 15), "TP2": (6, 22), "TP3": (6, 29),
    "TP4": (6, 45), "TP5": (6, 55), "TP6": (6, 65),
    "TP7": (6, 87), "TP8": (6, 98), "TP9": (6, 109),
    "H1": (9, 5), "H2": (221, 5), "H3": (9, 135), "H4": (166, 135),
}
for ref, comp in components.items():
    fpid = comp.findtext("footprint")
    lib, name = fpid.split(":", 1)
    root = ROOT / f"{NAME}.pretty" if lib == NAME else LIBROOT / f"{lib}.pretty"
    fp = p.FootprintLoad(str(root), name)
    if fp is None:
        raise RuntimeError(f"Cannot load footprint {fpid} from {root}")
    fp.SetReference(ref)
    fp.SetValue(comp.findtext("value"))
    fp.SetFPID(p.LIB_ID(lib, name))
    fp.SetPath(p.KIID_PATH(f"/{ROOT_UUID}/{uid(ref)}"))
    x, y, angle = pos[ref]
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(angle)
    fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(V(0.85, 0.85))
    fp.Reference().SetTextThickness(M(0.13))
    fp.Reference().SetKeepUpright(True)
    fp.Reference().SetVisible(True)
    if ref in reference_positions:
        fp.Reference().SetPosition(V(*reference_positions[ref]))
        fp.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
    if ref == "U3":
        fp.Reference().SetPosition(V(88, 63))
    for pad in fp.Pads():
        net = pad_net.get((ref, pad.GetNumber()))
        if net is not None:
            pad.SetNet(net)
    board.Add(fp)
    footprints[ref] = fp

# Rectangular 232 x 141 mm outline.  The added service area holds the DIN
# video buffer and leaves 4 mm between the Pico USB origin and the edge.
outline = [(0, 0), (232, 0), (232, 141), (0, 141)]
for a, b in zip(outline, outline[1:] + outline[:1]):
    edge = p.PCB_SHAPE(board)
    edge.SetShape(p.SHAPE_T_SEGMENT)
    edge.SetStart(V(*a)); edge.SetEnd(V(*b))
    edge.SetLayer(p.Edge_Cuts); edge.SetWidth(M(0.05))
    board.Add(edge)

add_text(board, "V9958 PICO FUNCTIONAL TESTER", 115, 5, 1.6)
add_text(board, "REV 0.3  PROTOTYPE / UNVALIDATED", 115, 8, 0.9)
add_text(board, "POWER OFF BEFORE INSERTING OR REMOVING DUT", 88, 63, 0.9, p.B_SilkS)
add_text(board, "PIN 1", 60, 76, 0.8)
add_text(board, "PASS", 76, 95, 0.8)
add_text(board, "FAIL", 76, 105, 0.8)
add_text(board, "TEST", 100, 101, 0.8)
add_text(board, "F1 1A PTC", 167, 119, 0.8)
add_text(board, "USB POWER / SERIAL", 228, 106, 0.8, angle=90)
add_text(board, "OMEGA RGB DIN", 205, 22, 0.9)
add_text(board, "1:GND  4:SYNC  6:R  7:G  8:B", 205, 25, 0.8)
add_text(board, "(c) salvogendut 2026", 115, 135, 1.0)
add_text(board, "V9958 behavioral tester - not forensic authentication", 115, 138, 0.8, p.B_SilkS)
for label, y in (("5V", 15), ("3V3", 22), ("GND", 29),
                 ("CPUCLK", 45), ("HSYNC", 55), ("CSYNC", 65),
                 ("R", 87), ("G", 98), ("B", 109)):
    add_text(board, label, 15, y, 0.80)

# Explicit polarity marks.  KiCad's LED_D5.0mm footprint is K=1, A=2;
# all polarized capacitor footprints use pad 1 as positive in this design.
for x, y in ((81.5, 91), (81.5, 101)):
    add_text(board, "+", x, y, 1.2)
for x, y in ((97.5, 116), (215.5, 84), (184.5, 91), (228.5, 86.5),
             (225.5, 41), (225.5, 51), (225.5, 61)):
    add_text(board, "+", x, y, 1.2)

p.SaveBoard(str(BOARD), board)
PROJECT.write_bytes(project_bytes)  # pcbnew must not rewrite project constraints.
dsn = ROOT / "docs" / "unrouted.dsn"
if not p.ExportSpecctraDSN(board, str(dsn)):
    raise RuntimeError("Specctra DSN export failed")
print(f"Placed {len(footprints)} footprints, {len(nets)} nets; wrote {BOARD.name} and {dsn.name}")
