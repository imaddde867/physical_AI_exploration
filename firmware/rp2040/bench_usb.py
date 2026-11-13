"""Temporary RP2040 USB CDC benchmark; deploy as main.py, then restore the backup.

Protocol: SYNC <16-hex session> -> SYNCED; BENCH <seq> <size> <show> <F|S>
-> READY <session> <seq>; then exactly <size> raw bytes -> OK <session> <seq>
<crc32> <heap>. F is the high-throughput path; S is a separately tested,
interruptible byte-wise recovery path. See docs/hardware/usb-benchmark.md.
"""
import binascii
import gc
import sys

STALL_MS = 200
HEADER_LIMIT = 80
SIZES = (16, 1024, 28800, 134400)
FAST_CHUNK = 256


def parse_header(line):
    """Return (command, arguments) or raise ValueError, without side effects."""
    fields = line.split()
    if not fields:
        return None
    if fields[0] == "SYNC" and len(fields) == 2:
        nonce = fields[1]
        if len(nonce) == 16 and all(c in "0123456789abcdef" for c in nonce):
            return ("sync", nonce)
    if fields[0] == "BENCH" and len(fields) == 5:
        try:
            seq, n, show = int(fields[1]), int(fields[2]), int(fields[3])
        except ValueError:
            raise ValueError("invalid integers")
        if 0 <= seq <= 1000000 and n in SIZES and show in (0, 1) and fields[4] in ("F", "S"):
            return ("bench", seq, n, show, fields[4])
    raise ValueError("invalid header")


def read_header(poller, source):
    """Bound header memory; an empty or incomplete line never crashes the device."""
    line = bytearray()
    dropping = False
    while True:
        if not poller.poll(STALL_MS):
            line = bytearray()  # abandon a truncated header
            dropping = False
            continue
        ch = source.read(1)  # safe after POLLIN: exactly one byte
        if not ch:
            continue
        b = ch[0]
        if b == 10:  # newline
            if dropping:
                line = bytearray()
                dropping = False
                continue
            if line and line[-1] == 13:
                line.pop()
            try:
                return bytes(line).decode("ascii")
            except Exception:
                return ""
        if len(line) >= HEADER_LIMIT:
            dropping = True
        elif not dropping:
            line.append(b)


def recv_into(buf, n, poller, source, mode):
    """Return (success, bytes_received). Only S guarantees a 200-ms stall timeout.

    On MicroPython 1.22.2, stdin.buffer.readinto(N) waits for ALL N bytes,
    even after select.poll() reports readiness. Therefore F can still block
    inside a partly supplied 256-byte chunk; use S for recovery tests.
    """
    got = 0
    view = memoryview(buf)
    if mode == "S":
        one = bytearray(1)
        while got < n:
            if not poller.poll(STALL_MS):
                return False, got
            if source.readinto(one) != 1:
                return False, got
            buf[got] = one[0]
            got += 1
    else:
        while got < n:
            if not poller.poll(STALL_MS):
                return False, got
            stop = min(n, got + FAST_CHUNK)
            k = source.readinto(view[got:stop])
            if not k:
                return False, got
            got += k
    return True, got


def run():
    import micropython
    import select
    from waveshare_lcd import LCD_1inch69

    lcd = LCD_1inch69()
    lcd.set_bl_pwm(8192)
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)
    gc.collect()
    sys.stdout.write("bench ready; free heap: %d\n" % gc.mem_free())
    session = None
    try:
        while True:
            line = read_header(poller, sys.stdin.buffer)
            try:
                command = parse_header(line)
            except ValueError:
                sys.stdout.write("ERR header\n")
                continue
            if command is None:
                continue
            if command[0] == "sync":
                session = command[1]
                sys.stdout.write("SYNCED %s\n" % session)
                continue
            if session is None:
                sys.stdout.write("ERR need_sync\n")
                continue
            _, seq, n, show, mode = command
            micropython.kbd_intr(-1)  # arm before READY; host MUST wait for READY
            try:
                sys.stdout.write("READY %s %d\n" % (session, seq))
                ok, got = recv_into(lcd.buffer, n, poller, sys.stdin.buffer, mode)
            finally:
                micropython.kbd_intr(3)
            if not ok:
                sys.stdout.write("ERR %s %d stall %d\n" % (session, seq, got))
                session = None  # require a fresh SYNC after truncated binary
                continue
            if show:
                lcd.show()  # always refreshes the entire framebuffer
            crc = binascii.crc32(memoryview(lcd.buffer)[:n])
            sys.stdout.write("OK %s %d %d %d\n" % (session, seq, crc, gc.mem_free()))
    finally:
        lcd.set_bl_pwm(0)
        micropython.kbd_intr(3)


if __name__ == "__main__":
    run()
