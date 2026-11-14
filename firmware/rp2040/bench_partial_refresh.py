"""Time Windows_show against the production set_window override. Run with mpremote.

spi.write is counted through a proxy because machine.SPI may not allow attribute assignment.
Command bytes are 1 byte long; a pixel row is wider than that.
"""


class _CountingSPI:
    def __init__(self, spi):
        self._spi = spi
        self.rows = 0
        self.cmds = 0

    def write(self, buf):
        if len(buf) > 1:
            self.rows += 1
        else:
            self.cmds += 1
        return self._spi.write(buf)

    def __getattr__(self, name):
        return getattr(self._spi, name)


def _stats(samples):
    ordered = sorted(samples)
    count = len(ordered)
    total = 0
    for sample in ordered:
        total += sample
    mean_us = total / count
    return (mean_us / 1000,
            ordered[(95 * count + 99) // 100 - 1] / 1000,
            ordered[-1] / 1000)


def run():
    import gc
    import json
    import time
    from main import set_window
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            self.last_window = (x0, y0, x1, y1)
            set_window(self, x0, y0, x1, y1)

    regions = (
        ("40x40@(100,120)", 100, 120, 140, 160),
        ("120x120@(60,80)", 60, 80, 180, 200),
        ("band@x10-230,y120-160", 10, 120, 230, 160),
    )
    gc.collect()
    print("HEAP_BEFORE", gc.mem_free())
    lcd = Display()
    try:
        lcd.set_bl_pwm(8192)
        lcd.fill(0x4208)
        counter = _CountingSPI(lcd.spi)
        lcd.spi = counter
        gc.collect()
        for name, x0, y0, x1, y1 in regions:
            for _ in range(3):
                lcd.Windows_show(x0, y0, x1, y1)
            samples = []
            row_counts = []
            cmd_counts = []
            for _ in range(30):
                counter.rows = 0
                counter.cmds = 0
                start = time.ticks_us()
                lcd.Windows_show(x0, y0, x1, y1)
                elapsed = time.ticks_diff(time.ticks_us(), start)
                if elapsed <= 0:
                    raise ValueError("clock did not advance")
                samples.append(elapsed)
                row_counts.append(counter.rows)
                cmd_counts.append(counter.cmds)
            window = lcd.last_window
            width = window[2] - window[0]
            height = window[3] - window[1]
            nbytes = width * height * 2
            mean_ms, p95_ms, max_ms = _stats(samples)
            print(json.dumps({
                "name": name,
                "requested": [x0, y0, x1, y1],
                "effective": list(window),
                "effective_px": [width, height],
                "bytes": nbytes,
                "samples": len(samples),
                "mean_ms": mean_ms,
                "p95_ms": p95_ms,
                "max_ms": max_ms,
                "row_writes": row_counts[-1],
                "row_writes_min": min(row_counts),
                "row_writes_max": max(row_counts),
                "cmd_writes": cmd_counts[-1],
                "bytes_s": (nbytes / (mean_ms / 1000.0)) if mean_ms else 0,
                "heap_free": gc.mem_free(),
            }))

        lcd.last_window = None
        try:
            lcd.Windows_show(200, 120, 240, 160)
            print(json.dumps({
                "name": "edge_40x40@(200,120)",
                "result": "no_error",
                "effective": list(lcd.last_window) if lcd.last_window else None,
            }))
        except Exception as exc:
            print(json.dumps({
                "name": "edge_40x40@(200,120)",
                "result": "error",
                "exc_type": exc.__class__.__name__,
                "exc_msg": str(exc),
                "effective": list(lcd.last_window) if lcd.last_window else None,
            }))

        lcd.spi = counter._spi
        gc.collect()
        show_samples = []
        show_rows = []
        for _ in range(20):
            counter.rows = 0
            counter.cmds = 0
            start = time.ticks_us()
            lcd.show()
            elapsed = time.ticks_diff(time.ticks_us(), start)
            if elapsed <= 0:
                raise ValueError("clock did not advance")
            show_samples.append(elapsed)
            show_rows.append(counter.rows)
        mean_ms, p95_ms, max_ms = _stats(show_samples)
        print(json.dumps({
            "name": "show",
            "bytes": 134400,
            "samples": len(show_samples),
            "mean_ms": mean_ms,
            "p95_ms": p95_ms,
            "max_ms": max_ms,
            "row_writes": show_rows[-1],
            "cmd_writes": 0,
            "bytes_s": 134400 / (mean_ms / 1000.0),
            "heap_free": gc.mem_free(),
        }))
        if 45.0 <= mean_ms <= 65.0:
            print("CONTROL_IN_RANGE")
        else:
            print("CONTROL_OUT_OF_RANGE")

        # Command overhead only: production set_window, no pixel payload.
        cmd_samples = []
        for _ in range(50):
            start = time.ticks_us()
            set_window(lcd, 90, 110, 150, 170)
            elapsed = time.ticks_diff(time.ticks_us(), start)
            if elapsed <= 0:
                raise ValueError("clock did not advance")
            cmd_samples.append(elapsed)
        mean_ms, p95_ms, max_ms = _stats(cmd_samples)
        print(json.dumps({
            "name": "set_window(90,110,150,170)",
            "bytes": 0,
            "samples": len(cmd_samples),
            "mean_ms": mean_ms,
            "p95_ms": p95_ms,
            "max_ms": max_ms,
            "bytes_s": 0,
            "heap_free": gc.mem_free(),
        }))
        print("DONE")
    finally:
        lcd.set_bl_pwm(0)


if __name__ == "__main__":
    run()
