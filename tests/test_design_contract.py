"""Static regression checks: buying/specifications and implementation stay aligned."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DisplayDecisionTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_color_driver_and_pin_mapping(self):
        fw = self.read("firmware/src/main.cpp")
        cfg = self.read("firmware/platformio.ini")
        self.assertIn("#include <Adafruit_GC9A01A.h>", fw)
        self.assertIn("TFT_MOSI = 11", fw)
        self.assertIn("TFT_SCLK = 12", fw)
        self.assertIn("TFT_CS = 10", fw)
        self.assertIn("IMU_SDA = 8", fw)
        self.assertIn("IMU_SCL = 9", fw)
        self.assertIn("init_sent_unverified", fw)
        self.assertIn("adafruit/Adafruit GC9A01A @ 1.2.0", cfg)
        self.assertNotIn("Adafruit_SSD1306", fw + cfg)

    def test_bom_matches_display_choice(self):
        bom = self.read("docs/bom.md")
        shop = self.read("docs/shopping-list.md")
        self.assertIn("GC9A01", bom)
        self.assertIn("GC9A01", shop)
        self.assertIn("40.03", bom)
        self.assertIn("40.03", shop)
        self.assertIn("8.99", shop)
        self.assertIn("pre-soldered", shop)

    def test_concept_art_is_not_misrepresented_as_firmware(self):
        art = self.read('assets/face-preview.svg')
        doc = self.read('docs/character-direction.md')
        readme = self.read('README.md')
        for name in ('NIM', 'LUNE', 'KIP'):
            self.assertIn(name, art)
            self.assertIn(name, doc)
        self.assertIn('not the current firmware output', readme)

    def test_case_is_round_and_user_readme_current(self):
        scad = self.read("cad/desk-buddy.scad")
        readme = self.read("README.md")
        self.assertIn("opening_d = 31.4", scad)
        self.assertIn("front_round_hole", scad)
        self.assertIn("GC9A01", readme)
        self.assertNotIn("I2C SSD1306 OLED", readme)

if __name__ == "__main__":
    unittest.main()
