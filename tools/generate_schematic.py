#!/usr/bin/env python3
"""Generate the native KiCad 10 schematic from the reviewed connection table."""

import importlib.util
import json
import pathlib
import uuid
import copy

from sexpr import dump, node, nodes, parse


ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = "V9958-Tester"
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAME}/schematic/root"))


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAME}/{key}"))


def q(value):
    return json.dumps(str(value))


def effects(size=1.0, extra=""):
    return f'(effects (font (size {size} {size})) {extra})'


# Import the audited component/net table from the legacy-format generator.
spec = importlib.util.spec_from_file_location("legacy", ROOT / "tools" / "generate_legacy_schematic.py")
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
components = legacy.components


symbol_defs = {}
pin_locations = {}


def custom_rect(name, pin_names, left_count, half_width=12.7, pitch=2.54):
    count = len(pin_names)
    left = list(range(1, left_count + 1))
    right = list(range(left_count + 1, count + 1))
    max_count = max(len(left), len(right), 1)
    half_height = (max_count - 1) * pitch / 2 + 2.54
    body = (
        f'(symbol {q(name + "_0_1")} '
        f'(rectangle (start {-half_width} {half_height}) (end {half_width} {-half_height}) '
        f'(stroke (width 0.254) (type default)) (fill (type background))))'
    )
    pins = []
    locations = {}
    for side, nums in (("L", left), ("R", right)):
        top = (len(nums) - 1) * pitch / 2
        for index, num in enumerate(nums):
            y = round(top - index * pitch, 4)
            if side == "L":
                x, angle = -(half_width + 5.08), 0
            else:
                x, angle = half_width + 5.08, 180
            pname = pin_names[num]
            pins.append(
                f'(pin passive line (at {x} {y} {angle}) (length 5.08) '
                f'(name {q(pname)} {effects(0.9)}) (number {q(num)} {effects(0.9)}))'
            )
            locations[str(num)] = (x, y, angle)
    text = (
        f'(symbol {q(name)} (pin_names (offset 0.8)) (exclude_from_sim no) '
        f'(in_bom yes) (on_board yes) '
        f'(property "Reference" "U" (at 0 {half_height + 5.08} 0) {effects(1.27)}) '
        f'(property "Value" {q(name)} (at 0 {half_height + 2.54} 0) {effects(1.27)}) '
        f'{body} (symbol {q(name + "_1_1")} {"".join(pins)}))'
    )
    symbol_defs[name] = parse(text)
    pin_locations[name] = locations


def custom_two_pin(name, reference):
    text = (
        f'(symbol {q(name)} (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) '
        f'(in_bom yes) (on_board yes) '
        f'(property "Reference" {q(reference)} (at 0 3.81 0) {effects(1.0)}) '
        f'(property "Value" {q(name)} (at 0 -3.81 0) {effects(1.0)}) '
        f'(symbol {q(name + "_0_1")} '
        f'(rectangle (start -2.54 1.27) (end 2.54 -1.27) (stroke (width 0.254) (type default)) (fill (type background)))) '
        f'(symbol {q(name + "_1_1")} '
        f'(pin passive line (at -7.62 0 0) (length 5.08) (name "1" {effects(0.8)}) (number "1" {effects(0.8)})) '
        f'(pin passive line (at 7.62 0 180) (length 5.08) (name "2" {effects(0.8)}) (number "2" {effects(0.8)}))))'
    )
    symbol_defs[name] = parse(text)
    pin_locations[name] = {"1": (-7.62, 0, 0), "2": (7.62, 0, 180)}


def custom_one_pin(name, reference, in_bom="yes"):
    text = (
        f'(symbol {q(name)} (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) '
        f'(in_bom {in_bom}) (on_board yes) '
        f'(property "Reference" {q(reference)} (at 0 3.81 0) {effects(1.0)}) '
        f'(property "Value" {q(name)} (at 0 -3.81 0) {effects(1.0)}) '
        f'(symbol {q(name + "_0_1")} '
        f'(circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))) '
        f'(symbol {q(name + "_1_1")} '
        f'(pin passive line (at 0 -7.62 90) (length 5.08) (name "1" {effects(0.8)}) (number "1" {effects(0.8)}))))'
    )
    symbol_defs[name] = parse(text)
    pin_locations[name] = {"1": (0, -7.62, 90)}


def custom_zero_pin(name, reference, in_bom="no"):
    text = (
        f'(symbol {q(name)} (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) '
        f'(in_bom {in_bom}) (on_board yes) '
        f'(property "Reference" {q(reference)} (at 0 3.81 0) {effects(1.0)}) '
        f'(property "Value" {q(name)} (at 0 -3.81 0) {effects(1.0)}) '
        f'(symbol {q(name + "_0_1")} '
        f'(circle (center 0 0) (radius 2.54) (stroke (width 0.254) (type default)) (fill (type none)))))'
    )
    symbol_defs[name] = parse(text)
    pin_locations[name] = {}


custom_rect("V9958", legacy.v9958_names, 32, 15.24, 2.54)
custom_rect("RaspberryPi_Pico", legacy.pico_names, 20, 15.24, 2.54)
custom_rect("D41464", legacy.dram_names, 9, 10.16, 2.54)
custom_rect("SN74LVC245A", legacy.buf245_names, 10, 10.16, 2.54)
custom_rect("SN74AHCT244", legacy.buf244_names, 10, 10.16, 2.54)
custom_rect("SN74LVC244A", legacy.buf244_names, 10, 10.16, 2.54)
custom_rect("RN_Bussed_10", legacy.rn_names, 10, 8.89, 2.54)
custom_rect("CXA1645", legacy.cxa1645_names, 12, 11.43, 2.54)
custom_rect("DIN8_Omega", legacy.din8_names, 4, 8.89, 2.54)
for symbol, reference in [
    ("R", "R"), ("C", "C"), ("CP", "C"), ("L", "L"), ("Crystal", "Y"),
    ("Fuse", "F"), ("LED", "D"), ("SW_Push", "SW"),
]:
    custom_two_pin(symbol, reference)
custom_one_pin("TestPoint", "TP", "no")
custom_zero_pin("MountingHole", "H", "no")


body = []


def add_wire(x1, y1, x2, y2, tag):
    body.append(
        f'(wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})) '
        f'(stroke (width 0) (type default)) (uuid {uid(tag)}))'
    )


def add_label(name, x, y, justify, tag):
    body.append(
        f'(label {q(name)} (at {x:.4f} {y:.4f} 0) '
        f'{effects(0.9, f"(justify {justify} bottom)")} (uuid {uid(tag)}))'
    )


for comp in components:
    ref = comp["ref"]
    symbol_name = comp["symbol"]
    x = comp["x"] * 0.0254
    y = comp["y"] * 0.0254
    symbol = symbol_defs[symbol_name]
    lib_id = f"{NAME}:{symbol_name}"
    pin_nodes = [pin for sub in nodes(symbol, "symbol") for pin in nodes(sub, "pin")]
    max_y = max((abs(float(node(pin, "at")[2])) for pin in pin_nodes), default=0)
    in_bom = "no" if ref.startswith(("H", "TP")) else "yes"
    props = "".join([
        f'(property "Reference" {q(ref)} (at {x:.4f} {y-max_y-5.08:.4f} 0) {effects(1.0)})',
        f'(property "Value" {q(comp["value"])} (at {x:.4f} {y-max_y-2.54:.4f} 0) {effects(1.0)})',
        f'(property "Footprint" {q(comp["footprint"])} (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})',
        f'(property "Datasheet" "" (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})',
        f'(property "Description" "" (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})',
    ])
    body.append(
        f'(symbol (lib_id {q(lib_id)}) (at {x:.4f} {y:.4f} 0) (unit 1) '
        f'(in_bom {in_bom}) (on_board yes) (dnp no) (uuid {uid(ref)}) {props} '
        f'(instances (project {q(NAME)} (path {q("/" + ROOT_UUID)} (reference {q(ref)}) (unit 1)))))'
    )
    for pnum, (px_rel, py_rel, angle) in pin_locations[symbol_name].items():
        px = x + px_rel
        py = y - py_rel
        net = comp["nets"].get(str(pnum))
        if net is None or net.startswith("NC_"):
            body.append(f'(no_connect (at {px:.4f} {py:.4f}) (uuid {uid(ref + "/nc/" + pnum)}))')
            continue
        # Keep the labelled stubs deliberately short.  The compact component
        # rows otherwise let adjacent passive stubs touch and silently merge
        # unrelated nets in Eeschema.
        dx, dy = {0: (-1.27, 0), 180: (1.27, 0), 90: (0, 1.27), 270: (0, -1.27)}[angle]
        ex, ey = px + dx, py + dy
        add_wire(px, py, ex, ey, f"{ref}/wire/{pnum}")
        justify = "right" if dx < 0 else "left"
        add_label(net, ex, ey, justify, f"{ref}/label/{pnum}")


for index, (text, x, y, size) in enumerate([
    ("V9958 PICO FUNCTIONAL TESTER - PROTOTYPE REV 0.3", 20.32, 17.78, 2.0),
    ("Checks V9958 ID, CPU interface, 128 KiB VRAM, clocks/sync, interrupt and RGB response; buffered DIN RGB output.", 20.32, 22.86, 1.2),
    ("WARNING: power off before inserting/removing V9958 or VRAM. Use a current-limited 5V / 1A USB supply.", 20.32, 27.94, 1.2),
    ("Behavioral V9958 test only; a pass is not forensic proof of Yamaha manufacture.", 20.32, 33.02, 1.2),
]):
    body.append(
        f'(text {q(text)} (at {x} {y} 0) {effects(size, "(justify left)")} (uuid {uid("note/" + str(index))}))'
    )


embedded = []
for key, symbol in symbol_defs.items():
    current = copy.deepcopy(symbol)
    current[1] = f"{NAME}:{key}"
    embedded.append(dump(current))

output = (
    f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {ROOT_UUID}) (paper "A3") '
    f'(title_block (title "V9958 Pico Functional Tester") (date "2026-11-06") '
    f'(rev "0.3 - PROTOTYPE") (company "Omega side project") '
    f'(comment 1 "Unbuilt prototype; verify socket and parts before fabrication") '
    f'(comment 2 "Power off before inserting or removing DUT")) '
    f'(lib_symbols {" ".join(embedded)}) '
    f'{" ".join(body)} '
    f'(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
)
(ROOT / f"{NAME}.kicad_sch").write_text(output)

# Standalone symbol library for normal editing after opening the project.
standalone = []
for key, symbol in symbol_defs.items():
    current = copy.deepcopy(symbol)
    current[1] = key
    standalone.append(dump(current))
(ROOT / f"{NAME}.kicad_sym").write_text(
    '(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'
    + "\n".join(standalone) + "\n)\n"
)
(ROOT / "sym-lib-table").write_text(
    f'(sym_lib_table (version 7) (lib (name "{NAME}")(type "KiCad")'
    f'(uri "${{KIPRJMOD}}/{NAME}.kicad_sym")(options "")(descr "V9958 tester local symbols")))\n'
)

print(f"Generated native schematic with {len(components)} component instances")
