# Pinned Waveshare V2 reference

`esp_lcd_sh8601.c` and `.h` are copied **byte for byte** from:

- Repository: https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.64-v2
- Commit: `21b952243d306692774f3b5bfeb3eb5cff10f851`
- Path: `Arduino/examples/06_LVGL_Test/`
- Original headers identify Espressif Systems, Apache-2.0; see [LICENSE](LICENSE).

The pin macros, QSPI IO configuration, init table, RGB order, X offset and
byte swap are traced to `lcd_config.h`, `lcd_bsp.c` and
`Arduino/libraries/lv_conf.h` at that same revision. Our `display.c` adapts
that initialization without LVGL or touch. It uses native two-row strips,
software rotation baked into the assets and completion-checked DMA.
The eight-command panel override is retained in full; the generic driver's
three-command fallback is not used. The driver's hardware `swap_xy` rejects
rotation, so no guessed hardware rotation register is sent.

The product calls the panel CO5300; the vendor example calls this driver
SH8601. We retain the complete matching reference rather than infer panel
identity from either name. Physical identification and operation are pending.

Unmodified vendor behavior: `draw_bitmap` does not propagate `tx_color`'s
return code. Our renderer checks the call and aborts on a missing completion
within one second; it never reuses a potentially active DMA strip on timeout.
