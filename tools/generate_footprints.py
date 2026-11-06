#!/usr/bin/env python3
"""Generate the two small local footprint definitions used by the tester."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "V9958-Tester.pretty"
LIB.mkdir(exist_ok=True)


def pad(num, x, y, rect=False):
    shape = "rect" if rect else "oval"
    return (
        f'  (pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) '
        # 1.778 mm pitch requires a narrow copper width.  A 1.40 mm pad with
        # 0.90 mm drill retains 0.25 mm annular copper and 0.378 mm pin gap.
        f'(size 1.40 1.80) (drill 0.9) (layers "*.Cu" "*.Mask"))'
    )


lines = [
    '(footprint "SDIP-64_W19.05mm_P1.778mm_Socket"',
    '  (version 20240108)',
    '  (generator "v9958-tester-generator")',
    '  (layer "F.Cu")',
    '  (descr "V9958 64-pin shrink DIP, 1.778mm pitch, 19.05mm row spacing, socket-friendly holes")',
    '  (tags "V9958 SDIP64 socket")',
    '  (attr through_hole)',
    '  (fp_rect (start -29 -8.0) (end 29 8.0) (stroke (width 0.25) (type default)) (fill none) (layer "F.SilkS"))',
    '  (fp_arc (start -29 -1.5) (mid -27.5 0) (end -29 1.5) (stroke (width 0.25) (type default)) (fill none) (layer "F.SilkS"))',
    '  (fp_rect (start -29.3 -9.3) (end 29.3 9.3) (stroke (width 0.1) (type default)) (fill none) (layer "F.CrtYd"))',
    '  (fp_text reference "REF**" (at 0 -10.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
    '  (fp_text value "V9958" (at 0 10.5) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
    '  (fp_text user "PIN 1" (at -25.5 6.5) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
]

for n in range(1, 33):
    x = -27.559 + (n - 1) * 1.778
    lines.append(pad(n, x, 9.525, n == 1))
for n in range(33, 65):
    x = 27.559 - (n - 33) * 1.778
    lines.append(pad(n, x, -9.525))
lines.append(')')
(LIB / "SDIP-64_W19.05mm_P1.778mm_Socket.kicad_mod").write_text("\n".join(lines) + "\n")

trim = '''(footprint "C_Trim_P5.00mm"
  (version 20240108)
  (generator "v9958-tester-generator")
  (layer "F.Cu")
  (descr "Generic 2-pin 5mm pitch ceramic trimmer capacitor")
  (tags "trimmer capacitor THT")
  (attr through_hole)
  (fp_rect (start -1.25 -2.5) (end 6.25 2.5) (stroke (width 0.25) (type default)) (fill none) (layer "F.SilkS"))
  (fp_circle (center 2.5 0) (end 3.7 0) (stroke (width 0.2) (type default)) (fill none) (layer "F.SilkS"))
  (fp_text reference "REF**" (at 2.5 -3.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (fp_text value "C_Trim" (at 2.5 3.5) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (pad "1" thru_hole rect (at 0 0) (size 2 2) (drill 0.9) (layers "*.Cu" "*.Mask"))
  (pad "2" thru_hole circle (at 5 0) (size 2 2) (drill 0.9) (layers "*.Cu" "*.Mask"))
)
'''
(LIB / "C_Trim_P5.00mm.kicad_mod").write_text(trim)

(ROOT / "fp-lib-table").write_text(
    '(fp_lib_table\n'
    '  (version 7)\n'
    '  (lib (name "V9958-Tester")(type "KiCad")(uri "${KIPRJMOD}/V9958-Tester.pretty")(options "")(descr "Local V9958 tester footprints"))\n'
    ')\n'
)

print("Generated local V9958 and trimmer footprints")
