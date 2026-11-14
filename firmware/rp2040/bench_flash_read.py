"""Time LittleFS reads into the one LCD framebuffer. Run with mpremote; do not replace main.py.

Two 134,400-byte buffers do not fit in RP2040 SRAM, so every read uses lcd.buffer.
"""


def _stats(samples, nbytes):
    ordered = sorted(samples)
    count = len(ordered)
    total = 0
    for sample in ordered:
        total += sample
    mean_us = total / count
    p95_us = ordered[(95 * count + 99) // 100 - 1]
    max_us = ordered[-1]
    mb_s = (nbytes / mean_us) if mean_us and nbytes else 0.0
    return mean_us / 1000, p95_us / 1000, max_us / 1000, mb_s


def _emit(name, nbytes, samples, crc, heap, transfer=None):
    import json
    moved = nbytes if transfer is None else transfer
    mean_ms, p95_ms, max_ms, mb_s = _stats(samples, moved)
    print(json.dumps({
        "file": name,
        "bytes": nbytes,
        "samples": len(samples),
        "mean_ms": mean_ms,
        "p95_ms": p95_ms,
        "max_ms": max_ms,
        "mb_s": mb_s,
        "crc32": crc,
        "heap_free": heap,
    }))


def _timed(clock, count, fn):
    samples = []
    for _ in range(count):
        start = clock.ticks_us()
        fn()
        elapsed = clock.ticks_diff(clock.ticks_us(), start)
        if elapsed <= 0:
            raise ValueError("clock did not advance")
        samples.append(elapsed)
    return samples


def run():
    import binascii
    import gc
    import json
    import os
    import time
    from main import set_window
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    files = (("watch-final.rgb565", 134400), ("watch-frame.rgb565", 33600))
    gc.collect()
    print("HEAP_BEFORE", gc.mem_free())
    lcd = Display()
    try:
        lcd.set_bl_pwm(8192)
        view = memoryview(lcd.buffer)
        gc.collect()
        print("HEAP_LCD", gc.mem_free())
        for name, size in files:
            found = os.stat(name)[6]
            if found != size:
                raise ValueError("%s is %s bytes, expected %s" % (name, found, size))
            handle = open(name, "rb")
            try:
                def read_frame(handle=handle, size=size):
                    handle.seek(0)
                    got = handle.readinto(view)
                    if got != size:
                        raise ValueError("short read %s got %s" % (name, got))

                gc.collect()
                samples = _timed(time, 100, read_frame)
                crc = binascii.crc32(view[:size]) & 0xFFFFFFFF
            finally:
                handle.close()
            _emit(name, size, samples, crc, gc.mem_free())

        # seek(0) from EOF, so the sample is a real reposition and not a no-op at offset 0.
        # The untimed seek-to-end is outside the ticks window.
        for name, size in files:
            handle = open(name, "rb")
            try:
                samples = []
                for _ in range(100):
                    try:
                        handle.seek(0, 2)
                    except Exception:
                        handle.seek(size)
                    start = time.ticks_us()
                    handle.seek(0)
                    elapsed = time.ticks_diff(time.ticks_us(), start)
                    if elapsed < 0:
                        raise ValueError("clock went backwards")
                    samples.append(elapsed)
            finally:
                handle.close()
            gc.collect()
            _emit("seek:" + name, size, samples, None, gc.mem_free(), transfer=0)

        for name, size in files:
            def reopen(name=name):
                handle = open(name, "rb")
                handle.close()

            gc.collect()
            _emit("open:" + name, size, _timed(time, 100, reopen), None, gc.mem_free(), transfer=0)

        gc.collect()
        show_samples = _timed(time, 20, lcd.show)
        _emit("show", 134400, show_samples, None, gc.mem_free())
        mean_ms = _stats(show_samples, 134400)[0]
        if 45.0 <= mean_ms <= 65.0:
            print("CONTROL_IN_RANGE")
        else:
            print("CONTROL_OUT_OF_RANGE")
        print("DONE")
    finally:
        lcd.set_bl_pwm(0)


if __name__ == "__main__":
    run()
