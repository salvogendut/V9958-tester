# RGB DIN daughterboard test procedure

1. With both boards unpowered, check C6, C8 and C10–C13. The positive lead goes in rounded-square pad 1 beside the footprint `+`, and the striped lead goes in circular pad 2. Check that the J2 opening sits flush with the top edge. Insert the RGB plug from outside the board.
2. Check for a short between J1 pins 1 and 2.
3. Connect J1 to Revision B using a keyed straight-through 2x3 IDC cable. The
   pin-1 stripe must land on pin 1 at both ends. Do not power the daughterboard
   from a second supply.
4. Connect J2 only to an Omega-compatible RGB cable and a 15.6 kHz RGB/SCART
   display. Do not connect it to a VGA-only input.
5. Apply USB power to Revision B. A result screen should remain visible after
   the automated test.

With a terminated display attached, expect approximately 0.7 V peak-to-peak on
J2 red/green/blue and approximately 0.3-0.4 V active-low sync at J2 pin 4.
TP1/TP2 are +5 V/GND; TP3 is input CSYNC and TP4-TP6 are the coupled DIN RGB
outputs.
