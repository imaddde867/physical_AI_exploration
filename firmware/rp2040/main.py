"""Local blink for Waveshare RP2040-Touch-LCD-1.69; see README.md."""
import math

WIDTH, HEIGHT = 240, 280
EYE_R, EYE_DX, BLINK_MS, BLINK_EVERY_MS = 18, 42, 140, 4000


def set_window(lcd, x0, y0, x1, y1):
    """Exclusive end coordinates, with the panel's 20-row offset."""
    if not (0 <= x0 < x1 <= WIDTH and 0 <= y0 < y1 <= HEIGHT):
        raise ValueError("display window is outside the panel")
    # The vendor example uses Ystart instead of Yend for the bottom row.
    for cmd, start, end in ((0x2A, x0, x1 - 1), (0x2B, y0 + 20, y1 + 19)):
        lcd.write_cmd(cmd)
        for value in (start >> 8, start & 255, end >> 8, end & 255):
            lcd.write_data(value)
    lcd.write_cmd(0x2C)


def draw(lcd, blink):
    lcd.fill(0)
    for sign in (-1, 1):
        cx, cy = WIDTH // 2 + sign * EYE_DX, HEIGHT // 2
        if blink:
            lcd.fill_rect(cx - EYE_R, cy - 2, 2 * EYE_R + 1, 4, 0xFFFF)
        else:
            for dy in range(-EYE_R, EYE_R + 1):
                half = int(math.sqrt(EYE_R * EYE_R - dy * dy) + 0.5)
                lcd.fill_rect(cx - half, cy + dy, 2 * half + 1, 1, 0xFFFF)
    lcd.show()


def run():
    import gc
    import time
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    gc.collect()
    lcd = Display()  # The vendor driver owns the only 134,400-byte framebuffer.
    try:
        lcd.set_bl_pwm(32768)
        gc.collect()
        print("blink ready; free heap:", gc.mem_free(), "bytes; Ctrl-C to stop")
        previous = time.ticks_ms()
        phase, last_blink = BLINK_MS, None
        while True:
            now = time.ticks_ms()
            # Accumulate short tick differences so long runs survive clock wraparound.
            phase = (phase + time.ticks_diff(now, previous)) % BLINK_EVERY_MS
            previous = now
            blink = phase < BLINK_MS
            if blink != last_blink:
                draw(lcd, blink)
                last_blink = blink
            time.sleep_ms(20)
    finally:
        lcd.set_bl_pwm(0)


if __name__ == "__main__":
    run()
