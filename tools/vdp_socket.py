"""Through-hole model selector and dual sync receiver shared by the tester PCBs."""

LM393 = {1: "OUTA", 2: "INA-", 3: "INA+", 4: "GND",
          5: "INB+", 6: "INB-", 7: "OUTB", 8: "V+"}
HC14 = {1: "1A", 2: "1Y", 3: "2A", 4: "2Y", 5: "3A", 6: "3Y", 7: "GND",
          8: "4Y", 9: "4A", 10: "5Y", 11: "5A", 12: "6Y", 13: "6A", 14: "VCC"}
# Column assignments follow KiCad's JS202011CQN footprint, viewed from above.
SELECTOR = {1: "38-A", 2: "COM-A", 3: "58-A", 4: "58-B", 5: "COM-B", 6: "38-B"}

AXIAL = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
DISC = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"

# R43 remains connected when SW2 is open or in transit. SW2 only bypasses
# R43 in the V9958 position. The other pole selects the sync slicing level.
PARTS = [
    ("SW2", "VDP_Select", "JS202011CQN", "Button_Switch_THT:SW_CK_JS202011CQN_DPDT_Straight",
     {2: "VDP_PIN21", 3: "VCCVDP", 4: "REF_58", 5: "SYNC_REF", 6: "REF_38"}),
    ("U10", "LM393", "LM393P", "Package_DIP:DIP-8_W7.62mm",
     {1: "H_COMP", 2: "H_HALF", 3: "SYNC_REF", 4: "GND",
      5: "SYNC_REF", 6: "C_HALF", 7: "C_COMP", 8: "VCCVDP"}),
    ("R43", "R", "470", AXIAL, {1: "VCCVDP", 2: "VDP_PIN21"}),
    ("R44", "R", "15k 1%", AXIAL, {1: "VCCVDP", 2: "REF_38"}),
    ("R45", "R", "6.2k 1%", AXIAL, {1: "REF_38", 2: "REF_58"}),
    ("R46", "R", "4.3k 1%", AXIAL, {1: "REF_58", 2: "GND"}),
    ("R47", "R", "10k", AXIAL, {1: "VCCVDP", 2: "WAIT_RAW"}),
    ("U11", "74HC14", "SN74HC14N", "Package_DIP:DIP-14_W7.62mm",
     {1: "H_COMP", 2: "HSYNC_TTL", 3: "C_COMP", 4: "CSYNC_TTL",
      5: "GND", 7: "GND", 9: "GND", 11: "GND", 13: "GND", 14: "VCCVDP"}),
    ("C30", "C", "100n", DISC, {1: "VCCVDP", 2: "GND"}),
    ("R48", "R", "47k 1%", AXIAL, {1: "HSYNC_RAW", 2: "H_HALF"}),
    ("R49", "R", "47k 1%", AXIAL, {1: "H_HALF", 2: "GND"}),
    ("R50", "R", "47k 1%", AXIAL, {1: "CSYNC_RAW", 2: "C_HALF"}),
    ("R51", "R", "47k 1%", AXIAL, {1: "C_HALF", 2: "GND"}),
    ("R52", "R", "2.2k", AXIAL, {1: "VCCVDP", 2: "H_COMP"}),
    ("R53", "R", "2.2k", AXIAL, {1: "VCCVDP", 2: "C_COMP"}),
    ("C29", "C", "100n U10", DISC, {1: "VCCVDP", 2: "GND"}),
]
