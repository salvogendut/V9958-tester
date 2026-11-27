#!/usr/bin/env python3
"""Check the two switch positions and DIN mating geometry on the released boards."""
from itertools import product
from pathlib import Path
import xml.etree.ElementTree as ET

import pcbnew
from polarity import check_polarity

ROOT = Path(__file__).resolve().parents[1]


def check_sync_thresholds(values):
    # TI LM393P input offset and bias, allowing for both inputs on the shared
    # reference ladder. Resistances below are in kΩ and voltages are in V.
    for top_ref, bottom_ref in (("R48", "R49"), ("R50", "R51")):
        refs = ("R44", "R45", "R46", top_ref, bottom_ref)
        nominal = [float(values[ref].removesuffix("k 1%")) for ref in refs]
        for factors in product((0.99, 1.01), repeat=5):
            r44, r45, r46, top, bottom = [r * k for r, k in zip(nominal, factors)]
            gain = bottom / (top + bottom)
            total = r44 + r45 + r46
            for rail in (4.75, 5.25):
                assert rail * gain + 0.010 < rail - 2.0  # input headroom at full-scale
                for lower, low_max, high_min in ((r45 + r46, 3.7, 4.5), (r46, 0.8, 2.2)):
                    reference = rail * lower / total
                    reference_r = lower * (total - lower) / total
                    error = 0.009 + 0.0004 * (top * gain + 2 * reference_r)
                    assert error < 0.025
                    assert low_max < (reference - 0.025) / gain
                    assert (reference + 0.025) / gain < high_min


def check_socket(netlist):
    tree = ET.parse(netlist)
    values = {item.get("ref"): item.findtext("value") for item in tree.findall("./components/comp")}
    assert [values[f"R{i}"] for i in range(43, 48)] == ["470", "15k 1%", "6.2k 1%", "4.3k 1%", "10k"]
    assert all(values[f"R{i}"] == "47k 1%" for i in (48, 49, 50, 51))
    assert values["R52"] == values["R53"] == "2.2k"
    assert values["C30"] == "100n" and values["U11"] == "SN74HC14N"
    assert values["U10"] == "LM393P" and values["SW2"] == "JS202011CQN"
    check_sync_thresholds(values)
    pins = {}
    for net in tree.findall("./nets/net"):
        for node in net.findall("node"):
            pins[node.get("ref"), int(node.get("pin"))] = net.get("name").removeprefix("/")
    expected = {
        "VDP_PIN21": {("U3", 21), ("SW2", 2), ("R43", 2)},
        "HSYNC_RAW": {("U3", 5), ("R48", 1)},
        "CSYNC_RAW": {("U3", 6), ("R50", 1)},
        "H_HALF": {("R48", 2), ("R49", 1), ("U10", 2)},
        "C_HALF": {("R50", 2), ("R51", 1), ("U10", 6)},
        "H_COMP": {("U10", 1), ("R52", 2), ("U11", 1)},
        "C_COMP": {("U10", 7), ("R53", 2), ("U11", 3)},
        "SYNC_REF": {("U10", 3), ("U10", 5), ("SW2", 5)},
        "REF_38": {("R44", 2), ("R45", 1), ("SW2", 6)},
        "REF_58": {("R45", 2), ("R46", 1), ("SW2", 4)},
    }
    for net, contacts in expected.items():
        assert {pin for pin, actual in pins.items() if actual == net} == contacts, (netlist, net)
    for pin in [("U3", 58), ("SW2", 3), ("R43", 1), ("R44", 1), ("R47", 1), ("U10", 8),
                ("R52", 1), ("R53", 1), ("U11", 14), ("C29", 1), ("C30", 1)]:
        assert pins[pin] == "VCCVDP", (netlist, pin)
    assert pins["SW2", 1].startswith("unconnected-")
    assert pins["R46", 2] == pins["U10", 4] == "GND"
    assert pins["R47", 2] == pins["U3", 26] == "WAIT_RAW"
    for pin in [("R49", 2), ("R51", 2), ("C29", 2), ("C30", 2)]:
        assert pins[pin] == "GND"
    for pin in (5, 7, 9, 11, 13):
        assert pins["U11", pin] == "GND"
    for pin in (6, 8, 10, 12):
        assert pins["U11", pin].startswith("unconnected-")
    assert pins["U11", 2] == "HSYNC_TTL" and pins["U11", 4] == "CSYNC_TTL"
    # Confirm the driven signals reach the existing 3.3 V monitor buffer.
    for signal, u4pin in (("HSYNC_TTL", 4), ("CSYNC_TTL", 6)):
        destination = pins["U4", u4pin]
        assert any(pins.get((ref, 1)) == signal and pins.get((ref, 2)) == destination
                   for ref in values if ref.startswith("R"))
    if ("U9", 10) in pins:
        assert pins["U9", 10] == pins["R38", 1] == "CSYNC_TTL"
    else:
        assert pins["J1", 6] == "CSYNC_TTL"


def check_din(board, ref):
    socket = board.FindFootprintByReference(ref)
    face = socket.GetPosition().y
    outline = board.GetBoardEdgesBoundingBox()
    assert abs(outline.GetTop() - face) <= pcbnew.FromMM(0.03)
    assert socket.GetOrientationDegrees() == 0 and socket.GetLayer() == pcbnew.F_Cu
    # SDS-J drawing p.5, top view rotated so the plug enters from the top.
    assert socket.GetValue() == "SDS-80J"
    plated = []
    locating = []
    for pad in socket.Pads():
        offset = pad.GetPosition() - socket.GetPosition()
        drill = pad.GetDrillSize()
        assert drill.x == drill.y
        hole = (pcbnew.ToMM(offset.x), pcbnew.ToMM(offset.y), pcbnew.ToMM(drill.x))
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            locating.append(hole)
        else:
            plated.append((pad.GetNumber(), *hole))
    assert sorted(locating) == [(-7.5, 7.5, 2.4), (7.5, 7.5, 2.4)]
    assert sorted(plated) == sorted([
        ("1", -2.5, 2.5, 1.3), ("1", 2.5, 2.5, 1.3),  # E ground terminals
        ("1", -5, 12.5, 1.3), ("2", 0, 12.5, 1.3), ("3", 5, 12.5, 1.3),
        ("4", -2.5, 15, 1.3), ("5", 2.5, 15, 1.3), ("6", -7.5, 15, 1.3),
        ("7", 7.5, 15, 1.3), ("8", 0, 17.5, 1.3),
    ])
    for pin, net in {1: "GND", 3: "DIN_AV", 4: "DIN_SYNC", 5: "DIN_YS",
                     6: "DIN_R", 7: "DIN_G", 8: "DIN_B"}.items():
        assert {p.GetNetname() for p in socket.Pads() if p.GetNumber() == str(pin)} == {"/" + net}
    assert socket.FindPadByNumber("2").GetNetname() == f"unconnected-({ref}-AUDIO-Pad2)"


for path in sorted(ROOT.glob("**/*.kicad_pcb")):
    board = pcbnew.LoadBoard(str(path))
    netlist = path.parent / "docs" / path.with_suffix(".xml").name
    check_polarity(board, netlist)
    if path.parent.name == "video-daughterboard":
        check_din(board, "J2")
    else:
        check_socket(netlist)
        if path.parent == ROOT:
            check_din(board, "J1")
    print(f"{path.stem}: passed")
