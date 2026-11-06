#!/usr/bin/env python3
"""Generate and finish the Revision B/B2 cores and RGB DIN daughterboard.

The schematics and placed boards are generated deterministically from the
reviewed connection tables below.  Run with KiCad's Python for ``board`` and
``finish`` because those modes use pcbnew.
"""

from __future__ import annotations

import copy
import csv
import json
import pathlib
import sys
import uuid
import xml.etree.ElementTree as ET

from sexpr import dump, node, nodes, parse


REPO = pathlib.Path(__file__).resolve().parents[1]


def comp(ref, symbol, value, footprint, nets):
    return {"ref": ref, "symbol": symbol, "value": value,
            "footprint": footprint,
            "nets": {str(pin): net for pin, net in nets.items()}}


V9958 = {
    1:"GND", 2:"~DHCLK", 3:"~DLCLK", 4:"~VRESET", 5:"~HSYNC",
    6:"~CSYNC", 7:"BLEO", 8:"CPUCLK/~VDS", 9:"~RESET", 10:"~YS",
    11:"CBDR", 12:"C7", 13:"C6", 14:"C5", 15:"C4", 16:"C3",
    17:"C2", 18:"C1", 19:"C0", 20:"GND_DAC", 21:"VDD_DAC",
    22:"G", 23:"R", 24:"B", 25:"~INT", 26:"~WAIT",
    27:"~HRESET", 28:"MODE1", 29:"MODE0", 30:"~CSW", 31:"~CSR",
    32:"CD7", 33:"VBB", 34:"CD6", 35:"CD5", 36:"CD4", 37:"CD3",
    38:"CD2", 39:"CD1", 40:"CD0", 41:"RD0", 42:"RD1", 43:"RD2",
    44:"RD3", 45:"RD4", 46:"RD5", 47:"RD6", 48:"RD7", 49:"AD0",
    50:"AD1", 51:"AD2", 52:"AD3", 53:"AD4", 54:"AD5", 55:"AD6",
    56:"AD7", 57:"R/~W", 58:"VDD", 59:"~CASX", 60:"~CAS1",
    61:"~CAS0", 62:"~RAS", 63:"XTAL1", 64:"XTAL2",
}
PICO = {
    1:"GP0", 2:"GP1", 3:"GND", 4:"GP2", 5:"GP3", 6:"GP4",
    7:"GP5", 8:"GND", 9:"GP6", 10:"GP7", 11:"GP8", 12:"GP9",
    13:"GND", 14:"GP10", 15:"GP11", 16:"GP12", 17:"GP13",
    18:"GND", 19:"GP14", 20:"GP15", 21:"GP16", 22:"GP17",
    23:"GND", 24:"GP18", 25:"GP19", 26:"GP20", 27:"GP21",
    28:"GND", 29:"GP22", 30:"RUN", 31:"GP26_ADC0", 32:"GP27_ADC1",
    33:"AGND", 34:"GP28_ADC2", 35:"ADC_VREF", 36:"3V3_OUT",
    37:"3V3_EN", 38:"GND", 39:"VSYS", 40:"VBUS",
}
DRAM = {1:"~OE",2:"DQ0",3:"DQ1",4:"~WE",5:"~RAS",6:"A6",7:"A5",
        8:"A4",9:"VCC",10:"A7",11:"A3",12:"A2",13:"A1",14:"A0",
        15:"DQ2",16:"~CAS",17:"DQ3",18:"GND"}
LVC245 = {1:"DIR",2:"A0",3:"A1",4:"A2",5:"A3",6:"A4",7:"A5",
          8:"A6",9:"A7",10:"GND",11:"B7",12:"B6",13:"B5",14:"B4",
          15:"B3",16:"B2",17:"B1",18:"B0",19:"~OE",20:"VCC"}
LVC244 = {1:"~1OE",2:"1A1",3:"2Y4",4:"1A2",5:"2Y3",6:"1A3",
          7:"2Y2",8:"1A4",9:"2Y1",10:"GND",11:"2A1",12:"1Y4",
          13:"2A2",14:"1Y3",15:"2A3",16:"1Y2",17:"2A4",
          18:"1Y1",19:"~2OE",20:"VCC"}
RN10 = {1:"COM", **{i:str(i) for i in range(2, 11)}}
CXA1645 = {1:"GND1",2:"RIN",3:"GIN",4:"BIN",5:"NC",6:"SCIN",
           7:"NPIN",8:"BFOUT",9:"YCLPC",10:"SYNCIN",11:"NC",12:"VCC1",
           13:"IREF",14:"VREF",15:"COUT",16:"YOUT",17:"YTRAP",18:"FO",
           19:"VCC2",20:"CVOUT",21:"BOUT",22:"GOUT",23:"ROUT",24:"GND2"}
DIN8 = {1:"GND",2:"AUDIO",3:"AV",4:"SYNC",5:"YS",6:"RED",7:"GREEN",8:"BLUE"}
IDC6 = {1:"GND",2:"+5V",3:"RED",4:"GREEN",5:"BLUE",6:"CSYNC"}
SRAM128K = {
    1:"NC", 2:"A16", 3:"A14", 4:"A12", 5:"A7", 6:"A6", 7:"A5",
    8:"A4", 9:"A3", 10:"A2", 11:"A1", 12:"A0", 13:"I/O0",
    14:"I/O1", 15:"I/O2", 16:"GND", 17:"I/O3", 18:"I/O4",
    19:"I/O5", 20:"I/O6", 21:"I/O7", 22:"~CE", 23:"A10",
    24:"~OE", 25:"A11", 26:"A9", 27:"A8", 28:"A13", 29:"~WE",
    30:"A15", 31:"CE2", 32:"VCC",
}
AHCT573 = {
    1:"~OE", 2:"D0", 3:"D1", 4:"D2", 5:"D3", 6:"D4", 7:"D5",
    8:"D6", 9:"D7", 10:"GND", 11:"LE", 12:"Q7", 13:"Q6",
    14:"Q5", 15:"Q4", 16:"Q3", 17:"Q2", 18:"Q1", 19:"Q0", 20:"VCC",
}
AHCT08 = {
    1:"1A", 2:"1B", 3:"1Y", 4:"2A", 5:"2B", 6:"2Y", 7:"GND",
    8:"3Y", 9:"3A", 10:"3B", 11:"4Y", 12:"4A", 13:"4B", 14:"VCC",
}


def dram_map(bits, cas):
    return {1:"GND",2:f"VD{bits[0]}",3:f"VD{bits[1]}",4:"VWR",5:"RAS",
            6:"VA6",7:"VA5",8:"VA4",9:"VCCVDP",10:"VA7",11:"VA3",
            12:"VA2",13:"VA1",14:"VA0",15:f"VD{bits[2]}",16:cas,
            17:f"VD{bits[3]}",18:"GND"}


def revb_components():
    c = []
    c.append(comp("A1", "RaspberryPi_Pico", "Raspberry Pi Pico",
                  "Module:RaspberryPi_Pico_Common_THT", {
        1:"P_D0",2:"P_D1",3:"GND",4:"P_D2",5:"P_D3",6:"P_D4",7:"P_D5",8:"GND",
        9:"P_D6",10:"P_D7",11:"P_MODE0",12:"P_MODE1",13:"GND",
        14:"P_CSW_N",15:"P_CSR_N",16:"BUS_DIR",17:"BUS_OE_N",18:"GND",
        19:"P_RESET_N",20:"LED_GREEN",21:"LED_RED",22:"MON_CPUCLK",23:"GND",
        24:"MON_WAIT",25:"MON_HSYNC",26:"MON_INT",27:"MON_CSYNC",28:"GND",
        31:"ADC_R",32:"ADC_G",33:"GND",34:"ADC_B",36:"+3V3",38:"GND",40:"VBUS_USB",
    }))
    c.append(comp("U1", "SN74LVC245A", "SN74LVC245AN",
                  "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", {
        1:"BUS_DIR",2:"P_D0",3:"P_D1",4:"P_D2",5:"P_D3",6:"P_D4",7:"P_D5",8:"P_D6",9:"P_D7",10:"GND",
        11:"VDP_D7",12:"VDP_D6",13:"VDP_D5",14:"VDP_D4",15:"VDP_D3",16:"VDP_D2",17:"VDP_D1",18:"VDP_D0",19:"BUS_OE_N",20:"+3V3",
    }))
    c.append(comp("U4", "SN74LVC244A", "SN74LVC244AN",
                  "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", {
        1:"GND",2:"CPUCLK_5",4:"HSYNC_5",6:"CSYNC_5",8:"WAIT_5",9:"MON_INT",10:"GND",
        11:"INT_5",12:"MON_WAIT",13:"GND",14:"MON_CSYNC",15:"GND",16:"MON_HSYNC",
        17:"GND",18:"MON_CPUCLK",19:"GND",20:"+3V3",
    }))
    c.append(comp("U3", "V9958", "V9958 DUT",
                  "V9958-Tester:SDIP-64_W19.05mm_P1.778mm_Socket", {
        1:"GND",4:"VRESET",5:"HSYNC_RAW",6:"CSYNC_RAW",8:"CPUCLK_RAW",9:"VDP_RESET_N",
        12:"CB7",13:"CB6",14:"CB5",15:"CB4",16:"CB3",17:"CB2",18:"CB1",19:"CB0",
        20:"GND",21:"VCCVDP",22:"GREEN_RAW",23:"RED_RAW",24:"BLUE_RAW",25:"INT_RAW",26:"WAIT_RAW",
        27:"HRESET",28:"VDP_MODE1",29:"VDP_MODE0",30:"VDP_CSW_N",31:"VDP_CSR_N",
        32:"VDP_D7",33:"VBB",34:"VDP_D6",35:"VDP_D5",36:"VDP_D4",37:"VDP_D3",38:"VDP_D2",39:"VDP_D1",40:"VDP_D0",
        41:"VD0",42:"VD1",43:"VD2",44:"VD3",45:"VD4",46:"VD5",47:"VD6",48:"VD7",
        49:"VA0",50:"VA1",51:"VA2",52:"VA3",53:"VA4",54:"VA5",55:"VA6",56:"VA7",
        57:"VWR_RAW",58:"VCCVDP",60:"CAS1_RAW",61:"CAS0_RAW",62:"RAS_RAW",63:"XTAL1",64:"XTAL2",
    }))
    for ref, value, bits, cas in [
        ("U5","41464 VRAM L0",(0,1,2,3),"CAS0"),
        ("U6","41464 VRAM H0",(4,5,6,7),"CAS0"),
        ("U7","41464 VRAM L1",(0,1,2,3),"CAS1"),
        ("U8","41464 VRAM H1",(4,5,6,7),"CAS1")]:
        c.append(comp(ref, "D41464", value,
                      "Package_DIP:DIP-18_W7.62mm_Socket_LongPads", dram_map(bits, cas)))
    c.append(comp("RN1", "RN_Bussed_10", "10k bussed",
                  "Resistor_THT:R_Array_SIP10", {1:"VCCVDP",2:"CB0",3:"CB1",4:"CB2",5:"CB3",6:"CB4",7:"CB5",8:"CB6",9:"CB7",10:"VRESET"}))

    axial = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
    disc = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
    def r(ref, value, a, b): c.append(comp(ref,"R",value,axial,{1:a,2:b}))
    def cap(ref, value, a, b, footprint=disc): c.append(comp(ref,"C",value,footprint,{1:a,2:b}))
    r("R1","10k","VCCVDP","HRESET")
    r("R2","470k","XTAL1","XTAL2")
    c.append(comp("Y1","Crystal","21.477270MHz","Crystal:Crystal_HC49-U_Vertical",{1:"XTAL1",2:"XTAL2"}))
    cap("C1","30pF trimmer","XTAL1","GND","V9958-Tester:C_Trim_P5.00mm")
    cap("C2","22pF","XTAL2","GND")
    for ref, src, dst in [("R3","P_MODE0","VDP_MODE0"),("R4","P_MODE1","VDP_MODE1"),
                           ("R5","P_CSW_N","VDP_CSW_N"),("R6","P_CSR_N","VDP_CSR_N"),
                           ("R7","P_RESET_N","VDP_RESET_N")]: r(ref,"330",src,dst)
    for ref, net, rail in [("R8","VDP_MODE0","GND"),("R9","VDP_MODE1","GND"),
                           ("R10","VDP_CSW_N","+3V3"),("R11","VDP_CSR_N","+3V3"),
                           ("R12","VDP_RESET_N","GND"),("R13","BUS_DIR","GND"),
                           ("R14","BUS_OE_N","+3V3")]: r(ref,"10k",net,rail)
    for ref, raw, buffered in [("R15","CPUCLK_RAW","CPUCLK_5"),("R16","HSYNC_RAW","HSYNC_5"),
                               ("R17","CSYNC_RAW","CSYNC_5"),("R18","WAIT_RAW","WAIT_5"),
                               ("R19","INT_RAW","INT_5")]: r(ref,"1k",raw,buffered)
    r("R20","10k","+3V3","INT_RAW")
    for ref, raw, clean in [("R21","VWR_RAW","VWR"),("R22","CAS0_RAW","CAS0"),
                            ("R23","CAS1_RAW","CAS1"),("R24","RAS_RAW","RAS")]: r(ref,"100",raw,clean)
    for index, (raw, adc) in enumerate([("RED_RAW","ADC_R"),("GREEN_RAW","ADC_G"),("BLUE_RAW","ADC_B")]):
        base = 25 + index * 3
        r(f"R{base}","470",raw,"GND")
        r(f"R{base+1}","22k",raw,adc)
        r(f"R{base+2}","22k",adc,"GND")
        cap(f"C{3+index}","10n",adc,"GND")
    r("R34","1k","LED_GREEN","LED_GREEN_A")
    r("R35","1k","LED_RED","LED_RED_A")
    c.append(comp("D1","LED","GREEN PASS","LED_THT:LED_D5.0mm",{1:"GND",2:"LED_GREEN_A"}))
    c.append(comp("D2","LED","RED FAIL","LED_THT:LED_D5.0mm",{1:"GND",2:"LED_RED_A"}))
    c.append(comp("F1","Fuse","Bourns MF-RHT100 PTC 1.0A","Fuse:Fuse_Bourns_MF-RHT100",{1:"VBUS_USB",2:"+5V"}))
    c.append(comp("L1","L","5.6uH","Inductor_THT:L_Axial_L14.0mm_D4.5mm_P15.24mm_Horizontal_Fastron_LACC",{1:"+5V",2:"VCCVDP"}))
    c.append(comp("C6","CP","100uF","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",{1:"VCCVDP",2:"GND"}))
    cap("C7","100n VDP","VCCVDP","GND")
    cap("C8","100n DAC","VCCVDP","GND")
    cap("C9","100n VBB","VBB","GND")
    cap("C10","100n U1","+3V3","GND")
    cap("C11","100n U4","+3V3","GND")
    for n in range(12,16): cap(f"C{n}","100n VRAM","VCCVDP","GND")
    cap("C16","100n VIDEO","+5V","GND")
    c.append(comp("J1","IDC_2x3","VIDEO DAUGHTERBOARD",
                  "Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical",
                  {1:"GND",2:"+5V",3:"RED_RAW",4:"GREEN_RAW",5:"BLUE_RAW",6:"CSYNC_RAW"}))
    for ref, value, net in [("TP1","5V","+5V"),("TP2","GND","GND"),
                            ("TP3","CPUCLK","CPUCLK_RAW"),("TP4","CSYNC","CSYNC_RAW"),
                            ("TP5","RED","RED_RAW"),("TP6","GREEN","GREEN_RAW"),("TP7","BLUE","BLUE_RAW")]:
        c.append(comp(ref,"TestPoint",value,"TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",{1:net}))
    for ref in ("H1","H2","H3","H4"):
        c.append(comp(ref,"MountingHole","M3","MountingHole:MountingHole_3.2mm_M3",{}))
    return c


def revb2_components():
    """Revision B2: replace four 41464s with one asynchronous SRAM adapter."""
    removed = {"U5", "U6", "U7", "U8", "R21", "R22", "R23", "R24", "C12", "C13", "C14", "C15"}
    c = [item for item in revb_components() if item["ref"] not in removed]

    c.append(comp("U5", "AS6C1008", "AS6C1008-55PCN 128Kx8 SRAM",
                  "Package_DIP:DIP-32_W15.24mm_Socket_LongPads", {
        2:"SRAM_CAS0_N", 3:"SRAM_A14", 4:"SRAM_A12", 5:"VA7", 6:"VA6",
        7:"VA5", 8:"VA4", 9:"VA3", 10:"VA2", 11:"VA1", 12:"VA0",
        13:"VD0", 14:"VD1", 15:"VD2", 16:"GND", 17:"VD3", 18:"VD4",
        19:"VD5", 20:"VD6", 21:"VD7", 22:"GND", 23:"SRAM_A10",
        24:"SRAM_OE_N", 25:"SRAM_A11", 26:"SRAM_A9", 27:"SRAM_A8",
        28:"SRAM_A13", 29:"SRAM_WE_N", 30:"SRAM_A15", 31:"VCCVDP", 32:"VCCVDP",
    }))
    c.append(comp("U6", "SN74AHCT573", "SN74AHCT573N row-address latch",
                  "Package_DIP:DIP-20_W7.62mm_Socket_LongPads", {
        1:"GND", 2:"VA0", 3:"VA1", 4:"VA2", 5:"VA3", 6:"VA4", 7:"VA5",
        8:"VA6", 9:"VA7", 10:"GND", 11:"SRAM_RAS_N", 12:"SRAM_A15",
        13:"SRAM_A14", 14:"SRAM_A13", 15:"SRAM_A12", 16:"SRAM_A11",
        17:"SRAM_A10", 18:"SRAM_A9", 19:"SRAM_A8", 20:"VCCVDP",
    }))
    c.append(comp("U7", "SN74AHCT08", "SN74AHCT08N CAS-to-OE gate",
                  "Package_DIP:DIP-14_W7.62mm_Socket_LongPads", {
        1:"SRAM_CAS0_N", 2:"SRAM_CAS1_N", 3:"SRAM_OE_N",
        4:"GND", 5:"GND", 7:"GND", 9:"GND", 10:"GND",
        12:"GND", 13:"GND", 14:"VCCVDP",
    }))

    axial = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
    disc = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
    for ref, raw, clean in [
        ("R21", "VWR_RAW", "SRAM_WE_N"),
        ("R22", "CAS0_RAW", "SRAM_CAS0_N"),
        ("R23", "CAS1_RAW", "SRAM_CAS1_N"),
        ("R24", "RAS_RAW", "SRAM_RAS_N"),
    ]:
        c.append(comp(ref, "R", "47", axial, {1:raw, 2:clean}))
    for ref, value in [
        ("C12", "100n SRAM"), ("C13", "100n U6"), ("C14", "100n U7"),
    ]:
        c.append(comp(ref, "C", value, disc, {1:"VCCVDP", 2:"GND"}))
    for ref, value, net in [
        ("TP8", "RAS", "SRAM_RAS_N"), ("TP9", "CAS0", "SRAM_CAS0_N"),
        ("TP10", "CAS1", "SRAM_CAS1_N"), ("TP11", "SRAM OE", "SRAM_OE_N"),
        ("TP12", "SRAM WE", "SRAM_WE_N"),
    ]:
        c.append(comp(ref, "TestPoint", value,
                      "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm", {1:net}))
    return c


def daughter_components():
    c = []
    c.append(comp("J1","IDC_2x3","FROM REV B",
                  "Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical",
                  {1:"GND",2:"+5V",3:"RED_IN",4:"GREEN_IN",5:"BLUE_IN",6:"CSYNC_IN"}))
    c.append(comp("U1","CXA1645","CXA1645P RGB buffer",
                  "Package_DIP:DIP-24_W10.16mm_Socket_LongPads", {
        1:"GND",2:"CXA_R_IN",3:"CXA_G_IN",4:"CXA_B_IN",7:"GND",9:"CXA_YCLP",
        10:"CSYNC_IN",12:"+5V",13:"CXA_IREF",14:"CXA_VREF",18:"CXA_FO",
        19:"+5V",21:"CXA_B_OUT",22:"CXA_G_OUT",23:"CXA_R_OUT",24:"GND",
    }))
    c.append(comp("J2","DIN8_Omega","OMEGA RGB DIN-8",
                  "V9958-Video-Daughterboard:DIN8_Omega_THT", {
        1:"GND",3:"DIN_AV",4:"DIN_SYNC",5:"DIN_YS",6:"DIN_R",7:"DIN_G",8:"DIN_B"}))
    axial = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
    disc = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
    def r(ref,value,a,b): c.append(comp(ref,"R",value,axial,{1:a,2:b}))
    def cap(ref,value,a,b,footprint=disc,symbol="C"): c.append(comp(ref,symbol,value,footprint,{1:a,2:b}))
    cap("C1","100n","RED_IN","CXA_R_IN")
    cap("C2","100n","GREEN_IN","CXA_G_IN")
    cap("C3","100n","BLUE_IN","CXA_B_IN")
    cap("C4","100n YCLP","CXA_YCLP","GND")
    r("R1","47k","CXA_IREF","GND")
    cap("C5","100n IREF","CXA_IREF","GND")
    cap("C6","10uF","CXA_VREF","GND","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm","CP")
    r("R2","16k 1% PAL","CXA_FO","GND")
    cap("C7","100n VCC1","+5V","GND")
    cap("C8","47uF VCC1","+5V","GND","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm","CP")
    cap("C9","100n VCC2","+5V","GND")
    cap("C10","47uF VCC2","+5V","GND","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm","CP")
    for ref, source, middle, cref, target in [
        ("R3","CXA_R_OUT","DIN_R_AC","C11","DIN_R"),
        ("R4","CXA_G_OUT","DIN_G_AC","C12","DIN_G"),
        ("R5","CXA_B_OUT","DIN_B_AC","C13","DIN_B")]:
        r(ref,"75",source,middle)
        cap(cref,"220uF",middle,target,"Capacitor_THT:CP_Radial_D8.0mm_P3.50mm","CP")
    r("R6","1k sync/75R load","CSYNC_IN","DIN_SYNC")
    r("R7","1k","+5V","DIN_AV"); r("R8","10k","DIN_AV","GND")
    r("R9","120","+5V","DIN_YS"); r("R10","180","DIN_YS","GND")
    for ref, value, net in [("TP1","5V","+5V"),("TP2","GND","GND"),
                            ("TP3","SYNC","CSYNC_IN"),("TP4","RED","DIN_R"),
                            ("TP5","GREEN","DIN_G"),("TP6","BLUE","DIN_B")]:
        c.append(comp(ref,"TestPoint",value,"TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",{1:net}))
    for ref in ("H1","H2","H3","H4"):
        c.append(comp(ref,"MountingHole","M3","MountingHole:MountingHole_3.2mm_M3",{}))
    return c


PROJECTS = {
    "revb": {
        "name":"V9958-Tester-RevB", "directory":REPO/"revision-b",
        "title":"V9958 Pico Tester Revision B", "rev":"B0 PROTOTYPE",
        "company":"(c) salvogendut 2026", "components":revb_components(),
        "size":(170,118),
        "positions": {
            "A1":(166,84,270), "U1":(141,18,0), "U4":(141,48,0), "U3":(68,57,0),
            "U5":(24,15,90), "U6":(48,15,90), "U7":(72,15,90), "U8":(96,15,90),
            "RN1":(9,32,90), "Y1":(38,40,0), "C1":(31,46,0), "C2":(51,40,0), "R1":(14,66,90), "R2":(38,35,0),
            "R3":(108,57,90), "R4":(114.5,57,90), "R5":(121,57,90), "R6":(127.5,57,90), "R7":(134,57,90),
            "R8":(108,69,90), "R9":(114.5,69,90), "R10":(121,69,90), "R11":(127.5,69,90), "R12":(134,69,90),
            "R13":(102,81,90), "R14":(109,81,90),
            "R15":(102,43,90), "R16":(109,43,90), "R17":(116,43,90), "R18":(123,43,90), "R19":(130,43,90), "R20":(102,31,90),
            "R21":(25,36,0), "R22":(49,36,0), "R23":(73,36,0), "R24":(89,36,0),
            "R25":(20,77,0), "R26":(32,77,0), "R27":(44,77,0), "C3":(54,77,0),
            "R28":(20,86,0), "R29":(32,86,0), "R30":(44,86,0), "C4":(54,86,0),
            "R31":(20,95,0), "R32":(32,95,0), "R33":(44,95,0), "C5":(54,95,0),
            "R34":(65,87,0), "D1":(76,87,0), "R35":(65,96,0), "D2":(76,96,0),
            "F1":(132,110,0), "L1":(95,110,0), "C6":(86,110,0), "C7":(80,72,0), "C8":(90,72,0), "C9":(89,41,0),
            "C10":(132,26,0), "C11":(141,74,0), "C12":(20,27,0), "C13":(44,27,0), "C14":(68,27,0), "C15":(92,27,0), "C16":(18,82,0),
            "J1":(8,91,90),
            "TP1":(162,12,0), "TP2":(162,18,0), "TP3":(162,27,0), "TP4":(162,33,0),
            "TP5":(162,42,0), "TP6":(162,48,0), "TP7":(162,54,0),
            "H1":(4,4,0), "H2":(166,4,0), "H3":(4,114,0), "H4":(78,114,0),
        },
        "silk":[
            ("V9958 TESTER REVISION B",85,5,1.5,0),("MINIMAL CORE / PROTOTYPE",145,8,0.9,0),
            ("POWER OFF BEFORE CHANGING DUT",68,57,0.8,31),("VIDEO OUT",9,79,0.8,0),
            ("1 GND  2 +5V  3 R  4 G  5 B  6 CSYNC",50,115,0.8,0),
            ("PASS",76,91,0.8,0),("FAIL",76,100,0.8,0),("USB POWER / SERIAL",166,72,0.8,90),
            ("(c) salvogendut 2026",118,115,0.9,0),
        ],
        "plus":[(81.5,87),(81.5,96),(82,110)],
        "ref_positions":{
            "U3":(68,69), "U5":(35,18.8), "U6":(59,18.8), "U7":(83,18.8), "U8":(107,18.8),
            "U1":(145,30), "U4":(145,60), "A1":(151,98), "C11":(145,78),
            "C16":(18,79), "R28":(20,89), "Y1":(40,44), "C2":(51,36),
        },
        "hide_refs":["H1","H2","H3","H4"],
        "full_zone_pads":[("U8","18"),("C9","2"),("U6","1"),("U6","18"),("A1","28"),("C2","2"),("U3","20"),("U7","1"),("U7","18")],
        "power_nets":["/+5V","/+3V3","/VCCVDP","/VBUS_USB","/GND"],
    },
    "revb2": {
        "name":"V9958-Tester-RevB2-SRAM", "directory":REPO/"revision-b2-sram",
        "title":"V9958 Pico Tester Revision B2 SRAM", "rev":"B2 PROTOTYPE",
        "company":"(c) salvogendut 2026", "components":revb2_components(),
        "size":(160,110),
        "positions": {
            "A1":(156,76,270), "U1":(131,14,0), "U4":(131,42,0), "U3":(63,55,0),
            "U5":(20,18,90), "U6":(68,14,90), "U7":(100,14,90),
            "RN1":(8,31,90), "Y1":(35,39,0), "C1":(24.5,45,0), "C2":(48,39,0), "R1":(13,64,90), "R2":(35,34,0),
            "R3":(99,55,90), "R4":(105,55,90), "R5":(111,55,90), "R6":(117,55,90), "R7":(123,55,90),
            "R8":(99,67,90), "R9":(105,67,90), "R10":(111,67,90), "R11":(117,67,90), "R12":(123,67,90),
            "R13":(96,79,90), "R14":(103,79,90),
            "R15":(96,41,90), "R16":(102,41,90), "R17":(108,41,90), "R18":(114,41,90), "R19":(120,41,90), "R20":(96,29,90),
            "R21":(20,34,0), "R22":(46,34,0), "R23":(68,34,0), "R24":(84,34,0),
            "R25":(20,75,0), "R26":(32,75,0), "R27":(44,75,0), "C3":(54,75,0),
            "R28":(20,84,0), "R29":(32,84,0), "R30":(44,84,0), "C4":(54,84,0),
            "R31":(20,93,0), "R32":(32,93,0), "R33":(44,93,0), "C5":(54,93,0),
            "R34":(62,84,0), "D1":(73,84,0), "R35":(62,93,0), "D2":(73,93,0),
            "F1":(122,102,0), "L1":(87,102,0), "C6":(78,102,0), "C7":(77,70,0), "C8":(87,70,0), "C9":(86,39,0),
            "C10":(121,23,0), "C11":(131,68,0), "C12":(26,28,0), "C13":(74,27,0), "C14":(105,27,0), "C16":(16,80,0),
            "J1":(8,89,90),
            "TP1":(152,10,0), "TP2":(152,16,0), "TP3":(152,24,0), "TP4":(152,30,0),
            "TP5":(85,78,0), "TP6":(85,86,0), "TP7":(85,94,0),
            "TP8":(5,42,0), "TP9":(5,50,0), "TP10":(5,58,0), "TP11":(5,66,0), "TP12":(5,74,0),
            "H1":(4,4,0), "H2":(156,4,0), "H3":(4,106,0), "H4":(56,106,0),
        },
        "silk":[
            ("V9958 TESTER REVISION B2 / SRAM",63,52,1.2,0),("EXPERIMENTAL PROTOTYPE",130,8,0.85,0),
            ("POWER OFF BEFORE CHANGING DUT",63,61,0.8,0),("VIDEO OUT",8,77,0.8,0),
            ("J1: 1 GND  2 +5V  3 R",30,104,0.8,0),("4 G  5 B  6 CSYNC",30,107,0.8,0),
            ("PASS",73,88,0.8,0),("FAIL",73,97,0.8,0),("USB POWER / SERIAL",156,59,0.8,90),
            ("(c) salvogendut 2026",128,107,0.85,0),
        ],
        "plus":[(78.5,84),(78.5,93),(74,102)],
        "ref_positions":{
            "U3":(63,67), "U5":(39,23.8), "U6":(79,18.8), "U7":(108,18.8),
            "U1":(135,26), "U4":(135,54), "A1":(142,91), "C11":(135,72),
            "C16":(16,77), "R28":(20,87), "Y1":(37,43), "C2":(48,30),
        },
        "hide_refs":["H1","H2","H3","H4"],
        "full_zone_pads":[("C9","2"),("U5","16"),("U6","10"),("U7","7"),("A1","23"),("A1","28"),("A1","33"),("C2","2"),("U3","20"),("R12","2"),("U4","19"),("U1","10"),("D1","1")],
        "power_nets":["/+5V","/+3V3","/VCCVDP","/VBUS_USB"],
        "ground_plane_only":True,
    },
    "daughter": {
        "name":"V9958-Video-Daughterboard", "directory":REPO/"video-daughterboard",
        "title":"V9958 RGB DIN Daughterboard", "rev":"B0 PROTOTYPE",
        "company":"(c) salvogendut 2026", "components":daughter_components(),
        "size":(120,80),
        "positions": {
            "J1":(8,40,90), "U1":(52,31,0), "J2":(108,23,180),
            "C1":(22,19,90), "C2":(27,19,90), "C3":(32,19,90), "C4":(34,32,0),
            "R1":(35,43,0), "C5":(35,49,0), "C6":(40,58,0), "R2":(67,58,0),
            "C7":(32,70,0), "C8":(44,70,0), "C9":(58,70,0), "C10":(70,70,0),
            "R3":(72,19,0), "C11":(84,19,0), "R4":(72,30,0), "C12":(84,30,0),
            "R5":(72,41,0), "C13":(84,41,0), "R6":(67,50,0),
            "R7":(82,62,90), "R8":(90,62,90), "R9":(98,62,90), "R10":(106,62,90),
            "TP1":(8,58,0), "TP2":(8,65,0), "TP3":(17,58,0), "TP4":(17,65,0), "TP5":(26,65,0), "TP6":(26,72,0),
            "H1":(4,4,0), "H2":(90,4,0), "H3":(4,76,0), "H4":(116,76,0),
        },
        "silk":[
            ("V9958 RGB DIN DAUGHTERBOARD",60,5,1.25,0),("REV B0 PROTOTYPE",60,8,0.8,0),
            ("FROM REV B",9,29,0.8,0),("OMEGA RGB DIN",106,48,0.85,0),
            ("IDC: 1 GND  2 +5V  3 R  4 G  5 B  6 CSYNC",60,77,0.8,0),
            ("(c) salvogendut 2026",60,74,0.85,0),
        ],
        "plus":[(37,58),(40,70),(66,70),(78.5,15),(78.5,26),(78.5,37)],
        "ref_positions":{},
        "hide_refs":["H1","H2","H3","H4"],
        "full_zone_pads":[],
        "power_nets":["/+5V","/GND"],
    },
}


SYMBOL_PINS = {
    "V9958":V9958, "RaspberryPi_Pico":PICO, "D41464":DRAM,
    "SN74LVC245A":LVC245, "SN74LVC244A":LVC244, "RN_Bussed_10":RN10,
    "CXA1645":CXA1645, "DIN8_Omega":DIN8, "IDC_2x3":IDC6,
    "AS6C1008":SRAM128K, "SN74AHCT573":AHCT573, "SN74AHCT08":AHCT08,
}


def uid(name, key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{name}/{key}"))


def q(value):
    return json.dumps(str(value))


def effects(size=1.0, extra=""):
    return f'(effects (font (size {size} {size})) {extra})'


def symbol_library(name):
    definitions, locations = {}, {}
    for sym, pin_names in SYMBOL_PINS.items():
        count = len(pin_names); left_count = count // 2
        left = list(range(1, left_count + 1)); right = list(range(left_count + 1, count + 1))
        half_width = 15.24 if sym in ("V9958","RaspberryPi_Pico") else (11.43 if sym == "CXA1645" else 10.16)
        pitch = 2.54; half_height = (max(len(left),len(right))-1)*pitch/2 + 2.54
        body = f'(symbol {q(sym+"_0_1")} (rectangle (start {-half_width} {half_height}) (end {half_width} {-half_height}) (stroke (width 0.254) (type default)) (fill (type background))))'
        pins=[]; loc={}
        for side, nums in (("L",left),("R",right)):
            top=(len(nums)-1)*pitch/2
            for index,num in enumerate(nums):
                y=round(top-index*pitch,4); x=-(half_width+5.08) if side=="L" else half_width+5.08; angle=0 if side=="L" else 180
                pins.append(f'(pin passive line (at {x} {y} {angle}) (length 5.08) (name {q(pin_names[num])} {effects(0.9)}) (number {q(num)} {effects(0.9)}))')
                loc[str(num)]=(x,y,angle)
        definitions[sym]=parse(f'(symbol {q(sym)} (pin_names (offset 0.8)) (exclude_from_sim no) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {half_height+5.08} 0) {effects(1.27)}) (property "Value" {q(sym)} (at 0 {half_height+2.54} 0) {effects(1.27)}) {body} (symbol {q(sym+"_1_1")} {"".join(pins)}))')
        locations[sym]=loc
    for sym, ref in (("R","R"),("C","C"),("CP","C"),("L","L"),("Crystal","Y"),("Fuse","F"),("LED","D")):
        definitions[sym]=parse(f'(symbol {q(sym)} (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes) (property "Reference" {q(ref)} (at 0 3.81 0) {effects(1.0)}) (property "Value" {q(sym)} (at 0 -3.81 0) {effects(1.0)}) (symbol {q(sym+"_0_1")} (rectangle (start -2.54 1.27) (end 2.54 -1.27) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol {q(sym+"_1_1")} (pin passive line (at -7.62 0 0) (length 5.08) (name "1" {effects(0.8)}) (number "1" {effects(0.8)})) (pin passive line (at 7.62 0 180) (length 5.08) (name "2" {effects(0.8)}) (number "2" {effects(0.8)}))))')
        locations[sym]={"1":(-7.62,0,0),"2":(7.62,0,180)}
    definitions["TestPoint"]=parse(f'(symbol "TestPoint" (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) (in_bom no) (on_board yes) (property "Reference" "TP" (at 0 3.81 0) {effects(1.0)}) (property "Value" "TestPoint" (at 0 -3.81 0) {effects(1.0)}) (symbol "TestPoint_0_1" (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))) (symbol "TestPoint_1_1" (pin passive line (at 0 -7.62 90) (length 5.08) (name "1" {effects(0.8)}) (number "1" {effects(0.8)}))))')
    locations["TestPoint"]={"1":(0,-7.62,90)}
    definitions["MountingHole"]=parse(f'(symbol "MountingHole" (pin_names (offset 0.5) (hide yes)) (exclude_from_sim no) (in_bom no) (on_board yes) (property "Reference" "H" (at 0 3.81 0) {effects(1.0)}) (property "Value" "MountingHole" (at 0 -3.81 0) {effects(1.0)}) (symbol "MountingHole_0_1" (circle (center 0 0) (radius 2.54) (stroke (width 0.254) (type default)) (fill (type none)))))')
    locations["MountingHole"]={}
    return definitions, locations


def generate_schematic(spec):
    name=spec["name"]; directory=spec["directory"]; directory.mkdir(parents=True,exist_ok=True)
    (directory/"docs").mkdir(exist_ok=True); (directory/"fabrication").mkdir(exist_ok=True)
    root_uuid=uid(name,"schematic/root"); definitions, locations=symbol_library(name)
    body=[]; normal_index=0
    has_large=any(item["symbol"] in ("RaspberryPi_Pico","V9958") for item in spec["components"])
    for item in spec["components"]:
        ref=item["ref"]; sym=item["symbol"]
        if sym == "RaspberryPi_Pico": x,y=63.5,69.85
        elif sym == "V9958": x,y=143.51,69.85
        else:
            x=25.4+(normal_index%12)*45.72
            y=(144.78 if has_large else 59.69)+(normal_index//12)*40.64
            normal_index+=1
        max_y=max((abs(float(v[1])) for v in locations[sym].values()),default=0)
        in_bom="no" if ref.startswith(("H","TP")) else "yes"
        props="".join([
            f'(property "Reference" {q(ref)} (at {x:.4f} {y-max_y-5.08:.4f} 0) {effects(1.0)})',
            f'(property "Value" {q(item["value"])} (at {x:.4f} {y-max_y-2.54:.4f} 0) {effects(1.0)})',
            f'(property "Footprint" {q(item["footprint"])} (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})',
            f'(property "Datasheet" "" (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})',
            f'(property "Description" "" (at {x:.4f} {y:.4f} 0) (hide yes) {effects(1.0)})'])
        body.append(f'(symbol (lib_id {q(name+":"+sym)}) (at {x:.4f} {y:.4f} 0) (unit 1) (in_bom {in_bom}) (on_board yes) (dnp no) (uuid {uid(name,ref)}) {props} (instances (project {q(name)} (path {q("/"+root_uuid)} (reference {q(ref)}) (unit 1)))))')
        for pin,(pxr,pyr,angle) in locations[sym].items():
            px=x+pxr; py=y-pyr; net=item["nets"].get(pin)
            if net is None:
                body.append(f'(no_connect (at {px:.4f} {py:.4f}) (uuid {uid(name,ref+"/nc/"+pin)}))'); continue
            dx,dy={0:(-1.27,0),180:(1.27,0),90:(0,1.27),270:(0,-1.27)}[angle]; ex=px+dx; ey=py+dy
            body.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {ex:.4f} {ey:.4f})) (stroke (width 0) (type default)) (uuid {uid(name,ref+"/wire/"+pin)}))')
            justify="right" if dx<0 else "left"
            body.append(f'(label {q(net)} (at {ex:.4f} {ey:.4f} 0) {effects(0.9,f"(justify {justify} bottom)")} (uuid {uid(name,ref+"/label/"+pin)}))')
    notes=[spec["title"]+" - "+spec["rev"],"All carrier-board parts are through-hole.","Power off before inserting or removing socketed ICs.","Prototype/unvalidated: verify mechanical fit and electrical levels before relying on results."]
    for index,text_value in enumerate(notes):
        body.append(f'(text {q(text_value)} (at 20.32 {17.78+index*5.08} 0) {effects(1.5 if index==0 else 1.0,"(justify left)")} (uuid {uid(name,"note/"+str(index))}))')
    embedded=[]
    for key,symbol in definitions.items():
        current=copy.deepcopy(symbol); current[1]=f"{name}:{key}"; embedded.append(dump(current))
    output=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root_uuid}) (paper "A2") (title_block (title {q(spec["title"])}) (date "2026-11-06") (rev {q(spec["rev"])}) (company {q(spec["company"])}) (comment 1 "UNBUILT PROTOTYPE") (comment 2 "Power off before changing DUT")) (lib_symbols {" ".join(embedded)}) {" ".join(body)} (sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
    (directory/f'{name}.kicad_sch').write_text(output)
    standalone=[]
    for key,symbol in definitions.items():
        current=copy.deepcopy(symbol); current[1]=key; standalone.append(dump(current))
    (directory/f'{name}.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+"\n".join(standalone)+'\n)\n')
    (directory/"sym-lib-table").write_text(f'(sym_lib_table (version 7) (lib (name "{name}")(type "KiCad")(uri "${{KIPRJMOD}}/{name}.kicad_sym")(options "")(descr "Local symbols")))\n')
    fp_extra='  (lib (name "V9958-Tester")(type "KiCad")(uri "${KIPRJMOD}/../V9958-Tester.pretty")(options "")(descr "V9958 tester footprints"))\n' if name.startswith("V9958-Tester-RevB") else '  (lib (name "V9958-Video-Daughterboard")(type "KiCad")(uri "${KIPRJMOD}/V9958-Video-Daughterboard.pretty")(options "")(descr "Daughterboard footprints"))\n'
    (directory/"fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n'+fp_extra+')\n')
    project={"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{name}.kicad_pro","version":1},"net_settings":{"classes":[],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{}}
    (directory/f'{name}.kicad_pro').write_text(json.dumps(project,indent=2)+"\n")
    print(f"Generated {name} schematic with {len(spec['components'])} footprints")


def generate_bom(spec):
    groups={}
    for item in spec["components"]:
        if item["ref"].startswith(("H","TP")): continue
        groups.setdefault((item["value"],item["footprint"]),[]).append(item["ref"])
    out=spec["directory"]/"docs"/"BOM.csv"
    with out.open("w",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n"); writer.writerow(("Quantity","References","Value / part","KiCad footprint"))
        for (value,footprint),refs in sorted(groups.items(),key=lambda x:x[1][0]): writer.writerow((len(refs)," ".join(refs),value,footprint))


def generate_board(spec):
    import pcbnew as p
    name=spec["name"]; directory=spec["directory"]; M=p.FromMM
    def V(x,y): return p.VECTOR2I(M(round(x,5)),M(round(y,5)))
    tree=ET.parse(directory/"docs"/f"{name}.xml").getroot(); board=p.BOARD(); board.SetCopperLayerCount(2)
    settings=board.GetDesignSettings(); settings.SetBoardThickness(M(1.6)); default=settings.m_NetSettings.GetDefaultNetclass(); default.SetClearance(M(0.30)); default.SetTrackWidth(M(0.25)); default.SetViaDiameter(M(0.70)); default.SetViaDrill(M(0.35))
    title=board.GetTitleBlock(); title.SetTitle(spec["title"]); title.SetRevision(spec["rev"]); title.SetDate("2026-11-06"); title.SetCompany(spec["company"])
    nets={}; pad_net={}
    for item in tree.findall("./nets/net"):
        net=p.NETINFO_ITEM(board,item.attrib["name"]); board.Add(net); nets[item.attrib["name"]]=net
        for n in item.findall("node"): pad_net[(n.attrib["ref"],n.attrib["pin"])]=net
    power=p.NETCLASS("Power"); power.SetClearance(M(0.30)); power.SetTrackWidth(M(0.60)); power.SetViaDiameter(M(0.80)); power.SetViaDrill(M(0.40)); settings.m_NetSettings.SetNetclass("Power",power)
    for netname in spec["power_nets"]:
        if netname in nets: nets[netname].SetNetClass(power); settings.m_NetSettings.SetNetclassPatternAssignment(netname,"Power")
    if spec.get("ground_plane_only"):
        ground=p.NETCLASS("Ground"); ground.SetClearance(M(0.30)); ground.SetTrackWidth(M(0.60)); ground.SetViaDiameter(M(0.80)); ground.SetViaDrill(M(0.40)); settings.m_NetSettings.SetNetclass("Ground",ground)
        if "/GND" in nets:
            nets["/GND"].SetNetClass(ground); settings.m_NetSettings.SetNetclassPatternAssignment("/GND","Ground")
    components={c.attrib["ref"]:c for c in tree.findall("./components/comp")}
    if set(components)!=set(spec["positions"]): raise RuntimeError(f"placement mismatch {set(components)^set(spec['positions'])}")
    libroot=pathlib.Path("/app/share/kicad/footprints")
    for ref,item in components.items():
        fpid=item.findtext("footprint"); lib,fpname=fpid.split(":",1)
        if lib=="V9958-Tester": root=REPO/"V9958-Tester.pretty"
        elif lib=="V9958-Video-Daughterboard": root=directory/"V9958-Video-Daughterboard.pretty"
        else: root=libroot/f"{lib}.pretty"
        fp=p.FootprintLoad(str(root),fpname)
        if fp is None: raise RuntimeError(f"cannot load {fpid}")
        fp.SetReference(ref); fp.SetValue(item.findtext("value")); fp.SetFPID(p.LIB_ID(lib,fpname)); fp.SetPath(p.KIID_PATH(f"/{uid(name,'schematic/root')}/{uid(name,ref)}"))
        x,y,angle=spec["positions"][ref]; fp.SetPosition(V(x,y)); fp.SetOrientationDegrees(angle); fp.Value().SetVisible(False); fp.Reference().SetVisible(ref not in spec["hide_refs"]); fp.Reference().SetTextSize(V(0.8,0.8)); fp.Reference().SetTextThickness(M(0.13)); fp.Reference().SetKeepUpright(True)
        if ref in spec["ref_positions"]:
            fp.Reference().SetPosition(V(*spec["ref_positions"][ref])); fp.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
        for pad in fp.Pads():
            net=pad_net.get((ref,pad.GetNumber()))
            if net is not None: pad.SetNet(net)
        board.Add(fp)
    width,height=spec["size"]
    for a,b in zip([(0,0),(width,0),(width,height),(0,height)],[(width,0),(width,height),(0,height),(0,0)]):
        edge=p.PCB_SHAPE(board); edge.SetShape(p.SHAPE_T_SEGMENT); edge.SetStart(V(*a)); edge.SetEnd(V(*b)); edge.SetLayer(p.Edge_Cuts); edge.SetWidth(M(0.05)); board.Add(edge)
    for text_value,x,y,size,angle in spec["silk"]:
        item=p.PCB_TEXT(board); item.SetText(text_value); item.SetPosition(V(x,y)); item.SetTextSize(V(size,size)); item.SetTextThickness(M(0.14)); item.SetLayer(p.F_SilkS); item.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T)); board.Add(item)
    for x,y in spec["plus"]:
        item=p.PCB_TEXT(board); item.SetText("+"); item.SetPosition(V(x,y)); item.SetTextSize(V(1.2,1.2)); item.SetTextThickness(M(0.18)); item.SetLayer(p.F_SilkS); board.Add(item)
    boardfile=directory/f"{name}.kicad_pcb"; p.SaveBoard(str(boardfile),board)
    if not p.ExportSpecctraDSN(board,str(directory/"docs"/"unrouted.dsn")): raise RuntimeError("DSN export failed")
    print(f"Placed {len(components)} footprints for {name}")


def finish_board(spec):
    import pcbnew as p
    name=spec["name"]; directory=spec["directory"]; M=p.FromMM
    board=p.LoadBoard(str(directory/f"{name}.kicad_pcb")); session=directory/"docs"/"routed.ses"
    if not p.ImportSpecctraSES(board,str(session)): raise RuntimeError(f"could not import {session}")
    footprints=list(board.GetFootprints()); pads={(item.GetReference(),pad.GetNumber()):pad for item in footprints for pad in item.Pads()}
    settings=board.GetDesignSettings(); settings.m_NetSettings.GetDefaultNetclass().SetClearance(M(0.20))
    try: settings.m_NetSettings.GetNetclass("Power").SetClearance(M(0.20))
    except Exception: pass
    for track in board.GetTracks():
        if not isinstance(track,p.PCB_VIA) and track.GetWidth()<M(0.25): track.SetWidth(M(0.25))
    for ref,number in spec["full_zone_pads"]:
        pad=pads[(ref,number)]
        pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    gnd=board.FindNet("/GND"); width,height=spec["size"]
    for layer in (p.F_Cu,p.B_Cu):
        zone=p.ZONE(board); zone.SetZoneName("GND plane"); zone.SetLayer(layer); zone.SetNet(gnd); zone.SetLocalClearance(M(0.25)); zone.SetMinThickness(M(0.20)); zone.SetThermalReliefGap(M(0.25)); zone.SetThermalReliefSpokeWidth(M(0.35)); zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
        poly=zone.Outline(); poly.NewOutline()
        for x,y in ((0.5,0.5),(width-0.5,0.5),(width-0.5,height-0.5),(0.5,height-0.5)): poly.Append(M(x),M(y))
        board.Add(zone)
    p.ZONE_FILLER(board).Fill(board.Zones())
    p.SaveBoard(str(directory/f"{name}.kicad_pcb"),board)
    print(f"Finished {name} with {len(list(board.GetTracks()))} tracks/vias")


def polish_board(spec):
    """Apply review-only silk/reference/thermal changes without touching routes."""
    import pcbnew as p
    name=spec["name"]; directory=spec["directory"]; M=p.FromMM
    def V(x,y): return p.VECTOR2I(M(round(x,5)),M(round(y,5)))
    board=p.LoadBoard(str(directory/f"{name}.kicad_pcb")); footprints=list(board.GetFootprints()); pads={(item.GetReference(),pad.GetNumber()):pad for item in footprints for pad in item.Pads()}
    for footprint in footprints:
        ref=footprint.GetReference(); field=footprint.Reference()
        field.SetVisible(ref not in spec["hide_refs"]); field.SetTextSize(V(0.8,0.8)); field.SetTextThickness(M(0.13)); field.SetKeepUpright(True)
        if ref in spec["ref_positions"]:
            field.SetPosition(V(*spec["ref_positions"][ref])); field.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    silk={text_value:(x,y,size,angle) for text_value,x,y,size,angle in spec["silk"]}
    for drawing in board.GetDrawings():
        if isinstance(drawing,p.PCB_TEXT) and drawing.GetText() in silk:
            x,y,size,angle=silk[drawing.GetText()]; drawing.SetPosition(V(x,y)); drawing.SetTextSize(V(size,size)); drawing.SetTextThickness(M(0.14)); drawing.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T))
    for drawing in list(board.GetDrawings()):
        if isinstance(drawing,p.PCB_TEXT) and drawing.GetText()=="+": board.Remove(drawing)
    for x,y in spec["plus"]:
        drawing=p.PCB_TEXT(board); drawing.SetText("+"); drawing.SetPosition(V(x,y)); drawing.SetTextSize(V(1.2,1.2)); drawing.SetTextThickness(M(0.18)); drawing.SetLayer(p.F_SilkS); board.Add(drawing)
    for ref,number in spec["full_zone_pads"]:
        pad=pads[(ref,number)]
        pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    p.ZONE_FILLER(board).Fill(board.Zones())
    p.SaveBoard(str(directory/f"{name}.kicad_pcb"),board)
    print(f"Polished {name} without changing routes")


def main():
    if len(sys.argv)<3 or sys.argv[1] not in PROJECTS or sys.argv[2] not in ("schematic","board","finish","polish","bom"):
        raise SystemExit("usage: aux_projects.py revb|revb2|daughter schematic|board|finish|polish|bom")
    spec=PROJECTS[sys.argv[1]]; mode=sys.argv[2]
    {"schematic":generate_schematic,"board":generate_board,"finish":finish_board,"polish":polish_board,"bom":generate_bom}[mode](spec)


if __name__=="__main__": main()
