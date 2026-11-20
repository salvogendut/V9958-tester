#!/usr/bin/env python3
"""Check the two switch positions and DIN mating geometry on the released boards."""
from pathlib import Path
import xml.etree.ElementTree as ET

import pcbnew

ROOT = Path(__file__).resolve().parents[1]


def check_socket(netlist):
    tree = ET.parse(netlist)
    values = {item.get("ref"): item.findtext("value") for item in tree.findall("./components/comp")}
    assert [values[f"R{i}"] for i in range(43, 48)] == ["470", "2.2k 1%", "6.2k 1%", "3.9k 1%", "10k"]
    assert values["U10"] == "MAX942CPA+" and values["SW2"] == "JS202011CQN"
    pins = {}
    for net in tree.findall("./nets/net"):
        for node in net.findall("node"):
            pins[node.get("ref"), int(node.get("pin"))] = net.get("name").removeprefix("/")
    expected = {
        "VDP_PIN21": {("U3", 21), ("SW2", 2), ("R43", 2)},
        "HSYNC_RAW": {("U3", 5), ("U10", 3)},
        "CSYNC_RAW": {("U3", 6), ("U10", 5)},
        "SYNC_REF": {("U10", 2), ("U10", 6), ("SW2", 5)},
        "REF_38": {("R44", 2), ("R45", 1), ("SW2", 6)},
        "REF_58": {("R45", 2), ("R46", 1), ("SW2", 4)},
    }
    for net, contacts in expected.items():
        assert {pin for pin, actual in pins.items() if actual == net} == contacts, (netlist, net)
    for pin in [("U3", 58), ("SW2", 3), ("R43", 1), ("R44", 1), ("R47", 1), ("U10", 8)]:
        assert pins[pin] == "VCCVDP", (netlist, pin)
    assert pins["SW2", 1].startswith("unconnected-")
    assert pins["R46", 2] == pins["U10", 4] == "GND"
    assert pins["R47", 2] == pins["U3", 26] == "WAIT_RAW"
    assert pins["U10", 1] == "HSYNC_TTL" and pins["U10", 7] == "CSYNC_TTL"
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
    # Top view of the post-2022 SDF-80J: shield tabs nearest the plug, contact 8 last.
    pads = list(socket.Pads())
    depths = sorted(round(pcbnew.ToMM(pad.GetPosition().y - face), 2)
                    for pad in pads if pad.GetNumber() == "1")
    assert depths == [2.5, 2.5, 12.5]
    for pin, net in {1: "GND", 3: "DIN_AV", 4: "DIN_SYNC", 5: "DIN_YS",
                     6: "DIN_R", 7: "DIN_G", 8: "DIN_B"}.items():
        assert {p.GetNetname() for p in pads if p.GetNumber() == str(pin)} == {"/" + net}
    assert socket.FindPadByNumber("8").GetPosition().y == face + pcbnew.FromMM(17.5)


for path in sorted(ROOT.glob("**/*.kicad_pcb")):
    if path.parent.name == "video-daughterboard":
        check_din(pcbnew.LoadBoard(str(path)), "J2")
    else:
        check_socket(path.parent / "docs" / path.with_suffix(".xml").name)
        if path.parent == ROOT:
            check_din(pcbnew.LoadBoard(str(path)), "J1")
    print(f"{path.stem}: passed")
