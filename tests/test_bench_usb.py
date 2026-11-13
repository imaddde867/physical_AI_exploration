import binascii
import io
import os
try:
    import pty
except ImportError:
    pty = None
import select
import threading
import time
import unittest
from unittest.mock import patch

from firmware.rp2040 import bench_usb as device
from tools import bench_usb as host


class BenchHelpers(unittest.TestCase):
    def test_payload_has_every_byte_including_ctrl_c_and_newline(self):
        p = host.payload(1000)
        self.assertEqual(len(p), 1000)
        self.assertTrue({0x03, 0x0A, 0x00, 0xFF} <= set(p))

    def test_summarize(self):
        s = host.summarize([0.1] * 19 + [0.3], 28800, failures=1)
        self.assertEqual((s["frames"], s["failures"]), (20, 1))
        self.assertAlmostEqual(s["ms_mean"], 110.0)
        self.assertAlmostEqual(s["ms_p95"], 100.0)
        self.assertAlmostEqual(s["kb_s_mean"], 28.8 / 0.11, places=1)
        self.assertAlmostEqual(s["kb_s_p95_worst"], 28.8 / 0.1, places=1)

    def test_extra_stats(self):
        s = host.summarize([.1, .2], 28800, 0, [.12, .24], [87024, 85000])
        self.assertEqual((s['heap_min'], s['heap_max']), (85000, 87024))
        self.assertAlmostEqual(s['cycle_ms_mean'], 180)

    def test_decision_rule_thresholds(self):
        self.assertIn("full-region", host.decide(500))
        self.assertIn("dirty-rectangle", host.decide(499.9))
        self.assertIn("dirty-rectangle", host.decide(150))
        self.assertIn("device-side", host.decide(149.9))

    def test_host_rejects_bad_ack_and_crc(self):
        nonce = '0123456789abcdef'
        host.parse_ready(b'READY ' + nonce.encode() + b' 7', nonce, 7)
        with self.assertRaises(host.BenchmarkError):
            host.parse_ready(b'READY ' + nonce.encode() + b' 6', nonce, 7)
        self.assertEqual(host.parse_result(b'OK ' + nonce.encode() + b' 7 1234 87024', nonce, 7, 1234), 87024)
        for bad in (b'OK 0123456789abcdef 6 1234 87024',
                    b'OK 0123456789abcdef 7 1235 87024',
                    b'OK 0123456789abcdef 7 abc 87024',
                    b'OK 0123456789abcdef 7 1234 -1',
                    b'not OK'):
            with self.subTest(bad=bad), self.assertRaises(host.BenchmarkError):
                host.parse_result(bad, nonce, 7, 1234)


class FakePoller:
    def __init__(self, stream):
        self.stream = stream
    def poll(self, timeout):
        return [True] if self.stream.tell() < len(self.stream.getbuffer()) else []


class DeviceSafety(unittest.TestCase):
    def test_valid_headers(self):
        self.assertIsNone(device.parse_header(''))
        self.assertEqual(device.parse_header('SYNC 0123456789abcdef'), ('sync', '0123456789abcdef'))
        self.assertEqual(device.parse_header('BENCH 5 134400 1 F'), ('bench', 5, 134400, 1, 'F'))
        self.assertEqual(device.parse_header('BENCH 0 1024 0 S'), ('bench', 0, 1024, 0, 'S'))

    def test_malformed_or_unsafe_header_rejected(self):
        for bad in ('BENCH', 'BENCH 1024 1', 'BENCH 1 999999 1 F',
                    'BENCH 1 28800 2 F', 'BENCH 1 28800 0 invalid',
                    'BENCH abc 16 0 S', 'SYNC not-a-valid-nonce',
                    'BENCH -1 16 0 F', 'REPL'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                device.parse_header(bad)

    def test_empty_header_is_not_a_crash(self):
        data = io.BytesIO(b'\nBENCH 0 16 0 S\n')
        poller = FakePoller(data)
        self.assertEqual(device.read_header(poller, data), '')
        self.assertEqual(device.parse_header(device.read_header(poller, data)),
                         ('bench', 0, 16, 0, 'S'))

    def test_overlong_header_discarded(self):
        data = io.BytesIO(b'X' * 100 + b'\nSYNC 0123456789abcdef\n')
        poller = FakePoller(data)
        self.assertEqual(device.parse_header(device.read_header(poller, data)),
                         ('sync', '0123456789abcdef'))

    def test_bounded_safe_read_recovers_at_byte_boundary(self):
        data = io.BytesIO(b'\x03' + b'U' * 16)
        buf = bytearray(1024)
        ok, got = device.recv_into(buf, 1024, FakePoller(data), data, 'S')
        self.assertFalse(ok)
        self.assertEqual(got, 17)
        self.assertEqual(buf[:17], b'\x03' + b'U' * 16)

    def test_bulk_read_has_full_payload_on_normal_path(self):
        data = io.BytesIO(host.payload(28800))
        buf = bytearray(28800)
        ok, got = device.recv_into(buf, 28800, FakePoller(data), data, 'F')
        self.assertTrue(ok)
        self.assertEqual(got, 28800)
        self.assertEqual(buf, host.payload(28800))


class FakeDevice(threading.Thread):
    """Host transport integration with a PTY, not a substitute for the RP2040."""
    def __init__(self, master):
        super().__init__(daemon=True)
        self.fd = master
        self.session = None
        self.input = bytearray()
        self.pending = None
        self.running = True
        self.frame_count = 0
        self.last_received = time.monotonic()

    def run(self):
        while self.running:
            try:
                if not select.select([self.fd], [], [], .025)[0]:
                    if (self.pending and self.pending[3] == 'S'
                            and 0 < len(self.input) < self.pending[1]
                            and time.monotonic() - self.last_received > .22):
                        seq, n, show, mode = self.pending
                        got = len(self.input)
                        self.input.clear()
                        os.write(self.fd, ('ERR %s %d stall %d\n' %
                                (self.session, seq, got)).encode())
                        self.pending = None
                        self.session = None
                    continue
                data = os.read(self.fd, 65536)
            except OSError:
                return
            if not data:
                return
            self.input.extend(data)
            self.last_received = time.monotonic()
            while True:
                if self.pending:
                    seq, n, show, mode = self.pending
                    if len(self.input) < n:
                        break
                    payload = bytes(self.input[:n])
                    del self.input[:n]
                    os.write(self.fd, ('OK %s %d %d 87024\n' %
                            (self.session, seq, binascii.crc32(payload))).encode())
                    self.pending = None
                    self.frame_count += 1
                elif b'\n' in self.input:
                    end = self.input.index(10)
                    line = bytes(self.input[:end]).decode(errors='replace')
                    del self.input[:end + 1]
                    try:
                        cmd = device.parse_header(line)
                    except ValueError:
                        os.write(self.fd, b'ERR header\n')
                        continue
                    if not cmd:
                        continue
                    if cmd[0] == 'sync':
                        self.session = cmd[1]
                        os.write(self.fd, ('SYNCED %s\n' % self.session).encode())
                    else:
                        _, seq, n, show, mode = cmd
                        os.write(self.fd, ('READY %s %d\n' % (self.session, seq)).encode())
                        self.pending = (seq, n, show, mode)
                else:
                    break


@unittest.skipUnless(pty is not None and hasattr(os, 'openpty'), 'requires Unix pseudo-terminals')
class HostTransport(unittest.TestCase):
    def test_two_binary_frames_over_fake_serial_port(self):
        master, slave = pty.openpty()
        path = os.ttyname(slave)
        board = FakeDevice(master)
        board.start()
        try:
            with host.SerialPort(path) as link:
                nonce = host.synchronize(link)
                d0, _, h0 = host.send_frame(link, nonce, 0, 28800, 0, 'F')
                d1, _, h1 = host.send_frame(link, nonce, 1, 16, 1, 'S')
            self.assertGreater(d0, 0)
            self.assertGreater(d1, 0)
            self.assertEqual((h0, h1), (87024, 87024))
            self.assertEqual(board.frame_count, 2)
        finally:
            board.running = False
            os.close(slave)
            os.close(master)
            board.join(timeout=1)

    def test_safe_recovery_over_fake_serial_port(self):
        master, slave = pty.openpty()
        board = FakeDevice(master)
        board.start()
        try:
            with host.SerialPort(os.ttyname(slave)) as link:
                host.recovery_test(link)
            self.assertEqual(board.frame_count, 1)
        finally:
            board.running = False
            os.close(slave)
            os.close(master)
            board.join(timeout=1)

    def test_missing_ack_times_out(self):
        master, slave = pty.openpty()
        try:
            with host.SerialPort(os.ttyname(slave)) as link:
                with self.assertRaises(TimeoutError):
                    link.read_line(.025)
        finally:
            os.close(slave)
            os.close(master)


if __name__ == '__main__':
    unittest.main()
