"""Transfer-only timing for the ordered board; no animation decoding or scan-rate changes."""


def measure_show(lcd, clock, samples=120):
    if not 1 <= samples <= 1000:
        raise ValueError('samples must be between 1 and 1000')
    durations = [0] * samples
    for index in range(samples):
        start = clock.ticks_us()
        lcd.show()
        elapsed = clock.ticks_diff(clock.ticks_us(), start)
        if elapsed <= 0:
            raise ValueError('clock must resolve a display transfer')
        durations[index] = elapsed
    ordered = sorted(durations)
    total = sum(durations)
    return {'samples': samples, 'mean_us': total / samples,
            'p95_us': ordered[(95*samples+99)//100-1], 'max_us': ordered[-1],
            'transfer_only_fps': samples * 1000000 / total}


def run():
    import gc
    import time
    from main import set_window
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    lcd = Display()
    try:
        lcd.set_bl_pwm(32768)
        lcd.fill(0x4208)  # A steady dark image avoids strobing while timing writes.
        for _ in range(3):
            lcd.show()
        gc.collect()
        print('SPI configuration:', lcd.spi)
        print('Free heap before:', gc.mem_free())
        print(measure_show(lcd, time))
        print('Free heap after:', gc.mem_free())
        print('Transfer only: add flash reads, decoding and scheduling before choosing animation FPS.')
    finally:
        lcd.set_bl_pwm(0)


if __name__ == '__main__':
    run()
