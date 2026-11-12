"""Local blink for Waveshare RP2040-Touch-LCD-1.69; see README.md."""
import math

try:  # on the board, daemon/protocol.py is copied to the root as protocol.py
    from daemon import protocol
except ImportError:
    import protocol

WIDTH, HEIGHT = 240, 280
EYE_R, EYE_DX, BLINK_MS, BLINK_EVERY_MS = 18, 42, 140, 4000
HOLD_MS = 2000  # a host-held blink releases itself, so a dead sender cannot freeze it
MAX_CHARS_PER_TICK = 256  # bounds input work so a flood cannot starve rendering
# One reply per tick: each write can stall for the USB TX timeout if the host stops reading.
MAX_REPLIES_PER_TICK = 1
OVERFLOW = object()  # LineReader sentinel: the line exceeded MAX_LINE and was dropped


class LineReader:
    """Frames newline-terminated lines and never buffers past the protocol byte limit."""

    def __init__(self, limit=protocol.MAX_LINE - 1):
        self.limit, self.chars, self.size, self.dropping = limit, [], 0, False

    def feed(self, ch):
        """One character in: None to continue, a complete line, or OVERFLOW."""
        if ch == "\n":
            over, self.dropping = self.dropping, False
            line, self.chars, self.size = "".join(self.chars).rstrip("\r"), [], 0
            return OVERFLOW if over else line
        if self.dropping:
            return None
        self.size += len(ch.encode())  # MAX_LINE counts UTF-8 bytes, not characters
        if self.size > self.limit:
            self.chars, self.size, self.dropping = [], 0, True  # drop to the next newline
            return None
        self.chars.append(ch)
        return None


def _line(msg):
    return protocol.encode(msg).decode()


def handle(text):
    """Apply one command line: (reply line, eyelid hold in ms or None)."""
    try:
        msg = protocol.decode(text)
    except protocol.ProtocolError as e:
        return _line({"v": 1, "t": "err", "code": e.code}), None
    if msg["t"] == "ping":
        return _line({"v": 1, "t": "ok"}), None
    if msg["t"] == "face" and not {"x", "y", "mood"} & set(msg):
        if "blink" in msg:
            return _line({"v": 1, "t": "ok"}), HOLD_MS if msg["blink"] else 0
        return _line({"v": 1, "t": "ok"}), None
    # Valid protocol messages this prototype cannot render yet.
    return _line({"v": 1, "t": "err", "code": "unsupported"}), None


def gray(level):
    """RGB565 gray, byte-swapped for the driver's direct SPI buffer write."""
    packed = ((level >> 3) << 11) | ((level >> 2) << 5) | (level >> 3)
    return ((packed & 255) << 8) | (packed >> 8)


EYE_COLOR = gray(232)


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
            lcd.fill_rect(cx - EYE_R, cy - 2, 2 * EYE_R + 1, 4, EYE_COLOR)
        else:
            for dy in range(-EYE_R, EYE_R + 1):
                inner_sq = (EYE_R - 0.5) ** 2 - dy * dy
                inner = int(math.sqrt(inner_sq)) if inner_sq >= 0 else -1
                if inner >= 0:
                    lcd.fill_rect(cx - inner, cy + dy, 2 * inner + 1, 1, EYE_COLOR)
                outer = int(math.sqrt((EYE_R + 0.5) ** 2 - dy * dy))
                for dx in range(inner + 1, outer + 1):
                    # A one-pixel coverage ramp smooths the silhouette without a halo.
                    coverage = EYE_R + 0.5 - math.sqrt(dx * dx + dy * dy)
                    if coverage > 0:
                        color = EYE_COLOR if coverage >= 1 else gray(int(232 * coverage))
                        lcd.fill_rect(cx + dx, cy + dy, 1, 1, color)
                        if dx:
                            lcd.fill_rect(cx - dx, cy + dy, 1, 1, color)
    lcd.show()


def run():
    import gc
    import select
    import sys
    import time
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    gc.collect()
    lcd = Display()  # The vendor driver owns the only 134,400-byte framebuffer.
    try:
        lcd.set_bl_pwm(8192)
        gc.collect()
        # USB serial shares one stream with the REPL, so reads are polled, not blocked on.
        poller = select.poll()
        poller.register(sys.stdin, select.POLLIN)
        reader = LineReader()
        print("blink ready; free heap:", gc.mem_free(), "bytes; Ctrl-C to stop")
        previous = time.ticks_ms()
        phase, last_blink, hold_ms = BLINK_MS, None, 0
        while True:
            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, previous)
            # Accumulate short tick differences so long runs survive clock wraparound.
            phase = (phase + elapsed) % BLINK_EVERY_MS
            previous = now
            if hold_ms:
                hold_ms = max(0, hold_ms - elapsed)  # release a hold the host left behind
            replied = 0
            for _ in range(MAX_CHARS_PER_TICK):
                if replied >= MAX_REPLIES_PER_TICK:
                    break
                if not poller.poll(0):
                    break
                ch = sys.stdin.read(1)
                if not ch:  # a vanished host keeps the eyes animating
                    break
                line = reader.feed(ch)
                if line is None:
                    continue
                if line is OVERFLOW:
                    sys.stdout.write(_line({"v": 1, "t": "err", "code": "too_long"}))
                    replied += 1
                    continue
                reply, hold = handle(line)
                if hold is not None:
                    hold_ms = hold
                    if not hold:
                        phase = BLINK_MS  # reopen now, and start a fresh four-second cycle
                sys.stdout.write(reply)
                replied += 1
            blink = hold_ms > 0 or phase < BLINK_MS
            if blink != last_blink:
                draw(lcd, blink)
                last_blink = blink
            time.sleep_ms(20)
    finally:
        lcd.set_bl_pwm(0)


if __name__ == "__main__":
    run()
