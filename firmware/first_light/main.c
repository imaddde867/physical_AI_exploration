/* First-light diagnostic for the integrated Waveshare RP2040-Touch-LCD-1.69.
 * NOT for the standalone LCD module. No heap or full-screen framebuffer.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "pico/stdlib.h"
#include "pico/stdio_usb.h"
#include "core.h"

#define LCD_DC 8u
#define LCD_CS 9u
#define LCD_SCK 10u
#define LCD_MOSI 11u
#define LCD_RST 13u
#define LCD_BL 25u
#define SPI_BAUD 31250000u  /* vendor-demo rate; do not overclock first light */
#define MAX_LINE 512u       /* includes newline, as in docs/protocol.md */

static uint8_t scanline[BUDDY_ROW_BYTES];
static char serial_line[MAX_LINE + 1u];

static void gpio_output(unsigned pin, bool high) {
    gpio_init(pin);
    gpio_put(pin, high);
    gpio_set_dir(pin, GPIO_OUT);
}

static void spi_drain(void) {
    while (spi_is_busy(spi1)) tight_loop_contents();
}

static void lcd_command(uint8_t command, const uint8_t *data, size_t bytes) {
    gpio_put(LCD_CS, 0);
    gpio_put(LCD_DC, 0);
    spi_write_blocking(spi1, &command, 1);
    spi_drain();
    if (bytes) {
        gpio_put(LCD_DC, 1);
        spi_write_blocking(spi1, data, bytes);
        spi_drain();
    }
    gpio_put(LCD_CS, 1);
}

static void lcd_command1(uint8_t command, uint8_t value) {
    lcd_command(command, &value, 1);
}

static void lcd_init(void) {
    gpio_output(LCD_DC, false);
    gpio_output(LCD_CS, true);
    gpio_output(LCD_RST, true);
    gpio_output(LCD_BL, false);

    spi_init(spi1, SPI_BAUD);
    spi_set_format(spi1, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(LCD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(LCD_MOSI, GPIO_FUNC_SPI);

    sleep_ms(100);
    gpio_put(LCD_RST, 0);
    sleep_ms(100);
    gpio_put(LCD_RST, 1);
    sleep_ms(100);

    /* ST7789V2 init for THIS integrated board; transcribed from the
     * independently hardware-tested gud-panel Waveshare-demo port. */
    lcd_command1(0x36, 0x00); /* MADCTL, portrait RGB */
    lcd_command1(0x3A, 0x05); /* RGB565 */
    lcd_command(0xB2, (const uint8_t[]){0x0B, 0x0B, 0x00, 0x33, 0x35}, 5);
    lcd_command1(0xB7, 0x11);
    lcd_command1(0xBB, 0x35);
    lcd_command1(0xC0, 0x2C);
    lcd_command1(0xC2, 0x01);
    lcd_command1(0xC3, 0x0D);
    lcd_command1(0xC4, 0x20);
    lcd_command1(0xC6, 0x13);
    lcd_command(0xD0, (const uint8_t[]){0xA4, 0xA1}, 2);
    lcd_command1(0xD6, 0xA1);
    lcd_command(0xE0, (const uint8_t[]){
        0xF0, 0x06, 0x0B, 0x0A, 0x09, 0x26, 0x29,
        0x33, 0x41, 0x18, 0x16, 0x15, 0x29, 0x2D
    }, 14);
    lcd_command(0xE1, (const uint8_t[]){
        0xF0, 0x04, 0x08, 0x08, 0x07, 0x03, 0x28,
        0x32, 0x40, 0x3B, 0x19, 0x18, 0x2A, 0x2E
    }, 14);
    lcd_command(0xE4, (const uint8_t[]){0x25, 0x00, 0x00}, 3);
    lcd_command(0x21, NULL, 0); /* display inversion */
    lcd_command(0x11, NULL, 0); /* sleep out */
    sleep_ms(120);
    lcd_command(0x29, NULL, 0); /* display on */
}

static void lcd_pattern(void) {
    /* ST7789V2 RAM: 240x320; this 240x280 glass begins at row 20. */
    lcd_command(0x2A, (const uint8_t[]){0x00, 0x00, 0x00, 0xEF}, 4);
    const unsigned y0 = BUDDY_ROW_OFFSET;
    const unsigned y1 = BUDDY_ROW_OFFSET + BUDDY_HEIGHT - 1u;
    lcd_command(0x2B, (const uint8_t[]){
        (uint8_t)(y0 >> 8), (uint8_t)y0, (uint8_t)(y1 >> 8), (uint8_t)y1
    }, 4);
    gpio_put(LCD_CS, 0);
    gpio_put(LCD_DC, 0);
    const uint8_t ram_write = 0x2C;
    spi_write_blocking(spi1, &ram_write, 1);
    spi_drain();
    gpio_put(LCD_DC, 1);
    for (unsigned y = 0; y < BUDDY_HEIGHT; ++y) {
        buddy_pattern_row(y, scanline);
        spi_write_blocking(spi1, scanline, sizeof(scanline));
    }
    spi_drain();
    gpio_put(LCD_CS, 1);
    gpio_put(LCD_BL, 1);
}

static void handle_line(const char *line) {
    switch (buddy_parse(line)) {
        case BUDDY_PING:
            puts("{\"v\":1,\"t\":\"ok\"}");
            break;
        case BUDDY_SLEEP:
            gpio_put(LCD_BL, 0);
            lcd_command(0x28, NULL, 0);
            puts("{\"v\":1,\"t\":\"ok\"}");
            break;
        case BUDDY_WAKE:
            lcd_command(0x29, NULL, 0);
            gpio_put(LCD_BL, 1);
            puts("{\"v\":1,\"t\":\"ok\"}");
            break;
        case BUDDY_UNSUPPORTED:
            puts("{\"v\":1,\"t\":\"err\",\"code\":\"unsupported\"}");
            break;
    }
}

int main(void) {
    stdio_init_all();
    lcd_init();
    lcd_pattern();

    bool connected_before = false;
    bool dropping = false;
    unsigned length = 0;
    for (;;) {
        bool connected = stdio_usb_connected();
        if (connected && !connected_before) {
            puts("{\"v\":1,\"t\":\"hello\",\"fw\":\"first-light-0.1\",\"w\":240,\"h\":280}");
        }
        if (!connected) {
            length = 0;
            dropping = false;
        }
        connected_before = connected;

        int ch;
        while (connected && (ch = getchar_timeout_us(0)) != PICO_ERROR_TIMEOUT) {
            /* Accept Return (CR) in macOS screen and LF/CRLF from scripts. */
            if (ch == '\r' || ch == '\n') {
                if (dropping) {
                    puts("{\"v\":1,\"t\":\"err\",\"code\":\"too_long\"}");
                } else if (length) {
                    serial_line[length] = 0;
                    handle_line(serial_line);
                }
                length = 0;
                dropping = false;
            } else if (!dropping) {
                if (length < MAX_LINE - 1u) serial_line[length++] = (char)ch;
                else dropping = true;
            }
        }
        sleep_ms(5);
    }
}
