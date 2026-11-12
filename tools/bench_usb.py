"""USB CDC throughput benchmark, Mac side (slice 0 of the buddy-os spec); stdlib only.

Usage: python3 tools/bench_usb.py [/dev/cu.usbmodemXXXX]
Needs firmware/rp2040/bench_usb.py running on the board as main.py. For each size and show
mode it sends BENCH frames and prints per-run stats and the spec's decision.
"""
import binascii
import os
import select
import sys
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.send_blink import open_raw

SIZES = (28800, 134400)  # a 120x120 region and a full frame, RGB565
FRAMES = 100
REPLY_TIMEOUT_S = 2.0


def payload(n):
    return (bytes(range(256)) * (n // 256 + 1))[:n]


def decide(kb_s):
    if kb_s >= 500:
        return "adopt C: full regions"
    if kb_s >= 150:
        return "adopt C with dirty rectangles only"
    return ("MicroPython CDC is the bottleneck: add a C/viper module, "
            "or stay device-side with clips in flash")


def summarize(durations_s, nbytes, failures):
    ordered = sorted(durations_s)
    n = len(ordered)
    p95 = ordered[(95 * n + 99) // 100 - 1]
    mean = sum(ordered) / n
    return {"frames": n, "failures": failures,
            "ms_mean": mean * 1000, "ms_p95": p95 * 1000,
            "kb_s_mean": nbytes / mean / 1000, "kb_s_p95_worst": nbytes / p95 / 1000}


def write_all(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def read_line(fd, timeout):
    end, buf = time.monotonic() + timeout, b""
    while not buf.endswith(b"\n"):
        left = end - time.monotonic()
        if left <= 0 or not select.select([fd], [], [], left)[0]:
            return None
        buf += os.read(fd, 256)
    return buf


def run_one(fd, nbytes, show):
    data = payload(nbytes)
    expect = binascii.crc32(data)
    durations, failures = [], 0
    for _ in range(FRAMES):
        start = time.monotonic()
        termios.tcflush(fd, termios.TCIFLUSH)  # drop stale replies from earlier frames
        write_all(fd, f"BENCH {nbytes} {show}\n".encode() + data)
        line = read_line(fd, REPLY_TIMEOUT_S)
        elapsed = time.monotonic() - start
        parts = line.split() if line else []
        if len(parts) == 3 and parts[0] == b"OK" and parts[1] == str(expect).encode():
            durations.append(elapsed)
        else:
            failures += 1
    return summarize(durations, nbytes, failures) if durations else None, parts


def main(argv):
    path = argv[1] if len(argv) > 1 else "/dev/cu.usbmodem101"
    fd, saved = open_raw(path)
    try:
        for nbytes in SIZES:
            for show in (0, 1):
                stats, last = run_one(fd, nbytes, show)
                print(f"{nbytes} B show={show}:", stats or "no valid reply", "last reply:", last)
                if stats:
                    print("  ->", decide(stats["kb_s_mean"]))
        write_all(fd, b"BENCH 0 0\n")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
