"""M4 Mac <-> RP2040 USB CDC benchmark. Standard library only.

The device must first be flashed with firmware/rp2040/bench_usb.py as main.py.
Examples:
  python3 tools/bench_usb.py /dev/cu.usbmodem101 --smoke
  python3 tools/bench_usb.py /dev/cu.usbmodem101 --frames 1 --size 28800 --show 0
  python3 tools/bench_usb.py /dev/cu.usbmodem101 --json-out /tmp/buddy-usb.json
  python3 tools/bench_usb.py /dev/cu.usbmodem101 --recovery-test

Mode F (default) measures the bulk-read path but cannot guarantee automatic
recovery from a partial 256-byte read in MicroPython 1.22.2. Mode S reads one
byte at a time and supports bounded-stall testing, not throughput decisions.
"""
import argparse
import binascii
import glob
import json
import os
import secrets
import select
import sys
import termios
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.send_blink import open_raw

SIZES = (28800, 134400)
FRAME_SIZES = (16, 1024) + SIZES
FRAMES = 100
WRITE_TIMEOUT_S = 10.0
REPLY_TIMEOUT_S = 10.0
MAX_REPLY = 256


class BenchmarkError(Exception):
    pass


def payload(n):
    return (bytes(range(256)) * (n // 256 + 1))[:n]


def decide(kb_s):
    if kb_s >= 500:
        return "full regions candidate (verify refresh, p95 and reliability)"
    if kb_s >= 150:
        return "dirty rectangles only candidate (real partial refresh unverified)"
    return ("MicroPython CDC receive path bottleneck candidate: "
            "investigate C/viper or retain device-side rendering")


def _p95(samples):
    ordered = sorted(samples)
    return ordered[(95 * len(ordered) + 99) // 100 - 1]


def summarize(durations_s, nbytes, failures, cycles_s=None, heaps=None):
    if not durations_s:
        raise ValueError("no completed frames")
    mean = sum(durations_s) / len(durations_s)
    p95 = _p95(durations_s)
    stats = {"frames": len(durations_s), "failures": failures,
             "ms_mean": mean * 1000, "ms_p95": p95 * 1000,
             "kb_s_mean": nbytes / mean / 1000,
             "kb_s_p95_worst": nbytes / p95 / 1000}
    if cycles_s:
        stats["cycle_ms_mean"] = sum(cycles_s) / len(cycles_s) * 1000
        stats["cycle_ms_p95"] = _p95(cycles_s) * 1000
    if heaps:
        stats["heap_min"] = min(heaps)
        stats["heap_max"] = max(heaps)
    return stats


class SerialPort:
    def __init__(self, path):
        self.fd, self.saved = open_raw(path)
        self.pending = bytearray()
        try:
            os.set_blocking(self.fd, False)
            termios.tcflush(self.fd, termios.TCIFLUSH)
        except Exception:
            self.close()
            raise

    def close(self):
        if self.fd is not None:
            try:
                termios.tcsetattr(self.fd, termios.TCSANOW, self.saved)
            except OSError:
                pass  # disconnected ports may not allow attribute restoration
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def write_all(self, data, timeout=WRITE_TIMEOUT_S):
        end = time.monotonic() + timeout
        view = memoryview(data)
        sent = 0
        while sent < len(view):
            remaining = end - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("USB write timed out after %d/%d bytes" % (sent, len(view)))
            if not select.select([], [self.fd], [], remaining)[1]:
                raise TimeoutError("USB write readiness timed out after %d bytes" % sent)
            try:
                n = os.write(self.fd, view[sent:])
            except BlockingIOError:
                continue
            if n > 0:
                sent += n
        return sent

    def read_line(self, timeout=REPLY_TIMEOUT_S):
        end = time.monotonic() + timeout
        while True:
            newline = self.pending.find(b"\n")
            if newline >= 0:
                line = bytes(self.pending[:newline]).rstrip(b"\r")
                del self.pending[:newline + 1]
                return line
            if len(self.pending) > MAX_REPLY:
                raise BenchmarkError("device output exceeded %d bytes without newline" % MAX_REPLY)
            remaining = end - time.monotonic()
            if remaining <= 0 or not select.select([self.fd], [], [], remaining)[0]:
                raise TimeoutError("no complete USB reply within %.1f s" % timeout)
            try:
                chunk = os.read(self.fd, 256)
            except BlockingIOError:
                continue
            if not chunk:
                raise ConnectionError("USB serial port disconnected")
            self.pending.extend(chunk)


def synchronize(link):
    nonce = secrets.token_hex(8)
    link.write_all(("\nSYNC %s\n" % nonce).encode())
    deadline = time.monotonic() + REPLY_TIMEOUT_S
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("no SYNCED reply; is benchmark main.py running?")
        line = link.read_line(remaining)
        if line == ("SYNCED %s" % nonce).encode():
            return nonce
        if line.startswith((b"bench ready;", b"MPY: soft reboot")) or line in (b"", b"ERR header"):
            continue
        raise BenchmarkError("unexpected startup reply: %r" % line)


def parse_ready(line, nonce, seq):
    expected = ("READY %s %d" % (nonce, seq)).encode()
    if line != expected:
        raise BenchmarkError("expected %r, got %r" % (expected, line))


def parse_result(line, nonce, seq, expected_crc):
    parts = line.split()
    if (len(parts) == 5 and parts[0] == b"OK"
            and parts[1] == nonce.encode() and parts[2] == str(seq).encode()):
        try:
            crc, heap = int(parts[3]), int(parts[4])
        except ValueError:
            raise BenchmarkError("noninteger CRC/heap: %r" % line)
        if crc != expected_crc:
            raise BenchmarkError("CRC mismatch: expected %d, got %d" % (expected_crc, crc))
        if heap < 0:
            raise BenchmarkError("invalid heap: %d" % heap)
        return heap
    raise BenchmarkError("unexpected acknowledgement: %r" % line)


def send_frame(link, nonce, seq, nbytes, show, mode):
    data = payload(nbytes)
    began = time.monotonic()
    link.write_all(("BENCH %d %d %d %s\n" % (seq, nbytes, show, mode)).encode())
    parse_ready(link.read_line(), nonce, seq)
    started = time.monotonic()
    link.write_all(data)
    heap = parse_result(link.read_line(), nonce, seq, binascii.crc32(data))
    ended = time.monotonic()
    return ended - started, ended - began, heap


def stop_device(link):
    """Use the spec's BENCH 0 0 terminator and confirm cleanup completed."""
    link.write_all(b"BENCH 0 0\n")
    reply = link.read_line()
    if reply != b"STOPPED":
        raise BenchmarkError("device did not acknowledge shutdown: %r" % reply)


def resolve_port(value):
    if value:
        return value
    choices = sorted(glob.glob("/dev/cu.usbmodem*"))
    if len(choices) != 1:
        raise BenchmarkError("expected one USB modem port, found %d: %s; pass port explicitly" %
                             (len(choices), ", ".join(choices) or "none"))
    return choices[0]


def save_results(path, port, results, complete):
    if not path:
        return
    with open(path, "w", encoding="utf-8") as output:
        json.dump({"port": port, "results": results, "complete": complete,
                   "hardware_validated": False,
                   "note": "Hardware conclusions require inspected board output and recovery evidence"},
                  output, indent=2)
    print("Saved:", path, flush=True)


def recovery_test(link):
    nonce = synchronize(link)
    seq = 0
    link.write_all(b"BENCH 0 1024 0 S\n")
    parse_ready(link.read_line(), nonce, seq)
    link.write_all(payload(1024)[:17])
    expected = ("ERR %s %d stall 17" % (nonce, seq)).encode()
    reply = link.read_line(3.0)
    if reply != expected:
        raise BenchmarkError("expected bounded-stall reply %r, got %r" % (expected, reply))
    nonce = synchronize(link)
    duration, _, heap = send_frame(link, nonce, 1, 16, 0, "S")
    print("SAFE recovery PASS: 17-byte partial frame stalled, resynchronized, then CRC-valid 16-byte frame")
    print("Recovery frame: %.1f ms; free heap: %d B" % (duration * 1000, heap))
    stop_device(link)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", nargs="?", help="serial port (auto-detect if exactly one cu.usbmodem)")
    parser.add_argument("--smoke", action="store_true", help="one 16-byte no-show frame")
    parser.add_argument("--recovery-test", action="store_true", help="SAFE-mode partial-frame recovery")
    parser.add_argument("--frames", type=int, default=FRAMES, help="frames per configuration (default: 100)")
    parser.add_argument("--size", type=int, action="append", choices=FRAME_SIZES,
                        help="test only these sizes (repeatable); default: 28800 and 134400")
    parser.add_argument("--show", choices=("0", "1", "both"), default="both")
    parser.add_argument("--mode", choices=("fast", "safe"), default="fast")
    parser.add_argument("--json-out", help="write successful measurements to this file")
    args = parser.parse_args(argv)
    if not 1 <= args.frames <= 10000:
        parser.error("--frames must be from 1 to 10000")
    if args.smoke and args.recovery_test:
        parser.error("--smoke and --recovery-test are mutually exclusive")
    if args.json_out and args.recovery_test:
        parser.error("--json-out is for throughput measurements only")

    results = []
    try:
        port = resolve_port(args.port)
        with SerialPort(port) as link:
            if args.recovery_test:
                recovery_test(link)
                return 0
            nonce = synchronize(link)
            sizes = (16,) if args.smoke else (args.size or SIZES)
            shows = (0,) if args.smoke else ((0, 1) if args.show == "both" else (int(args.show),))
            frames = 1 if args.smoke else args.frames
            mode = "S" if args.smoke else ("F" if args.mode == "fast" else "S")
            seq = 0
            for nbytes in sizes:
                for show in shows:
                    durations, cycles, heaps = [], [], []
                    for _ in range(frames):
                        try:
                            duration, cycle, heap = send_frame(link, nonce, seq, nbytes, show, mode)
                        except (TimeoutError, BenchmarkError, OSError) as exc:
                            # Do not send more frames on an unknown receiver state.
                            partial = {"size_bytes": nbytes, "show": show, "mode": mode,
                                       "status": "incomplete", "expected_frames": frames,
                                       "attempted_frames": len(durations) + 1,
                                       "completed_frames": len(durations), "failures": 1,
                                       "error": str(exc)}
                            if durations:
                                partial.update(summarize(durations, nbytes, 1, cycles, heaps))
                            results.append(partial)
                            print("INCOMPLETE: %s" % partial, flush=True)
                            save_results(args.json_out, port, results, complete=False)
                            print("STOP. Do not reuse the port until the receiver state is checked.")
                            return 2
                        durations.append(duration)
                        cycles.append(cycle)
                        heaps.append(heap)
                        seq += 1
                    stats = summarize(durations, nbytes, 0, cycles, heaps)
                    record = {"size_bytes": nbytes, "show": show, "mode": mode, **stats}
                    results.append(record)
                    print("%d B show=%d mode=%s: %s" % (nbytes, show, mode, stats), flush=True)
                    if mode == "F":
                        suffix = " (USB receive path only; no LCD refresh)" if not show else " (includes full LCD refresh)"
                        print("  -> provisional:", decide(stats["kb_s_mean"]) + suffix, flush=True)
                    else:
                        print("  -> safe-mode diagnostic only; do not choose streaming architecture", flush=True)
            # Saved before teardown: a lost STOPPED ack must not discard measured frames.
            save_results(args.json_out, port, results, complete=True)
            stop_device(link)
            if args.smoke:
                print("Smoke test PASS (16 bytes, binary including 0x03, CRC matched)")
            else:
                print("Complete: %d successful transfers, 0 frame failures. Recovery is a separate test." %
                      sum(x["frames"] for x in results))
            return 0
    except (TimeoutError, BenchmarkError, ConnectionError, OSError) as exc:
        print("FAIL: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
