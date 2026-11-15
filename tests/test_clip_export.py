import random
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from animation.clip_export import (dither565, decode_clip, encode_clip, hold_noise, load_frames, tone, tone_luts,
                                   read_png)

W, H = 40, 30


def write_png(path, rgb, w=W, h=H, filter_type=0):
    """Minimal RGB PNG writer; filter_type 0 or 1 (Sub) exercises the unfilter."""
    rows = bytearray()
    for y in range(h):
        line = rgb[y * w * 3:(y + 1) * w * 3]
        if filter_type == 1:
            line = bytes((line[i] - (line[i - 3] if i >= 3 else 0)) & 255 for i in range(len(line)))
        rows += bytes([filter_type]) + line

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b""))


def write_rgba_png(path, rgba, w, h):
    """RGBA PNG using every filter type (0-4) on consecutive rows, like Blender's output."""
    stride, rows, prev = w * 4, bytearray(), bytes(w * 4)
    for y in range(h):
        line, ft = rgba[y * stride:(y + 1) * stride], y % 5
        out = bytearray()
        for i in range(stride):
            a = line[i - 4] if i >= 4 else 0
            b = prev[i]
            c = prev[i - 4] if i >= 4 else 0
            if ft == 0:
                pred = 0
            elif ft == 1:
                pred = a
            elif ft == 2:
                pred = b
            elif ft == 3:
                pred = (a + b) // 2
            else:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
            out.append((line[i] - pred) & 255)
        rows += bytes([ft]) + out
        prev = line

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b""))


def synthetic(seed, n=6):
    """Black background with a moving noisy blob, so frames differ and loop."""
    rnd = random.Random(seed)
    frames = []
    for k in range(n):
        px = bytearray(W * H * 3)
        for y in range(8, 20):
            for x in range(10 + 3 * k, 24 + 3 * k):
                i = (y * W + x) * 3
                px[i:i + 3] = bytes(rnd.randrange(256) for _ in range(3))
        frames.append(bytes(px))
    return frames


class ClipExportTests(unittest.TestCase):
    def test_black_stays_exactly_zero(self):
        self.assertEqual(dither565(W, H, bytes(W * H * 3)), bytes(W * H * 2))

    def test_rgba_png_with_all_filters_decodes_exactly(self):
        rnd = random.Random(7)
        w, h = 13, 11
        rgba = bytes(rnd.randrange(256) for _ in range(w * h * 4))
        with tempfile.TemporaryDirectory() as d:
            write_rgba_png(Path(d) / "a.png", rgba, w, h)
            rw, rh, rgb = read_png(Path(d) / "a.png")
        want = bytearray(rgba)
        del want[3::4]
        self.assertEqual((rw, rh, rgb), (w, h, bytes(want)))

    def test_near_black_becomes_exact_black(self):
        self.assertEqual(dither565(2, 1, bytes([3, 2, 1, 3, 3, 3])), bytes(4))

    def test_roundtrip_reproduces_dithered_frames_and_loop_wrap(self):
        with tempfile.TemporaryDirectory() as d:
            for k, px in enumerate(synthetic(1)):
                write_png(Path(d) / f"frame-{k:04d}.png", px, filter_type=k % 2)
            frames, size = load_frames(d, black=0, gamma=(1, 1, 1), saturation=1)  # identity tone curve
            self.assertEqual(size, (W, H))
            want = [dither565(W, H, px) for px in synthetic(1)]
            self.assertEqual(frames, want)  # PNG decode incl. Sub filter is exact
            blob, _ = encode_clip(frames, W, H, 24)
            w, h, fps, got = decode_clip(blob)
            self.assertEqual((w, h, fps), (W, H, 24))
            self.assertEqual(got, want + [want[0]])  # last delta wraps to frame 0

    def test_small_noise_is_held_but_real_change_passes(self):
        base = bytes([100, 150, 200]) * 4
        noisy = bytes([101, 148, 202]) + bytes([100, 150, 200]) * 3
        moved = bytes([110, 150, 200]) + base[3:]
        self.assertEqual(hold_noise(base, noisy, 3), base)
        self.assertEqual(hold_noise(base, moved, 3), moved)

    def test_brightness_drift_held_only_with_luma_threshold(self):
        base = bytes([100, 100, 100])
        brighter = bytes([112, 112, 112])  # same colour, +12 brightness
        tinted = bytes([112, 100, 100])
        self.assertEqual(hold_noise(base, brighter, 6), brighter)
        self.assertEqual(hold_noise(base, brighter, 6, 14), base)
        self.assertEqual(hold_noise(base, tinted, 6, 14), tinted)

    def test_gap_and_run_over_65535_pixels(self):
        w, h = 300, 300  # 90000 px: first change after a >65535 gap, then a >65535 run
        a = bytes(w * h * 2)
        b = bytearray(a)
        b[70000 * 2:] = b"\x12\x34" * (w * h - 70000)
        blob, _ = encode_clip([a, bytes(b)], w, h, 12)
        self.assertEqual(decode_clip(blob)[3], [a, bytes(b), a])


class ToneAndEdgeTests(unittest.TestCase):
    def test_edge_pixel_going_black_is_never_held(self):
        # dark body pixel -> background black used to be held (ghost trailing a moving edge)
        self.assertEqual(hold_noise(bytes([20, 12, 10]), bytes(3), 6, 14), bytes(3))
        self.assertEqual(hold_noise(bytes(3), bytes([20, 12, 10]), 6, 14), bytes([20, 12, 10]))

    def test_tone_curve_gives_true_black_and_keeps_red_over_green(self):
        out = tone(bytes([8, 8, 8, 200, 200, 200]), tone_luts())
        self.assertEqual(out[:3], bytes(3))
        self.assertGreater(out[3], out[4])


if __name__ == "__main__":
    unittest.main()
