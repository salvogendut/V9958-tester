# Revision B firmware

This build uses the shared tester source in `../../firmware/main.c` with
`V9958_REV_B=1`. The electrical tests and optional on-screen result are the
same as revision 0.4. Revision B has no external TEST button; send `R` or `r`
over the Pico USB CDC serial port to repeat the test.

```sh
export PICO_SDK_PATH=/path/to/pico-sdk
cmake -S revision-b/firmware -B revision-b/firmware/build -DPICO_BOARD=pico
cmake --build revision-b/firmware/build -j4
```

The supplied [B1 UF2](v9958_tester_revb.uf2) identifies both chips on boards fitted with SW2. Set SW2 before applying power.
