"""Validate actual approved screen pixels, without a display or Pillow."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.face_asset import SIZE, indexed_png, encode_runs, decode_runs, generate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/face-idle-240.png"
APPROVED_SHA256 = "32821513663d47fb2b0bb5aea8116cf91d84ef4f29240b7dbd81520884de908c"


class FaceAssetTests(unittest.TestCase):
    def test_source_is_approved_single_face(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), APPROVED_SHA256)

    def test_pixel_encoding_round_trip(self):
        palette, pixels = indexed_png(SOURCE)
        self.assertEqual(len(palette), 32)
        self.assertEqual(len(pixels), SIZE * SIZE)
        tokens = encode_runs(pixels)
        self.assertLess(len(tokens), 16_000)
        self.assertEqual(pixels, decode_runs(tokens))

    def test_generated_header_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "face_asset.h"
            first = generate(SOURCE, output)
            before = output.read_bytes()
            second = generate(SOURCE, output)
            self.assertEqual(first, second)
            self.assertEqual(before, output.read_bytes())
            self.assertIn(b"kFacePackedRuns", before)

    def test_corrupted_png_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "broken.png"
            blob = bytearray(SOURCE.read_bytes())
            blob[100] ^= 1
            dest.write_bytes(blob)
            with self.assertRaises(ValueError):
                indexed_png(dest)


if __name__ == "__main__":
    unittest.main()
