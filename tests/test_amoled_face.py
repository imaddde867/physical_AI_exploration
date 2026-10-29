"""Software parity: approved composition -> C decoder -> native wire pixels."""
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import unittest

from tools.amoled_face import ROOT, FACES, WIDTH, HEIGHT, compose, generate, native_pixels
from tools.face_asset import rgb565


class AmoledFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.temp.name)
        generate(cls.work, cls.work / 'face_frames.h')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_checked_in_preview_and_asset_are_current(self):
        for name in ('face-idle-456.png', 'amoled-preview.html'):
            self.assertEqual((ROOT / 'assets' / name).read_bytes(), (self.work / name).read_bytes())
        png = (self.work / 'face-idle-456.png').read_bytes()
        self.assertEqual(struct.unpack('>II', png[16:24]), (456, 280))
        # Pixels must leave black margin on every edge, even in a blink.
        for face in FACES:
            for blink in (False, True):
                palette, pixels = compose(face, blink)
                black = palette.index((0, 0, 0))
                edge = pixels[:WIDTH] + pixels[-WIDTH:] + pixels[::WIDTH] + pixels[WIDTH-1::WIDTH]
                self.assertEqual(set(edge), {black})

    def test_html_frames_match_composition(self):
        html = (self.work / 'amoled-preview.html').read_text()
        encoded = json.loads(re.search(r'encoded=(\[.*?\]), palette=', html).group(1))
        for i, face in enumerate(FACES):
            for blink in (False, True):
                packed = base64.b64decode(encoded[i * 2 + blink])
                pixels = b''.join(bytes([p]) * count for count, p in struct.iter_unpack('<HB', packed))
                self.assertEqual(pixels, compose(face, blink)[1])
        self.assertNotIn('https://', html)
        self.assertNotIn('__FRAMES__', html)

    def test_firmware_decoder_wire_rotation_and_blink(self):
        cc = shutil.which('cc')
        if cc is None:
            self.skipTest('C compiler unavailable; run this check in CI')
        shutil.copy(ROOT / 'firmware-v2/include/render_core.h', self.work)
        binary = self.work / 'render'
        subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                        '-I', str(self.work), str(ROOT / 'tools/check_v2_renderer.c'), '-o', str(binary)], check=True)
        for i, face in enumerate(FACES):
            for blink in (False, True):
                palette, pixels = compose(face, blink)
                expected = b''.join(struct.pack('>H', rgb565(palette[p])) for p in native_pixels(pixels))
                result = subprocess.run([binary, str(i * 2 + blink)], capture_output=True, check=True)
                self.assertEqual(result.stdout, expected, (face, blink))
        self.assertEqual(subprocess.run([binary, '12'], capture_output=True).returncode, 1)
        self.assertEqual(subprocess.check_output([binary, 'time']), b'001100110001')

    def test_preview_script_pixels_and_controls(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node unavailable; preview script check needs Node in CI')
        hashes = json.loads(subprocess.check_output([
            node, str(ROOT / 'tools/check_amoled_preview.cjs'), str(self.work / 'amoled-preview.html')]))
        expected = []
        for face in FACES:
            for blink in (False, True):
                palette, pixels = compose(face, blink)
                rgba = bytearray()
                for pixel in pixels:
                    c = rgb565(palette[pixel])
                    rgba.extend((int((c >> 11) * 255 / 31 + .5),
                                 int(((c >> 5) & 63) * 255 / 63 + .5),
                                 int((c & 31) * 255 / 31 + .5), 255))
                expected.append(hashlib.sha256(rgba).hexdigest())
        self.assertEqual(hashes, expected)

    def test_vendor_driver_is_pinned_without_edits(self):
        expected = {
            'esp_lcd_sh8601.c': 'e4754b57e4b39f4cab5d33cebc3965382fbb4315dae2b807ce0c9acb711f1dc0',
            'esp_lcd_sh8601.h': 'f965079ea6224079904f0df804ba65bd57785a75a2f90685752b16cbb876f77c',
        }
        for name, sha in expected.items():
            data = (ROOT / 'firmware-v2/src/vendor' / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha)

    def test_invalid_expression_rejected(self):
        with self.assertRaises(ValueError):
            compose('emoji')
