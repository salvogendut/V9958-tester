"""Generate LED anode marks and check the front silk against the schematic pins."""

from itertools import combinations
from math import hypot
import xml.etree.ElementTree as ET

import pcbnew as p


def is_plus(item):
    return (isinstance(item, p.PCB_TEXT) and item.GetLayer() == p.F_SilkS
            and item.GetText().strip() == "+")


def add_led_anode_marks(board):
    for fp in list(board.GetFootprints()):
        if fp.GetFPIDAsString() != "LED_THT:LED_D5.0mm" or any(is_plus(i) for i in fp.GraphicalItems()):
            continue
        # The 5 mm LED has its anode at local X=2.54 mm. Attach the legend
        # to the footprint so moving or rotating the LED also moves its mark.
        mark = p.PCB_TEXT(fp)
        mark.SetText("+")
        mark.SetLayer(p.F_SilkS)
        mark.SetTextSize(p.VECTOR2I(p.FromMM(1.2), p.FromMM(1.2)))
        mark.SetTextThickness(p.FromMM(0.18))
        mark.SetFPRelativePosition(p.VECTOR2I(p.FromMM(5.5), 0))
        fp.Add(mark)


def cross_centres(drawings):
    """KiCad radial footprints draw their + with two centred, perpendicular strokes."""
    strokes = []
    for item in drawings:
        if item.GetLayer() != p.F_SilkS:
            continue
        if is_plus(item) and item.IsVisible():
            yield item.GetPosition()
        if isinstance(item, p.PCB_SHAPE) and item.GetShape() == p.SHAPE_T_SEGMENT:
            start, end = item.GetStart(), item.GetEnd()
            strokes.append(((start + end) / 2, end - start))
    for (a, u), (b, v) in combinations(strokes, 2):
        # Integer rounding of rotated geometry can move a midpoint by a few nm.
        if hypot(a.x - b.x, a.y - b.y) > p.FromMM(0.002):
            continue
        lengths = hypot(u.x, u.y) * hypot(v.x, v.y)
        if lengths and abs(u.x * v.x + u.y * v.y) < 0.001 * lengths:
            yield a


def check_polarity(board, netlist):
    for centre in cross_centres(board.GetDrawings()):
        raise ValueError(f"Loose front-silk + at {centre}; attach polarity to the footprint")

    tree = ET.parse(netlist)
    nets = {(n.get("ref"), n.get("pin")): net.get("name")
            for net in tree.findall("./nets/net") for n in net.findall("node")}
    for component in tree.findall("./components/comp"):
        part = component.find("libsource").get("part")
        footprint_id = component.findtext("footprint", "")
        capacitor = part in ("CP", "C_Polarized") or ":CP_Radial" in footprint_id
        if not capacitor and part != "LED" and not footprint_id.startswith("LED_THT:"):
            continue
        ref = component.get("ref")
        fp = board.FindFootprintByReference(ref)
        if not fp or fp.GetLayer() != p.F_Cu:
            raise ValueError(f"{ref}: expected a front-side polarized footprint")
        pos, neg = ("1", "2") if capacitor else ("2", "1")
        positive, negative = fp.FindPadByNumber(pos), fp.FindPadByNumber(neg)
        for pin, pad in ((pos, positive), (neg, negative)):
            if not pad or pad.GetNetname() != nets[ref, pin]:
                raise ValueError(f"{ref}.{pin}: pad does not match schematic net {nets[ref, pin]}")
        if capacitor and (positive.GetShape() not in (p.PAD_SHAPE_RECT, p.PAD_SHAPE_ROUNDRECT)
                          or negative.GetShape() != p.PAD_SHAPE_CIRCLE):
            raise ValueError(f"{ref}: expected square positive pad 1 and circular negative pad 2")
        marks = list(cross_centres(fp.GraphicalItems()))
        if len(marks) != 1:
            raise ValueError(f"{ref}: expected one front-silk +, found {len(marks)}")
        distance_to_positive = (marks[0] - positive.GetPosition()).EuclideanNorm()
        distance_to_negative = (marks[0] - negative.GetPosition()).EuclideanNorm()
        if distance_to_positive >= distance_to_negative:
            raise ValueError(f"{ref}: front-silk + must be on the side of positive pad {pos}")


def check_fabrication_silk(path):
    """Compare the production front legend, including mask subtraction, with the audited board."""
    from pathlib import Path
    import subprocess
    from tempfile import TemporaryDirectory
    from zipfile import ZipFile

    production = path.parent / "fabrication"
    archive, = production.glob(f"{path.stem}-*-gerbers.zip")
    legend = path.stem + "-F_Silkscreen.gto"
    with ZipFile(archive) as package:
        released = package.read(legend)
    if released != (production / "gerbers" / legend).read_bytes():
        raise ValueError(f"{archive.name}: front silkscreen differs from the loose Gerber")
    with TemporaryDirectory() as out:
        subprocess.run(["kicad-cli", "pcb", "export", "gerbers", str(path), "--layers", "F.SilkS",
                        "--subtract-soldermask", "-o", out], check=True)
        plotted = (Path(out) / legend).read_bytes()

    def artwork(data):
        return [line for line in data.splitlines()
                if not line.startswith((b"%TF.CreationDate,", b"G04 Created by KiCad"))]

    if artwork(plotted) != artwork(released):
        raise ValueError(f"{archive.name}: front silkscreen is stale; re-export from {path.name}")


if __name__ == "__main__":
    from aux_projects import PROJECTS, REPO

    directories = [REPO] + [spec["directory"] for spec in PROJECTS.values()]
    for directory in directories:
        path, = directory.glob("*.kicad_pcb")
        check_polarity(p.LoadBoard(str(path)), directory / "docs" / (path.stem + ".xml"))
        check_fabrication_silk(path)
        print(f"{path.stem}: PCB, schematic pin assignments and packaged front silkscreen passed")
