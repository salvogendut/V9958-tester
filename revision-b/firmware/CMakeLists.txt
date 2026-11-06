cmake_minimum_required(VERSION 3.13)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(v9958_tester_revb C ASM)
set(CMAKE_C_STANDARD 11)

pico_sdk_init()

add_executable(v9958_tester_revb ../../firmware/main.c)
target_compile_definitions(v9958_tester_revb PRIVATE V9958_REV_B=1)
target_link_libraries(v9958_tester_revb pico_stdlib hardware_adc hardware_pwm)
pico_enable_stdio_usb(v9958_tester_revb 1)
pico_enable_stdio_uart(v9958_tester_revb 0)
pico_add_extra_outputs(v9958_tester_revb)
