"""Validate actual approved screen pixels, without a display or Pillow."""
import hashlib
import struct
import zlib
import tempfile
import unittest
from pathlib import Path

from tools.face_asset import SIZE, indexed_png

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/face-idle-240.png"
APPROVED_SHA256 = "32821513663d47fb2b0bb5aea8116cf91d84ef4f29240b7dbd81520884de908c"


class FaceAssetTests(unittest.TestCase):
    def test_source_is_approved_single_face(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), APPROVED_SHA256)

    def test_indexed_png_shape(self):
        palette, pixels = indexed_png(SOURCE)
        self.assertEqual(len(palette), 32)
        self.assertEqual(len(pixels), SIZE * SIZE)

    def test_corrupted_png_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "broken.png"
            blob = bytearray(SOURCE.read_bytes())
            blob[100] ^= 1
            dest.write_bytes(blob)
            with self.assertRaises(ValueError):
                indexed_png(dest)

    def test_one_pixel_png_loads(self):
        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        blob = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 3, 0, 0, 0))
                + chunk(b"PLTE", b"\x10\x20\x30") + chunk(b"IDAT", zlib.compress(b"\x00\x00"))
                + chunk(b"IEND", b""))
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "one.png"
            dest.write_bytes(blob)
            self.assertEqual(indexed_png(dest, (1, 1)), ([(0x10, 0x20, 0x30)], b"\x00"))


if __name__ == "__main__":
    unittest.main()
