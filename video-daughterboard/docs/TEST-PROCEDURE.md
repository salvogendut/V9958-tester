# RGB DIN daughterboard test procedure

1. With both boards unpowered, verify capacitor polarity and socket orientation.
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
