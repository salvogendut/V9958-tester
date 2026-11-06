#!/usr/bin/env python3
"""Generate the reviewable legacy schematic used as input to KiCad 10 upgrade.

The generated .sch is immediately upgraded to .kicad_sch by the project build
script.  Keeping this generator makes the repeated net labels and the 64-pin
V9958 symbol independently auditable.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "V9958-Tester"


def pin_rows(count, left=True, pitch=100):
    top = (count - 1) * pitch // 2
    x = -600 if left else 600
    orient = "R" if left else "L"
    return [(x, top - i * pitch, orient) for i in range(count)]


def rect_symbol(name, ref, pins, left_count, width=800, pitch=100):
    left = pin_rows(left_count, True, pitch)
    right = pin_rows(len(pins) - left_count, False, pitch)
    locs = left + right
    half_h = max(abs(y) for _, y, _ in locs) + 100
    out = [
        f"#\n# {name}\n#",
        f"DEF {name} {ref} 0 40 Y Y 1 F N",
        f'F0 "{ref}" -300 {half_h + 150} 50 H V L CNN',
        f'F1 "{name}" -300 {half_h + 50} 50 H V L CNN',
        'F2 "" 0 0 50 H I C CNN',
        'F3 "" 0 0 50 H I C CNN',
        "DRAW",
        f"S {-width//2} {half_h} {width//2} {-half_h} 0 1 10 f",
    ]
    endpoints = {}
    for (pname, pnum, ptype), (x, y, orient) in zip(pins, locs):
        endpoints[str(pnum)] = (x, y)
        out.append(f"X {pname} {pnum} {x} {y} 200 {orient} 40 40 1 1 {ptype}")
    out.extend(["ENDDRAW", "ENDDEF"])
    return "\n".join(out), endpoints


def two_pin_symbol(name, ref, drawing):
    out = [
        f"#\n# {name}\n#",
        f"DEF {name} {ref} 0 40 Y Y 1 F N",
        f'F0 "{ref}" 0 150 50 H V C CNN',
        f'F1 "{name}" 0 -150 50 H V C CNN',
        'F2 "" 0 0 50 H I C CNN',
        'F3 "" 0 0 50 H I C CNN',
        "DRAW",
        drawing,
        "X 1 1 -300 0 200 R 40 40 1 1 P",
        "X 2 2 300 0 200 L 40 40 1 1 P",
        "ENDDRAW",
        "ENDDEF",
    ]
    return "\n".join(out), {"1": (-300, 0), "2": (300, 0)}


def one_pin_symbol(name, ref, drawing):
    out = [
        f"#\n# {name}\n#",
        f"DEF {name} {ref} 0 40 Y Y 1 F N",
        f'F0 "{ref}" 0 150 50 H V C CNN',
        f'F1 "{name}" 0 -150 50 H V C CNN',
        'F2 "" 0 0 50 H I C CNN',
        'F3 "" 0 0 50 H I C CNN',
        "DRAW",
        drawing,
        "X 1 1 0 -300 200 U 40 40 1 1 P",
        "ENDDRAW",
        "ENDDEF",
    ]
    return "\n".join(out), {"1": (0, -300)}


v9958_names = {
    1: "GND", 2: "~DHCLK", 3: "~DLCLK", 4: "~VRESET", 5: "~HSYNC",
    6: "~CSYNC", 7: "BLEO", 8: "CPUCLK/~VDS", 9: "~RESET", 10: "~YS",
    11: "CBDR", 12: "C7", 13: "C6", 14: "C5", 15: "C4", 16: "C3",
    17: "C2", 18: "C1", 19: "C0", 20: "GND_DAC", 21: "VDD_DAC",
    22: "G", 23: "R", 24: "B", 25: "~INT", 26: "~WAIT",
    27: "~HRESET", 28: "MODE1", 29: "MODE0", 30: "~CSW", 31: "~CSR",
    32: "CD7", 33: "VBB", 34: "CD6", 35: "CD5", 36: "CD4", 37: "CD3",
    38: "CD2", 39: "CD1", 40: "CD0", 41: "RD0", 42: "RD1", 43: "RD2",
    44: "RD3", 45: "RD4", 46: "RD5", 47: "RD6", 48: "RD7", 49: "AD0",
    50: "AD1", 51: "AD2", 52: "AD3", 53: "AD4", 54: "AD5", 55: "AD6",
    56: "AD7", 57: "R/~W", 58: "VDD", 59: "~CASX", 60: "~CAS1",
    61: "~CAS0", 62: "~RAS", 63: "XTAL1", 64: "XTAL2",
}

pico_names = {
    1: "GP0", 2: "GP1", 3: "GND", 4: "GP2", 5: "GP3", 6: "GP4",
    7: "GP5", 8: "GND", 9: "GP6", 10: "GP7", 11: "GP8", 12: "GP9",
    13: "GND", 14: "GP10", 15: "GP11", 16: "GP12", 17: "GP13",
    18: "GND", 19: "GP14", 20: "GP15", 21: "GP16", 22: "GP17",
    23: "GND", 24: "GP18", 25: "GP19", 26: "GP20", 27: "GP21",
    28: "GND", 29: "GP22", 30: "RUN", 31: "GP26_ADC0", 32: "GP27_ADC1",
    33: "AGND", 34: "GP28_ADC2", 35: "ADC_VREF", 36: "3V3_OUT",
    37: "3V3_EN", 38: "GND", 39: "VSYS", 40: "VBUS",
}

dram_names = {
    1: "~OE", 2: "DQ0", 3: "DQ1", 4: "~WE", 5: "~RAS", 6: "A6",
    7: "A5", 8: "A4", 9: "VCC", 10: "A7", 11: "A3", 12: "A2",
    13: "A1", 14: "A0", 15: "DQ2", 16: "~CAS", 17: "DQ3", 18: "GND",
}

buf245_names = {
    1: "DIR", 2: "A0", 3: "A1", 4: "A2", 5: "A3", 6: "A4", 7: "A5",
    8: "A6", 9: "A7", 10: "GND", 11: "B7", 12: "B6", 13: "B5",
    14: "B4", 15: "B3", 16: "B2", 17: "B1", 18: "B0", 19: "~OE", 20: "VCC",
}

buf244_names = {
    1: "~1OE", 2: "1A1", 3: "2Y4", 4: "1A2", 5: "2Y3", 6: "1A3",
    7: "2Y2", 8: "1A4", 9: "2Y1", 10: "GND", 11: "2A1", 12: "1Y4",
    13: "2A2", 14: "1Y3", 15: "2A3", 16: "1Y2", 17: "2A4",
    18: "1Y1", 19: "~2OE", 20: "VCC",
}

rn_names = {1: "COM", **{i: str(i) for i in range(2, 11)}}

cxa1645_names = {
    1: "GND1", 2: "RIN", 3: "GIN", 4: "BIN", 5: "NC", 6: "SCIN",
    7: "NPIN", 8: "BFOUT", 9: "YCLPC", 10: "SYNCIN", 11: "NC",
    12: "VCC1", 13: "IREF", 14: "VREF", 15: "COUT", 16: "YOUT",
    17: "YTRAP", 18: "FO", 19: "VCC2", 20: "CVOUT", 21: "BOUT",
    22: "GOUT", 23: "ROUT", 24: "GND2",
}

din8_names = {
    1: "GND", 2: "AUDIO", 3: "AV", 4: "SYNC", 5: "YS",
    6: "RED", 7: "GREEN", 8: "BLUE",
}


def pin_list(names):
    return [(names[i], i, "P") for i in sorted(names)]


symbols = {}
lib_parts = []
for name, ref, names, left_count in [
    ("V9958", "U", v9958_names, 32),
    ("RaspberryPi_Pico", "A", pico_names, 20),
    ("D41464", "U", dram_names, 9),
    ("SN74LVC245A", "U", buf245_names, 10),
    ("SN74AHCT244", "U", buf244_names, 10),
    ("SN74LVC244A", "U", buf244_names, 10),
    ("RN_Bussed_10", "RN", rn_names, 10),
    ("CXA1645", "U", cxa1645_names, 12),
    ("DIN8_Omega", "J", din8_names, 4),
]:
    text, ep = rect_symbol(name, ref, pin_list(names), left_count)
    lib_parts.append(text)
    symbols[name] = ep

for name, ref, drawing in [
    ("R", "R", "S -100 50 100 -50 0 1 10 N"),
    ("C", "C", "P 2 0 1 10 -50 100 -50 -100 N\nP 2 0 1 10 50 100 50 -100 N"),
    ("CP", "C", "P 2 0 1 10 -50 100 -50 -100 N\nP 2 0 1 10 50 100 50 -100 N\nT 0 -100 100 40 0 0 0 + Normal 0 C C"),
    ("L", "L", "S -100 60 100 -60 0 1 10 N"),
    ("Crystal", "Y", "S -80 100 80 -100 0 1 10 N"),
    ("Fuse", "F", "S -100 60 100 -60 0 1 10 N"),
    ("LED", "D", "P 3 0 1 10 -80 100 -80 -100 80 0 F\nP 2 0 1 10 80 100 80 -100 N"),
    ("SW_Push", "SW", "P 2 0 1 10 -100 0 -30 0 N\nP 2 0 1 10 30 0 100 0 N\nP 2 0 1 10 -20 -40 20 -40 N"),
]:
    text, ep = two_pin_symbol(name, ref, drawing)
    lib_parts.append(text)
    symbols[name] = ep

for name, ref, drawing in [
    ("TestPoint", "TP", "C 0 -80 60 0 1 10 N"),
    ("MountingHole", "H", "C 0 -80 80 0 1 10 N"),
]:
    text, ep = one_pin_symbol(name, ref, drawing)
    lib_parts.append(text)
    symbols[name] = ep

lib = "EESchema-LIBRARY Version 2.4\n#encoding utf-8\n" + "\n".join(lib_parts) + "\n#\n#End Library\n"
(ROOT / f"{NAME}-cache.lib").write_text(lib)


components = []


def add(ref, symbol, value, footprint, x, y, nets, note=""):
    components.append({
        "ref": ref, "symbol": symbol, "value": value, "footprint": footprint,
        "x": x, "y": y, "nets": {str(k): v for k, v in nets.items()}, "note": note,
    })


# Raspberry Pi Pico and digital level translation.
add("A1", "RaspberryPi_Pico", "Raspberry Pi Pico", "Module:RaspberryPi_Pico_Common_THT", 2300, 3100, {
    1:"P_D0",2:"P_D1",3:"GND",4:"P_D2",5:"P_D3",6:"P_D4",7:"P_D5",8:"GND",
    9:"P_D6",10:"P_D7",11:"CTRL_MODE0_IN",12:"CTRL_MODE1_IN",13:"GND",
    14:"CTRL_CSW_IN",15:"CTRL_CSR_IN",16:"BUS_DIR",17:"BUS_OE_N",18:"GND",
    19:"CTRL_RESET_IN",20:"LED_GREEN",21:"LED_RED",22:"MON_CPUCLK",23:"GND",
    24:"MON_WAIT",25:"MON_HSYNC",26:"MON_INT",27:"MON_CSYNC",28:"GND",
    29:"TEST_BUTTON",31:"ADC_R",32:"ADC_G",33:"GND",34:"ADC_B",36:"+3V3",
    38:"GND",40:"VBUS_USB",
})
add("U1", "SN74LVC245A", "SN74LVC245AN", "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", 4700, 2300, {
    1:"BUS_DIR",2:"P_D0",3:"P_D1",4:"P_D2",5:"P_D3",6:"P_D4",7:"P_D5",8:"P_D6",9:"P_D7",10:"GND",
    11:"VDP_D7",12:"VDP_D6",13:"VDP_D5",14:"VDP_D4",15:"VDP_D3",16:"VDP_D2",17:"VDP_D1",18:"VDP_D0",19:"BUS_OE_N",20:"+3V3",
})
add("U2", "SN74AHCT244", "SN74AHCT244N", "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", 4700, 4700, {
    1:"GND",2:"CTRL_MODE0_IN",3:"NC_U2_3",4:"CTRL_MODE1_IN",5:"NC_U2_5",6:"CTRL_CSW_IN",7:"NC_U2_7",8:"CTRL_CSR_IN",9:"VDP_RESET_N",10:"GND",
    11:"CTRL_RESET_IN",12:"VDP_CSR_N",13:"GND",14:"VDP_CSW_N",15:"GND",16:"VDP_MODE1",17:"GND",18:"VDP_MODE0",19:"GND",20:"+5V",
})
add("U4", "SN74LVC244A", "SN74LVC244AN", "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", 4700, 7200, {
    1:"GND",2:"CPUCLK_5",3:"NC_U4_3",4:"HSYNC_5",5:"NC_U4_5",6:"CSYNC_5",7:"NC_U4_7",8:"WAIT_5",9:"MON_INT",10:"GND",
    11:"INT_5",12:"MON_WAIT",13:"GND",14:"MON_CSYNC",15:"GND",16:"MON_HSYNC",17:"GND",18:"MON_CPUCLK",19:"GND",20:"+3V3",
})

# Device under test.
vdp_nets = {
    1:"GND",4:"VRESET",5:"HSYNC_RAW",6:"CSYNC_RAW",8:"CPUCLK_RAW",9:"VDP_RESET_N",
    12:"CB7",13:"CB6",14:"CB5",15:"CB4",16:"CB3",17:"CB2",18:"CB1",19:"CB0",
    20:"GND",21:"VCCVDP",22:"GREEN_RAW",23:"RED_RAW",24:"BLUE_RAW",25:"INT_RAW",
    26:"WAIT_RAW",27:"HRESET",28:"VDP_MODE1",29:"VDP_MODE0",30:"VDP_CSW_N",31:"VDP_CSR_N",
    32:"VDP_D7",33:"VBB",34:"VDP_D6",35:"VDP_D5",36:"VDP_D4",37:"VDP_D3",38:"VDP_D2",39:"VDP_D1",40:"VDP_D0",
    41:"VD0",42:"VD1",43:"VD2",44:"VD3",45:"VD4",46:"VD5",47:"VD6",48:"VD7",
    49:"VA0",50:"VA1",51:"VA2",52:"VA3",53:"VA4",54:"VA5",55:"VA6",56:"VA7",
    57:"VWR_RAW",58:"VCCVDP",59:"CASX",60:"CAS1_RAW",61:"CAS0_RAW",62:"RAS_RAW",63:"XTAL1",64:"XTAL2",
}
add("U3", "V9958", "V9958 DUT", "V9958-Tester:SDIP-64_W19.05mm_P1.778mm_Socket", 8200, 4800, vdp_nets)

# 128 KiB VRAM, two 64 Ki x 8 banks built from four 64 Ki x 4 DRAMs.
def dram_map(bits, cas):
    return {
        1:"GND",2:f"VD{bits[0]}",3:f"VD{bits[1]}",4:"VWR",5:"RAS",6:"VA6",7:"VA5",8:"VA4",9:"VCCVDP",
        10:"VA7",11:"VA3",12:"VA2",13:"VA1",14:"VA0",15:f"VD{bits[2]}",16:cas,17:f"VD{bits[3]}",18:"GND",
    }

add("U5", "D41464", "41464 VRAM L0", "Package_DIP:DIP-18_W7.62mm_Socket_LongPads", 11700, 1800, dram_map((0,1,2,3), "CAS0"))
add("U6", "D41464", "41464 VRAM H0", "Package_DIP:DIP-18_W7.62mm_Socket_LongPads", 14100, 1800, dram_map((4,5,6,7), "CAS0"))
add("U7", "D41464", "41464 VRAM L1", "Package_DIP:DIP-18_W7.62mm_Socket_LongPads", 11700, 4200, dram_map((0,1,2,3), "CAS1"))
add("U8", "D41464", "41464 VRAM H1", "Package_DIP:DIP-18_W7.62mm_Socket_LongPads", 14100, 4200, dram_map((4,5,6,7), "CAS1"))

# Pull-ups and the VDP crystal network.
add("RN1", "RN_Bussed_10", "10k bussed", "Resistor_THT:R_Array_SIP10", 11400, 6800, {
    1:"+5V",2:"CB0",3:"CB1",4:"CB2",5:"CB3",6:"CB4",7:"CB5",8:"CB6",9:"CB7",10:"VRESET",
})
add("R1", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 13400, 6500, {1:"+5V",2:"HRESET"})
add("R2", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 13400, 6800, {1:"+5V",2:"CASX"})
add("R3", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 13400, 7100, {1:"+5V",2:"INT_RAW"})
add("Y1", "Crystal", "21.477270MHz", "Crystal:Crystal_HC49-U_Vertical", 7900, 8500, {1:"XTAL1",2:"XTAL2"})
add("R4", "R", "470k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 7900, 8800, {1:"XTAL1",2:"XTAL2"})
add("C1", "C", "30pF trimmer", "V9958-Tester:C_Trim_P5.00mm", 7300, 9100, {1:"XTAL1",2:"GND"})
add("C2", "C", "22pF", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 8500, 9100, {1:"XTAL2",2:"GND"})

# VRAM series damping resistors.
for ref, y, a, b in [
    ("R5",7800,"VWR_RAW","VWR"),("R6",8100,"CAS0_RAW","CAS0"),
    ("R7",8400,"CAS1_RAW","CAS1"),("R8",8700,"RAS_RAW","RAS"),
]:
    add(ref, "R", "100", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 10100, y, {1:a,2:b})

# Monitor-input series resistors.
for ref, y, a, b in [
    ("R9",7800,"CPUCLK_RAW","CPUCLK_5"),("R10",8100,"HSYNC_RAW","HSYNC_5"),
    ("R11",8400,"CSYNC_RAW","CSYNC_5"),("R12",8700,"WAIT_RAW","WAIT_5"),
    ("R13",9000,"INT_RAW","INT_5"),
]:
    add(ref, "R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 5200, y, {1:a,2:b})

# Safe power-up defaults on Pico-to-VDP controls.
for ref, y, a, b, value in [
    ("R14",8600,"CTRL_MODE0_IN","GND","10k"),("R15",8900,"CTRL_MODE1_IN","GND","10k"),
    ("R16",9200,"CTRL_CSW_IN","+3V3","10k"),("R17",9500,"CTRL_CSR_IN","+3V3","10k"),
    ("R18",9800,"CTRL_RESET_IN","GND","10k"),("R19",10100,"BUS_DIR","GND","10k"),
    ("R20",10400,"BUS_OE_N","+3V3","10k"),
]:
    add(ref, "R", value, "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 3000, y, {1:a,2:b})

# RGB loads and protected/filtered ADC dividers.
rgb_y = {"R": 7600, "G": 8400, "B": 9200}
rgb_raw = {"R":"RED_RAW", "G":"GREEN_RAW", "B":"BLUE_RAW"}
rgb_adc = {"R":"ADC_R", "G":"ADC_G", "B":"ADC_B"}
next_r = 21
next_c = 3
for ch in ("R","G","B"):
    y = rgb_y[ch]
    add(f"R{next_r}", "R", "470", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 12100, y, {1:rgb_raw[ch],2:"GND"}); next_r += 1
    add(f"R{next_r}", "R", "22k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 13000, y, {1:rgb_raw[ch],2:rgb_adc[ch]}); next_r += 1
    add(f"R{next_r}", "R", "22k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 13900, y, {1:rgb_adc[ch],2:"GND"}); next_r += 1
    add(f"C{next_c}", "C", "10n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 14800, y, {1:rgb_adc[ch],2:"GND"}); next_c += 1

# Omega-compatible DIN RGB output.  The CXA1645P is used only as a low-
# impedance, clamp-timed RGB buffer here; no subcarrier is required because
# composite colour is not generated.  DIN pin 4 carries 75-ohm-terminated
# composite sync, not composite video.  Pins 3 and 5 reproduce the Omega's
# cable-control voltages so the same RGB lead can be used.
add("U9", "CXA1645", "CXA1645P RGB buffer", "Package_DIP:DIP-24_W10.16mm_Socket_LongPads", 10300, 10400, {
    1:"GND",2:"CXA_R_IN",3:"CXA_G_IN",4:"CXA_B_IN",7:"GND",9:"CXA_YCLP",
    10:"CSYNC_RAW",12:"+5V",13:"CXA_IREF",14:"CXA_VREF",18:"CXA_FO",
    19:"+5V",21:"CXA_B_OUT",22:"CXA_G_OUT",23:"CXA_R_OUT",24:"GND",
})
add("J1", "DIN8_Omega", "OMEGA RGB DIN-8", "V9958-Tester:DIN8_Omega_THT", 14300, 10400, {
    1:"GND",3:"DIN_AV",4:"DIN_SYNC",5:"DIN_YS",6:"DIN_R",7:"DIN_G",8:"DIN_B",
})

for ref, y, source, target in [
    ("C16",10000,"RED_RAW","CXA_R_IN"),
    ("C17",10300,"GREEN_RAW","CXA_G_IN"),
    ("C18",10600,"BLUE_RAW","CXA_B_IN"),
]:
    add(ref, "C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 8200, y, {1:source,2:target})

add("C19", "C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 7500, 11200, {1:"CXA_YCLP",2:"GND"})
add("R33", "R", "47k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 8400, 11200, {1:"CXA_IREF",2:"GND"})
add("C20", "C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 9300, 11200, {1:"CXA_IREF",2:"GND"})
add("C21", "CP", "10uF", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 10200, 11200, {1:"CXA_VREF",2:"GND"})
add("R34", "R", "16k 1% PAL", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 11100, 11200, {1:"CXA_FO",2:"GND"})
add("C22", "C", "100n VCC1", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 12000, 11200, {1:"+5V",2:"GND"})
add("C23", "CP", "47uF VCC1", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 12900, 11200, {1:"+5V",2:"GND"})
add("C24", "C", "100n VCC2", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 13800, 11200, {1:"+5V",2:"GND"})
add("C25", "CP", "47uF VCC2", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 14700, 11200, {1:"+5V",2:"GND"})

for ref, y, source, mid, capref, target in [
    ("R35",9800,"CXA_R_OUT","DIN_R_AC","C26","DIN_R"),
    ("R36",10100,"CXA_G_OUT","DIN_G_AC","C27","DIN_G"),
    ("R37",10400,"CXA_B_OUT","DIN_B_AC","C28","DIN_B"),
]:
    add(ref, "R", "75", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 12000, y, {1:source,2:mid})
    add(capref, "CP", "220uF", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", 13200, y, {1:mid,2:target})

add("R38", "R", "1k sync/75R load", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 12000, 10700, {1:"CSYNC_RAW",2:"DIN_SYNC"})
add("R39", "R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 14600, 9800, {1:"+5V",2:"DIN_AV"})
add("R40", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 15400, 9800, {1:"DIN_AV",2:"GND"})
add("R41", "R", "120", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 14600, 10100, {1:"+5V",2:"DIN_YS"})
add("R42", "R", "180", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 15400, 10100, {1:"DIN_YS",2:"GND"})

# Indicators and test button.
add("R30", "R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 1500, 7200, {1:"LED_GREEN",2:"LED_GREEN_A"})
add("D1", "LED", "GREEN PASS", "LED_THT:LED_D5.0mm", 2400, 7200, {1:"GND",2:"LED_GREEN_A"})
add("R31", "R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 1500, 7600, {1:"LED_RED",2:"LED_RED_A"})
add("D2", "LED", "RED FAIL", "LED_THT:LED_D5.0mm", 2400, 7600, {1:"GND",2:"LED_RED_A"})
add("SW1", "SW_Push", "TEST", "Button_Switch_THT:SW_PUSH_6mm_H7.3mm", 1500, 8100, {1:"TEST_BUTTON",2:"GND"})
add("R32", "R", "10k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", 2400, 8100, {1:"TEST_BUTTON",2:"+3V3"})

# Power distribution, decoupling and VBB bypass.
add("F1", "Fuse", "Bourns MF-RHT100 PTC 1.0A", "Fuse:Fuse_Bourns_MF-RHT100", 1200, 10000, {1:"VBUS_USB",2:"+5V"})
add("L1", "L", "5.6uH", "Inductor_THT:L_Axial_L14.0mm_D4.5mm_P15.24mm_Horizontal_Fastron_LACC", 2700, 10000, {1:"+5V",2:"VCCVDP"})
add("C6", "CP", "100uF", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 4000, 10000, {1:"VCCVDP",2:"GND"})
add("C7", "C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 5000, 10000, {1:"VCCVDP",2:"GND"})
add("C8", "C", "100n VBB", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 6000, 10000, {1:"VBB",2:"GND"})

# One local 100 nF bypass per logic/VRAM supply point.
decouple = [
    ("C9","+3V3"),("C10","+5V"),("C11","+3V3"),
    ("C12","VCCVDP"),("C13","VCCVDP"),("C14","VCCVDP"),("C15","VCCVDP"),
]
for idx, (ref, net) in enumerate(decouple):
    add(ref, "C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", 7600 + idx*900, 9600, {1:net,2:"GND"})

# Test points.
for idx, (ref, label, net) in enumerate([
    ("TP1","5V","+5V"),("TP2","3V3","+3V3"),("TP3","GND","GND"),
    ("TP4","CPUCLK","CPUCLK_RAW"),("TP5","HSYNC","HSYNC_RAW"),("TP6","CSYNC","CSYNC_RAW"),
    ("TP7","RED","RED_RAW"),("TP8","GREEN","GREEN_RAW"),("TP9","BLUE","BLUE_RAW"),
]):
    add(ref, "TestPoint", label, "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", 5900 + (idx%3)*600, 9000 + (idx//3)*500, {1:net})

# Mounting holes are represented on the schematic for PCB parity.
for ref, x, y in [("H1",1200,10800),("H2",2200,10800),("H3",3200,10800),("H4",4200,10800)]:
    add(ref, "MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", x, y, {})


def comp_text(c, idx):
    x, y = c["x"], c["y"]
    stamp = f"6A{idx:06X}"
    return "\n".join([
        "$Comp",
        f'L {NAME}-cache:{c["symbol"]} {c["ref"]}',
        f"U 1 1 {stamp}",
        f"P {x} {y}",
        f'F 0 "{c["ref"]}" H {x} {y-150} 50  0000 C CNN',
        f'F 1 "{c["value"]}" H {x} {y+150} 50  0000 C CNN',
        f'F 2 "{c["footprint"]}" H {x} {y} 50  0001 C CNN',
        f'F 3 "" H {x} {y} 50  0001 C CNN',
        f"\t1    {x} {y}",
        "\t1    0    0    -1",
        "$EndComp",
    ])


def pin_abs(c, pnum):
    rx, ry = symbols[c["symbol"]][str(pnum)]
    return c["x"] + rx, c["y"] - ry


sch = [
    "EESchema Schematic File Version 4",
    f"LIBS:{NAME}-cache",
    "EELAYER 30 0",
    "EELAYER END",
    "$Descr A3 16535 11693",
    "encoding utf-8",
    "Sheet 1 1",
    'Title "V9958 Pico Functional Tester"',
    'Date "2026-11-06"',
    'Rev "0.3-prototype"',
    'Comp "Omega side project"',
    'Comment1 "Unbuilt prototype - verify socket and parts before fabrication"',
    'Comment2 "USB 5V supply must provide at least 1A"',
    'Comment3 "Never insert or remove DUT while powered"',
    'Comment4 "V9958 behavioral tester, not forensic authentication"',
    "$EndDescr",
    "Text Notes 900 700 0    100  ~ 20",
    "V9958 PICO FUNCTIONAL TESTER - PROTOTYPE REV 0.3",
    "Text Notes 900 900 0    60   ~ 12",
    "Checks V9958 ID, CPU interface, 128 KiB VRAM, sync/clock frequencies, interrupt and RGB response; buffered DIN RGB output.",
    "Text Notes 900 1100 0    60   ~ 12",
    "WARNING: power off before inserting/removing V9958 or VRAM. Use a current-limited 5V USB supply.",
]

for idx, c in enumerate(components, 1):
    sch.append(comp_text(c, idx))
    for pnum in symbols[c["symbol"]]:
        xy = pin_abs(c, pnum)
        net = c["nets"].get(str(pnum))
        if net is None or net.startswith("NC_"):
            sch.append(f"NoConn ~ {xy[0]} {xy[1]}")
            continue
        rx, _ = symbols[c["symbol"]][str(pnum)]
        if rx < 0:
            x2 = xy[0] - 200
            sch.append(f"Wire Wire Line\n\t{xy[0]} {xy[1]} {x2} {xy[1]}")
            sch.append(f"Text Label {x2} {xy[1]} 2    40   ~ 0\n{net}")
        elif rx > 0:
            x2 = xy[0] + 200
            sch.append(f"Wire Wire Line\n\t{xy[0]} {xy[1]} {x2} {xy[1]}")
            sch.append(f"Text Label {x2} {xy[1]} 0    40   ~ 0\n{net}")
        else:
            y2 = xy[1] + 200
            sch.append(f"Wire Wire Line\n\t{xy[0]} {xy[1]} {xy[0]} {y2}")
            sch.append(f"Text Label {xy[0]} {y2} 3    40   ~ 0\n{net}")

sch.append("$EndSCHEMATC")
(ROOT / f"{NAME}.sch").write_text("\n".join(sch) + "\n")

(ROOT / "sym-lib-table").write_text(
    '(sym_lib_table\n  (version 7)\n'
    f'  (lib (name "{NAME}-cache")(type "Legacy")(uri "${{KIPRJMOD}}/{NAME}-cache.lib")(options "")(descr "Generated legacy symbols"))\n'
    ')\n'
)

print(f"Generated {NAME}.sch and {NAME}-cache.lib with {len(components)} components")
