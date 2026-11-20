"""Through-hole model selector and dual sync receiver shared by the tester PCBs."""

MAX942 = {1: "OUTA", 2: "INA-", 3: "INA+", 4: "GND",
          5: "INB+", 6: "INB-", 7: "OUTB", 8: "V+"}
# Column assignments follow KiCad's JS202011CQN footprint, viewed from above.
SELECTOR = {1: "38-A", 2: "COM-A", 3: "58-A", 4: "58-B", 5: "COM-B", 6: "38-B"}

AXIAL = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
DISC = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"

# R43 remains connected when SW2 is open or in transit. SW2 only bypasses
# R43 in the V9958 position. The other pole selects the sync slicing level.
PARTS = [
    ("SW2", "VDP_Select", "JS202011CQN", "Button_Switch_THT:SW_CK_JS202011CQN_DPDT_Straight",
     {2: "VDP_PIN21", 3: "VCCVDP", 4: "REF_58", 5: "SYNC_REF", 6: "REF_38"}),
    ("U10", "MAX942", "MAX942CPA+", "Package_DIP:DIP-8_W7.62mm",
     {1: "HSYNC_TTL", 2: "SYNC_REF", 3: "HSYNC_RAW", 4: "GND",
      5: "CSYNC_RAW", 6: "SYNC_REF", 7: "CSYNC_TTL", 8: "VCCVDP"}),
    ("R43", "R", "470", AXIAL, {1: "VCCVDP", 2: "VDP_PIN21"}),
    ("R44", "R", "2.2k 1%", AXIAL, {1: "VCCVDP", 2: "REF_38"}),
    ("R45", "R", "6.2k 1%", AXIAL, {1: "REF_38", 2: "REF_58"}),
    ("R46", "R", "3.9k 1%", AXIAL, {1: "REF_58", 2: "GND"}),
    ("R47", "R", "10k", AXIAL, {1: "VCCVDP", 2: "WAIT_RAW"}),
    ("C29", "C", "100n U10", DISC, {1: "VCCVDP", 2: "GND"}),
]
