# Revision B2 firmware

B2 uses the shared Revision B pinout and firmware source in
`../../firmware/main.c`. The SRAM adapter is transparent to the tester code.

```sh
export PICO_SDK_PATH=/path/to/pico-sdk
cmake -S revision-b2-sram/firmware -B revision-b2-sram/firmware/build -DPICO_BOARD=pico
cmake --build revision-b2-sram/firmware/build -j4
```

Send `R` or `r` over the Pico USB CDC serial port to repeat the test.

The supplied [B2.1 UF2](v9958_tester_revb2.uf2) identifies both chips on boards fitted with SW2. Set SW2 before applying power.
