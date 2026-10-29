idf_component_register(SRCS "main.c" "display.c" "vendor/esp_lcd_sh8601.c"
    INCLUDE_DIRS "." "../include" "vendor"
    REQUIRES esp_lcd driver json esp_timer)
