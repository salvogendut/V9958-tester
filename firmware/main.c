/*
 * V9938/V9958 Pico functional tester, prototype firmware.
 *
 * Set SW2 to match the DUT with USB power disconnected.
 * PASS covers the exercised functions of the identified VDP.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/sync.h"

#ifndef V9958_REV_B
#define V9958_REV_B 0
#endif


enum {
    PIN_D0 = 0,
    PIN_MODE0 = 8,
    PIN_MODE1 = 9,
    PIN_CSW_N = 10,
    PIN_CSR_N = 11,
    PIN_BUS_DIR = 12,
    PIN_BUS_OE_N = 13,
    PIN_VDP_RESET_N = 14,
    PIN_LED_GREEN = 15,
    PIN_LED_RED = 16,
    PIN_CPUCLK = 17,
    PIN_WAIT_N = 18,
    PIN_HSYNC_N = 19,
    PIN_INT_N = 20,
    PIN_CSYNC_N = 21,
    PIN_TEST_N = 22,
    PIN_ADC_R = 26,
    PIN_ADC_G = 27,
    PIN_ADC_B = 28,
};

#define DATA_MASK 0x000000ffu

enum test_error {
    ERR_NONE = 0,
    ERR_CLOCK = 1,
    ERR_ID = 2,
    ERR_CPU_BUS = 3,
    ERR_VRAM = 4,
    ERR_SYNC = 5,
    ERR_INTERRUPT = 6,
    ERR_RGB = 7,
};

enum vdp_model { VDP_UNKNOWN, VDP_V9938, VDP_V9958 };
static enum vdp_model model;

static const char *model_name(void) {
    switch (model) {
    case VDP_V9938: return "V9938";
    case VDP_V9958: return "V9958";
    default: return "UNKNOWN VDP";
    }
}

static void controls_idle(void) {
    gpio_put(PIN_CSW_N, 1);
    gpio_put(PIN_CSR_N, 1);
    gpio_put(PIN_BUS_OE_N, 1);
    gpio_put(PIN_MODE0, 0);
    gpio_put(PIN_MODE1, 0);
}

static void set_port(unsigned port) {
    gpio_put(PIN_MODE0, port & 1u);
    gpio_put(PIN_MODE1, (port >> 1u) & 1u);
}

static bool wait_ready_us(uint32_t timeout_us) {
    /* Pin 26 is the light-pen switch input on V9938. Identification uses
       fixed bus timing with the reset-default WAIT function disabled. */
    if (model != VDP_V9958) return true;
    absolute_time_t deadline = make_timeout_time_us(timeout_us);
    while (!gpio_get(PIN_WAIT_N)) {
        if (absolute_time_diff_us(get_absolute_time(), deadline) <= 0)
            return false;
    }
    return true;
}

static bool vdp_write_port(unsigned port, uint8_t value) {
    controls_idle();
    if (!wait_ready_us(100)) return false;
    set_port(port);
    gpio_put(PIN_BUS_DIR, 1);             /* LVC245 A (Pico) -> B (VDP). */
    gpio_set_dir_out_masked(DATA_MASK);
    gpio_put_masked(DATA_MASK, value);
    gpio_put(PIN_BUS_OE_N, 0);
    busy_wait_us_32(1);
    uint32_t irq_state = save_and_disable_interrupts();
    gpio_put(PIN_CSW_N, 0);
    /* 1 us is inside the V9958 186 ns..2 us strobe-width window. */
    busy_wait_us_32(1);
    gpio_put(PIN_CSW_N, 1);
    restore_interrupts(irq_state);
    /* 8 us also satisfies the longest documented inter-byte high time. */
    busy_wait_us_32(8);
    gpio_put(PIN_BUS_OE_N, 1);
    gpio_set_dir_in_masked(DATA_MASK);
    return wait_ready_us(100);
}

static bool vdp_read_port(unsigned port, uint8_t *value) {
    controls_idle();
    if (!wait_ready_us(100)) return false;
    set_port(port);
    gpio_put(PIN_BUS_DIR, 0);             /* LVC245 B (VDP) -> A (Pico). */
    gpio_set_dir_in_masked(DATA_MASK);
    gpio_put(PIN_BUS_OE_N, 0);
    busy_wait_us_32(1);
    uint32_t irq_state = save_and_disable_interrupts();
    gpio_put(PIN_CSR_N, 0);
    busy_wait_us_32(1);
    *value = (uint8_t)(gpio_get_all() & DATA_MASK);
    gpio_put(PIN_CSR_N, 1);
    restore_interrupts(irq_state);
    busy_wait_us_32(8);
    gpio_put(PIN_BUS_OE_N, 1);
    return wait_ready_us(100);
}

static bool vdp_reg(uint8_t reg, uint8_t value) {
    return vdp_write_port(1, value) && vdp_write_port(1, 0x80u | reg);
}

static bool vdp_status(uint8_t index, uint8_t *value) {
    if (!vdp_reg(15, index)) return false;
    bool ok = vdp_read_port(1, value);
    return vdp_reg(15, 0) && ok;
}

static bool vram_address(uint32_t address, bool write) {
    if (!vdp_reg(14, (address >> 14) & 7u)) return false;
    if (!vdp_write_port(1, address & 0xffu)) return false;
    uint8_t high = (address >> 8) & 0x3fu;
    if (write) high |= 0x40u;
    return vdp_write_port(1, high);
}

static uint8_t memory_pattern(uint32_t address, bool invert) {
    uint8_t value = (uint8_t)(address ^ (address >> 8) ^ (address >> 16) ^ 0x5au);
    return invert ? (uint8_t)~value : value;
}

static bool vram_pass(bool invert) {
    const uint32_t bytes = 128u * 1024u;
    const uint32_t block = 16u * 1024u;
    for (uint32_t base = 0; base < bytes; base += block) {
        if (!vram_address(base, true)) return false;
        for (uint32_t i = 0; i < block; ++i)
            if (!vdp_write_port(0, memory_pattern(base + i, invert))) return false;
    }
    for (uint32_t base = 0; base < bytes; base += block) {
        if (!vram_address(base, false)) return false;
        for (uint32_t i = 0; i < block; ++i) {
            uint8_t got;
            if (!vdp_read_port(0, &got)) return false;
            if (got != memory_pattern(base + i, invert)) {
                printf("VRAM mismatch @ 0x%05lx: got %02x expected %02x\n",
                       (unsigned long)(base + i), got,
                       memory_pattern(base + i, invert));
                return false;
            }
        }
    }
    return true;
}

static void count_monitor_edges(uint16_t *cpu, uint16_t *hsync, uint16_t *csync) {
    const uint pins[3] = {PIN_CPUCLK, PIN_HSYNC_N, PIN_CSYNC_N};
    uint slices[3];
    uint32_t mask = 0;
    for (unsigned i = 0; i < 3; ++i) {
        gpio_set_function(pins[i], GPIO_FUNC_PWM);
        slices[i] = pwm_gpio_to_slice_num(pins[i]);
        pwm_config cfg = pwm_get_default_config();
        pwm_config_set_clkdiv_mode(&cfg, PWM_DIV_B_RISING);
        pwm_config_set_wrap(&cfg, 0xffffu);
        pwm_init(slices[i], &cfg, false);
        pwm_set_counter(slices[i], 0);
        mask |= 1u << slices[i];
    }
    pwm_set_mask_enabled(mask);
    sleep_ms(10);
    pwm_set_mask_enabled(0);
    *cpu = pwm_get_counter(slices[0]);
    *hsync = pwm_get_counter(slices[1]);
    *csync = pwm_get_counter(slices[2]);
    for (unsigned i = 0; i < 3; ++i) {
        pwm_set_enabled(slices[i], false);
        gpio_set_function(pins[i], GPIO_FUNC_SIO);
        gpio_set_dir(pins[i], GPIO_IN);
    }
}

static uint16_t adc_average(unsigned input) {
    adc_select_input(input);
    (void)adc_read();
    uint32_t total = 0;
    for (unsigned i = 0; i < 64; ++i) {
        total += adc_read();
        busy_wait_us_32(20);
    }
    return (uint16_t)(total / 64u);
}

static bool palette(uint8_t index, uint8_t r, uint8_t g, uint8_t b) {
    return vdp_reg(16, index) &&
           vdp_write_port(2, (uint8_t)((r << 4) | b)) &&
           vdp_write_port(2, g);
}

static bool rgb_test(void) {
    if (!palette(1, 7, 0, 0) || !palette(2, 0, 7, 0) || !palette(3, 0, 0, 7))
        return false;
    /* Blank the display so every active pixel takes the programmed backdrop.
       The preceding inverted VRAM pattern otherwise appears on the ADCs. */
    if (!vdp_reg(0, 0) || !vdp_reg(1, 0) || !vdp_reg(9, 0x02)) return false;

    uint16_t sample[3][3];
    for (unsigned color = 0; color < 3; ++color) {
        if (!vdp_reg(7, (uint8_t)(color + 1))) return false;
        sleep_ms(40);
        sample[color][0] = adc_average(0);
        sample[color][1] = adc_average(1);
        sample[color][2] = adc_average(2);
    }
    printf("RGB ADC red=%u/%u/%u green=%u/%u/%u blue=%u/%u/%u\n",
           sample[0][0], sample[0][1], sample[0][2],
           sample[1][0], sample[1][1], sample[1][2],
           sample[2][0], sample[2][1], sample[2][2]);
    const uint16_t margin = 50; /* About 40 mV at a 3.3 V, 12-bit ADC. */
    return sample[0][0] > sample[1][0] + margin &&
           sample[0][0] > sample[2][0] + margin &&
           sample[1][1] > sample[0][1] + margin &&
           sample[1][1] > sample[2][1] + margin &&
           sample[2][2] > sample[0][2] + margin &&
           sample[2][2] > sample[1][2] + margin;
}

/* Compact 5x7 font used by the stand-alone DIN RGB result screen. */
static const uint8_t font_digits[10][7] = {
    {14,17,19,21,25,17,14}, {4,12,4,4,4,4,14},
    {14,17,1,2,4,8,31}, {30,1,1,14,1,1,30},
    {2,6,10,18,31,2,2}, {31,16,16,30,1,1,30},
    {14,16,16,30,17,17,14}, {31,1,2,4,8,8,8},
    {14,17,17,14,17,17,14}, {14,17,17,15,1,1,14},
};

static const uint8_t font_letters[26][7] = {
    {14,17,17,31,17,17,17}, {30,17,17,30,17,17,30},
    {14,17,16,16,16,17,14}, {30,17,17,17,17,17,30},
    {31,16,16,30,16,16,31}, {31,16,16,30,16,16,16},
    {14,17,16,23,17,17,15}, {17,17,17,31,17,17,17},
    {14,4,4,4,4,4,14}, {7,2,2,2,2,18,12},
    {17,18,20,24,20,18,17}, {16,16,16,16,16,16,31},
    {17,27,21,21,17,17,17}, {17,25,21,19,17,17,17},
    {14,17,17,17,17,17,14}, {30,17,17,30,16,16,16},
    {14,17,17,17,21,18,13}, {30,17,17,30,20,18,17},
    {15,16,16,14,1,1,30}, {31,4,4,4,4,4,4},
    {17,17,17,17,17,17,14}, {17,17,17,17,17,10,4},
    {17,17,17,21,21,21,10}, {17,17,10,4,10,17,17},
    {17,17,10,4,4,4,4}, {31,1,2,4,8,16,31},
};

static uint8_t glyph_row(char c, unsigned row) {
    uint8_t bits = 0;
    if (c >= '0' && c <= '9') bits = font_digits[c - '0'][row];
    else if (c >= 'A' && c <= 'Z') bits = font_letters[c - 'A'][row];
    else if (c == '-') bits = row == 3 ? 31 : 0;
    return (uint8_t)(bits << 3);
}

static bool text_write(unsigned row, unsigned column, const char *text) {
    if (!vram_address(row * 40u + column, true)) return false;
    while (*text) {
        if (!vdp_write_port(0, (uint8_t)*text++)) return false;
    }
    return true;
}

static bool show_result_screen(enum test_error result) {
    /* V9958 40-column text mode, PAL timing, pattern table at 0x0800. */
    if (!vdp_reg(1, 0x10) || !vdp_reg(0, 0x00) || !vdp_reg(2, 0x00) ||
        !vdp_reg(4, 0x01) || !vdp_reg(7, result == ERR_NONE ? 0xf2 : 0xf8) ||
        !vdp_reg(9, 0x02)) return false;

    for (unsigned c = 32; c <= 90; ++c) {
        if (!vram_address(0x0800u + c * 8u, true)) return false;
        for (unsigned row = 0; row < 7; ++row)
            if (!vdp_write_port(0, glyph_row((char)c, row))) return false;
        if (!vdp_write_port(0, 0)) return false;
    }
    if (!vram_address(0, true)) return false;
    for (unsigned i = 0; i < 40u * 24u; ++i)
        if (!vdp_write_port(0, ' ')) return false;

    static const char *const stage[] = {
        "ALL TESTS PASSED", "MASTER CLOCK", "VDP IDENTIFICATION",
        "CPU BUS OR WAIT", "128K VRAM", "HSYNC OR CSYNC",
        "VBLANK INTERRUPT", "RGB ANALOG OUTPUT",
    };
    char code[16];
    snprintf(code, sizeof(code), "RESULT CODE %u", (unsigned)result);
    if (!text_write(5, 14, model_name()) ||
        !text_write(9, result == ERR_NONE ? 18 : 17,
                    result == ERR_NONE ? "PASS" : "FAIL") ||
        !text_write(12, 12, stage[(unsigned)result]) ||
        !text_write(15, 13, code)) return false;
    return vdp_reg(1, 0x50);
}

static enum test_error run_test(void) {
    model = VDP_UNKNOWN;
    gpio_put(PIN_LED_GREEN, 0);
    gpio_put(PIN_LED_RED, 0);
    controls_idle();
    gpio_put(PIN_VDP_RESET_N, 0);
    sleep_ms(20);
    gpio_put(PIN_VDP_RESET_N, 1);
    sleep_ms(50);

    /* PAL, standard sync (S0=1) makes pin 5 horizontal sync during this
       measurement. At reset V9938 pin 5 carries the colour burst flag. */
    if (!vdp_reg(9, 0x12)) return ERR_CPU_BUS;
    sleep_ms(40);
    uint16_t cpu, hs, cs;
    count_monitor_edges(&cpu, &hs, &cs);
    printf("10 ms edge counts: CPUCLK=%u HSYNC=%u CSYNC=%u\n", cpu, hs, cs);
    if (cpu < 30000u || cpu > 42000u) return ERR_CLOCK;

    uint8_t s1;
    if (!vdp_status(1, &s1)) return ERR_CPU_BUS;
    unsigned id = (s1 >> 1) & 0x1fu;
    printf("Status #1=%02x, VDP ID=%u\n", s1, id);
    switch (id) {
    case 0: model = VDP_V9938; break;
    case 2: model = VDP_V9958; break;
    default: return ERR_ID;
    }
    printf("Detected %s\n", model_name());
    if (hs < 130u || hs > 190u || cs < 130u || cs > 190u) return ERR_SYNC;
    /* VR=1 selects 64K DRAM geometry. Disable sprites during the memory
       checks. Only V9958 implements R#25.WTE and has a WAIT output. */
    if (!vdp_reg(8, 0x0a)) return ERR_CPU_BUS;
    if (model == VDP_V9958 && !vdp_reg(25, 0x04)) return ERR_CPU_BUS;

    puts("VRAM pass 1/2: address pattern");
    if (!vram_pass(false)) return ERR_VRAM;
    puts("VRAM pass 2/2: inverted address pattern");
    if (!vram_pass(true)) return ERR_VRAM;

    uint8_t s0;
    if (!vdp_status(0, &s0)) return ERR_CPU_BUS;
    if (!gpio_get(PIN_INT_N)) return ERR_INTERRUPT;
    if (!vdp_reg(1, 0x60)) return ERR_CPU_BUS;
    absolute_time_t deadline = make_timeout_time_ms(100);
    while (gpio_get(PIN_INT_N) && absolute_time_diff_us(get_absolute_time(), deadline) > 0)
        tight_loop_contents();
    if (gpio_get(PIN_INT_N)) return ERR_INTERRUPT;
    if (!vdp_read_port(1, &s0)) return ERR_CPU_BUS;
    if (!(s0 & 0x80u) || !gpio_get(PIN_INT_N)) return ERR_INTERRUPT;
    printf("VBlank interrupt/status #0=%02x\n", s0);

    if (!rgb_test()) return ERR_RGB;
    return ERR_NONE;
}

static const char *error_name(enum test_error error) {
    static const char *const names[] = {
        "PASS", "master clock", "VDP identification", "CPU bus/WAIT",
        "128 KiB VRAM", "HSYNC/CSYNC", "VBlank interrupt", "RGB analog response"
    };
    return names[(unsigned)error < sizeof(names) / sizeof(names[0]) ? error : 0];
}

static void init_pins(void) {
    for (uint pin = 0; pin <= 22; ++pin) gpio_init(pin);
    gpio_set_dir_in_masked(DATA_MASK);
    for (uint pin = PIN_MODE0; pin <= PIN_LED_RED; ++pin) gpio_set_dir(pin, GPIO_OUT);
    for (uint pin = PIN_CPUCLK; pin <= PIN_TEST_N; ++pin) gpio_set_dir(pin, GPIO_IN);
    gpio_pull_up(PIN_TEST_N);
    controls_idle();
    gpio_put(PIN_BUS_DIR, 0);
    gpio_put(PIN_VDP_RESET_N, 0);
    gpio_put(PIN_LED_GREEN, 0);
    gpio_put(PIN_LED_RED, 0);
    adc_init();
    adc_gpio_init(PIN_ADC_R);
    adc_gpio_init(PIN_ADC_G);
    adc_gpio_init(PIN_ADC_B);
}

static void test_and_report(void) {
    enum test_error result = run_test();
    gpio_put(PIN_LED_GREEN, result == ERR_NONE);
    gpio_put(PIN_LED_RED, result != ERR_NONE);
    if (result == ERR_NONE)
        printf("RESULT: %s PASS (code 0)\n", model_name());
    else
        printf("RESULT: %s FAIL (code %u, %s)\n", model_name(), (unsigned)result, error_name(result));
    if (!show_result_screen(result)) puts("RGB result screen could not be displayed");
}

int main(void) {
    stdio_init_all();
    init_pins();
    sleep_ms(1500);
    puts("\nV9938/V9958 Pico functional tester");
    puts("Behavioral test only; power off before changing DUT/VRAM.");

    test_and_report();
    while (true) {
#if V9958_REV_B
        int ch = getchar_timeout_us(0);
        if (ch == 'r' || ch == 'R') test_and_report();
#else
        if (!gpio_get(PIN_TEST_N)) {
            sleep_ms(30);
            if (!gpio_get(PIN_TEST_N)) {
                while (!gpio_get(PIN_TEST_N)) sleep_ms(10);
                test_and_report();
            }
        }
#endif
        sleep_ms(20);
    }
}
