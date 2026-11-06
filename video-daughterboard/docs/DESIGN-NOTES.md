# RGB DIN daughterboard design notes

The raw Revision B RGB channels are AC-coupled into U1, a CXA1645P used as a
three-channel clamp and 75-ohm cable driver. R3-R5 are the 75-ohm source
resistors and C11-C13 are 220 uF output coupling capacitors. R6 attenuates TTL
CSYNC to approximately 0.35 V when the display supplies a 75-ohm termination.

R7/R8 generate the Omega AV-control voltage and R9/R10 generate its RGB/YS
control voltage. The unused composite, luma and chroma encoder outputs are not
connected. No colour subcarrier is required for the RGB-only path.

The PCB is 120 x 80 mm, two-layer, all THT, with 36 footprints, 98 pads, zero
SMD pads and ground pours on both sides. The DIN footprint must be checked
against the exact socket before manufacture.
