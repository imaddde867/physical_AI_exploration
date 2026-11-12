"""Mac-side service: keeps the RP2040 fed with valid messages and blinks it; stdlib only.

Usage: python3 tools/buddy_service.py [/dev/cu.usbmodemXXXX]   (Ctrl-C to stop)
Sends a ping every HEARTBEAT_S (protocol: at least one valid message per 2 s) and a
blink every BLINK_EVERY_S. Reconnects when the cable is replugged.
"""
import glob
import os
import sys
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from daemon import protocol
from tools.send_blink import blink_lines, open_raw, read_replies, send

HEARTBEAT_S = 1.5
BLINK_EVERY_S = 5.0
RETRY_S = 1.0
PING = protocol.encode({"v": 1, "t": "ping"})


def serve(fd, clock=time.monotonic, sleep=time.sleep, until=None):
    """Drive one open port until it errors (OSError) or `until()` is true."""
    next_blink = clock() + BLINK_EVERY_S
    while not (until and until()):
        os.write(fd, PING)
        read_replies(fd, timeout=0.05)  # drain replies so the device TX never backs up
        if clock() >= next_blink:
            send(fd, blink_lines())
            next_blink = clock() + BLINK_EVERY_S
        sleep(HEARTBEAT_S)


def find_port(argv):
    if len(argv) > 1:
        return argv[1]
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    return ports[0] if ports else None


def main(argv):
    while True:
        path = find_port(argv)
        try:
            if path is None:
                raise OSError("no /dev/cu.usbmodem* port")
            fd, saved = open_raw(path)
            print(f"connected {path}", flush=True)
            try:
                serve(fd)
            finally:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, saved)
                finally:
                    os.close(fd)
        except OSError as e:
            print(f"waiting for device: {e}", flush=True)
            time.sleep(RETRY_S)
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
