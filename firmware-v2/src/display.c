// Initialization adapted from Waveshare V2 Arduino/06_LVGL_Test at
// 21b952243d306692774f3b5bfeb3eb5cff10f851. See vendor/README.md.
#include <assert.h>
#include "display.h"
#include "render_core.h"
#include "esp_lcd_sh8601.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "driver/spi_master.h"

static esp_lcd_panel_io_handle_t io;
static esp_lcd_panel_handle_t panel;
static SemaphoreHandle_t transferred;
static uint16_t *strip;

// Preserve the reference's complete V2 override, not the driver's generic default.
static const sh8601_lcd_init_cmd_t init_cmds[] = {
    {0x11, (uint8_t[]){0x00}, 0, 80},
    {0xC4, (uint8_t[]){0x80}, 1, 0},
    {0x35, (uint8_t[]){0x00}, 1, 0},
    {0x53, (uint8_t[]){0x20}, 1, 1},
    {0x63, (uint8_t[]){0xFF}, 1, 1},
    {0x51, (uint8_t[]){0x00}, 1, 1},
    {0x29, (uint8_t[]){0x00}, 0, 10},
    {0x51, (uint8_t[]){0xFF}, 1, 0},
};

static bool color_done(esp_lcd_panel_io_handle_t handle, esp_lcd_panel_io_event_data_t *event, void *context) {
    BaseType_t wake = pdFALSE;
    xSemaphoreGiveFromISR(transferred, &wake);
    return wake == pdTRUE;
}

void buddy_display_brightness(uint8_t value) {
    ESP_ERROR_CHECK(esp_lcd_panel_io_tx_param(io, (0x02u << 24) | (0x51u << 8), &value, 1));
}

void buddy_display_init(void) {
    transferred = xSemaphoreCreateBinary();
    strip = heap_caps_malloc(BUDDY_STRIP_PIXELS * sizeof(uint16_t), MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    assert(transferred && strip);
    const spi_bus_config_t bus = SH8601_PANEL_BUS_QSPI_CONFIG(10, 11, 12, 13, 14, BUDDY_STRIP_PIXELS * 2);
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
    const esp_lcd_panel_io_spi_config_t config = SH8601_PANEL_IO_QSPI_CONFIG(46, color_done, NULL);
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST, &config, &io));
    const sh8601_vendor_config_t vendor = {
        .init_cmds = init_cmds,
        .init_cmds_size = sizeof(init_cmds) / sizeof(init_cmds[0]),
        .flags.use_qspi_interface = 1,
    };
    const esp_lcd_panel_dev_config_t device = {
        .reset_gpio_num = 21,
        .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
        .bits_per_pixel = 16,
        .vendor_config = (void *)&vendor,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_sh8601(io, &device, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));
    // V2 reference flush adds X=0x14. Apply it exactly once here.
    ESP_ERROR_CHECK(esp_lcd_panel_set_gap(panel, 0x14, 0));
    buddy_display_brightness(0); // first clear/render while dark
}

static bool emit_strip(int y, const uint16_t *pixels, void *context) {
    ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(panel, 0, y, 280, y + 2, pixels));
    // Vendor draw queues DMA. Do not overwrite the strip before its callback.
    // Timeout is fatal rather than silently reusing a live DMA buffer.
    ESP_ERROR_CHECK(xSemaphoreTake(transferred, pdMS_TO_TICKS(1000)) == pdTRUE ? ESP_OK : ESP_ERR_TIMEOUT);
    return true;
}

void buddy_display_frame(unsigned frame) {
    ESP_ERROR_CHECK(buddy_render(frame, strip, emit_strip, NULL) ? ESP_OK : ESP_ERR_INVALID_SIZE);
}
