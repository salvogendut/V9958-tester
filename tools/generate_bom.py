#!/usr/bin/env python3
"""Generate the grouped BOM from KiCad's XML netlist."""

import csv
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
tree = ET.parse(ROOT / "docs" / "V9958-Tester.xml").getroot()
groups = defaultdict(list)
for comp in tree.findall("./components/comp"):
    value = comp.findtext("value")
    footprint = comp.findtext("footprint")
    groups[(value, footprint)].append(comp.attrib["ref"])


def ref_key(ref):
    prefix = "".join(c for c in ref if not c.isdigit())
    number = int("".join(c for c in ref if c.isdigit()) or 0)
    return prefix, number


notes = {
    "V9958 DUT": "DUT; use a quality 64-pin 1.778 mm-pitch, 19.05 mm-row socket/ZIF",
    "Raspberry Pi Pico": "Original RP2040 Pico module; fit using two 1x20 THT socket strips",
    "41464 VRAM L0": "64Kx4 DRAM, 120 ns or faster; socket recommended",
    "41464 VRAM H0": "64Kx4 DRAM, 120 ns or faster; socket recommended",
    "41464 VRAM L1": "64Kx4 DRAM, 120 ns or faster; socket recommended",
    "41464 VRAM H1": "64Kx4 DRAM, 120 ns or faster; socket recommended",
    "SN74LVC245AN": "Use LVC, powered at 3.3 V; DIP socket recommended",
    "SN74LVC244AN": "Use LVC, powered at 3.3 V; DIP socket recommended",
    "SN74AHCT244N": "Use AHCT, powered at 5 V; DIP socket recommended",
    "10k bussed": "10-pin bussed/common SIP network; common pin is pin 1",
    "Bourns MF-RHT100 PTC 1.0A": "1.0 A hold / 1.8 A trip resettable fuse",
    "21.477270MHz": "Parallel-resonant fundamental crystal, HC49/U THT",
    "30pF trimmer": "2-pin ceramic trimmer, 5.0 mm pitch",
}

out = ROOT / "docs" / "BOM.csv"
with out.open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(("Quantity", "References", "Value / part", "KiCad footprint", "Notes"))
    for (value, footprint), refs in sorted(groups.items(), key=lambda x: ref_key(sorted(x[1], key=ref_key)[0])):
        refs = sorted(refs, key=ref_key)
        writer.writerow((len(refs), " ".join(refs), value, footprint, notes.get(value, "")))
print(f"Wrote {out} with {len(groups)} grouped lines")

