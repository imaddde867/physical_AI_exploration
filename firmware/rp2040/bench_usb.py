"""USB CDC receive benchmark, board side. Copy to the board as main.py for the run, then put the
real firmware/rp2040/main.py back. Pair with tools/bench_usb.py on the Mac. See the buddy-os spec."""
import binascii
import gc
import micropython
import select
import sys

from waveshare_lcd import LCD_1inch69

STALL_MS = 200


def recv_into(buf, n, poller):
    """Fill buf[:n] from stdin; False when the stream stalls for STALL_MS."""
    view, got = memoryview(buf), 0
    while got < n:
        if not poller.poll(STALL_MS):
            return False
        k = sys.stdin.buffer.readinto(view[got:n])
        if k:
            got += k
    return True


def run():
    lcd = LCD_1inch69()
    lcd.set_bl_pwm(8192)
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)
    gc.collect()
    print("bench ready; free heap:", gc.mem_free())
    try:
        while True:
            n, show = [int(x) for x in sys.stdin.readline().split()[1:3]]
            if n == 0:
                break
            micropython.kbd_intr(-1)  # 0x03 in the payload must not raise KeyboardInterrupt
            try:
                ok = recv_into(lcd.buffer, n, poller)
            finally:
                micropython.kbd_intr(3)
            if not ok:
                continue  # stalled: no reply, the host counts a failure
            if show:
                lcd.show()
            sys.stdout.write("OK %d %d\n" % (binascii.crc32(memoryview(lcd.buffer)[:n]), gc.mem_free()))
    finally:
        lcd.set_bl_pwm(0)
        micropython.kbd_intr(3)


run()
