"""Send one blink to the RP2040 over USB serial; standard library only.

Usage: python3 tools/send_blink.py [/dev/cu.usbmodem1101]
Exits 0 only when both messages were answered `ok`; the eyes are the real confirmation.
"""
import os
import select
import sys
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from daemon import protocol
from daemon.port import open_raw  # noqa: F401  (re-exported for buddy_service)

DEFAULT_PORT = "/dev/cu.usbmodem1101"
REPLY_WAIT_S = 0.5


def blink_lines():
    """Close the eyelids, hold about as long as the autonomous blink, then open."""
    return (protocol.encode({"v": 1, "t": "face", "blink": True}),
            protocol.encode({"v": 1, "t": "face", "blink": False}))


def send(fd, lines, hold_s=0.14):
    os.write(fd, lines[0])
    time.sleep(hold_s)
    os.write(fd, lines[1])


def read_replies(fd, timeout=REPLY_WAIT_S):
    """Everything the device said within the wait, as bytes; empty if it said nothing."""
    end = time.monotonic() + timeout
    chunks = []
    while True:
        left = end - time.monotonic()
        if left <= 0 or not select.select([fd], [], [], left)[0]:
            return b"".join(chunks)
        chunk = os.read(fd, protocol.MAX_LINE)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def acks(replies):
    """Leading `ok` replies, in order; the first protocol `err` ends the count.

    Startup banners and truncated lines are not protocol replies and are skipped.
    """
    count = 0
    for line in replies.splitlines():
        try:
            msg = protocol.decode(line)
        except protocol.ProtocolError:
            continue
        if msg["t"] != "ok":
            break
        count += 1
    return count


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_PORT
    lines = blink_lines()
    fd, saved = open_raw(path)
    try:
        send(fd, lines)
        replies = read_replies(fd)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        os.close(fd)
    sys.stdout.write(replies.decode(errors="replace") or "no reply\n")
    return 0 if acks(replies) == len(lines) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
