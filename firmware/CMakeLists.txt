cmake_minimum_required(VERSION 3.13)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(v9958_tester C ASM)
set(CMAKE_C_STANDARD 11)

pico_sdk_init()

add_executable(v9958_tester main.c)
target_link_libraries(v9958_tester pico_stdlib hardware_adc hardware_pwm)
pico_enable_stdio_usb(v9958_tester 1)
pico_enable_stdio_uart(v9958_tester 0)
pico_add_extra_outputs(v9958_tester)

