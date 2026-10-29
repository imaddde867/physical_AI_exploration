import unittest
from sim.screen import Screen, WIDTH, HEIGHT
from tools.face_asset import rgb565

def html_hex(color):
    v = rgb565(color)
    return "#%02x%02x%02x" % (round((v >> 11) * 255 / 31),
                              round(((v >> 5) & 63) * 255 / 63),
                              round((v & 31) * 255 / 31))

class SimScreenTests(unittest.TestCase):
    def test_dimensions_and_blank(self):
        s = Screen()
        self.assertEqual(WIDTH, 456); self.assertEqual(HEIGHT, 280)
        rows = s.rows()
        self.assertEqual(len(rows), 280)
        self.assertEqual(len(rows[0]), 456)
        self.assertEqual(rows[0][0], "#000000")

    def test_quantized_color_matches_html_formula(self):
        s = Screen()
        s.set_pixel(10, 10, (255, 205, 157))
        self.assertEqual(s.rows()[10][10], html_hex((255, 205, 157)))

    def test_set_pixel_clips(self):
        s = Screen()
        s.set_pixel(456, 279, (255, 255, 255))  # off right edge
        s.set_pixel(0, 280, (255, 255, 255))    # off bottom
        s.set_pixel(-3, -3, (255, 255, 255))
        self.assertEqual(s.rows()[279][455], "#000000")

    def test_fill_rect_and_zero_size_noop(self):
        s = Screen()
        s.fill_rect(100, 100, 50, 20, (0, 255, 0))
        r, c = html_hex((0, 255, 0)), s.rows()
        self.assertEqual(c[100][100], r); self.assertEqual(c[119][149], r)
        self.assertEqual(c[99][100], "#000000"); self.assertEqual(c[120][100], "#000000")
        s.fill_rect(5, 5, 0, 5, (255, 255, 255))   # w=0
        s.fill_rect(5, 5, 5, 0, (255, 255, 255))   # h=0
        self.assertEqual(s.rows()[5][5], "#000000")

    def test_clear(self):
        s = Screen()
        s.set_pixel(0, 0, (255, 255, 255)); s.clear((10, 20, 30))
        self.assertEqual(s.rows()[0][0], html_hex((10, 20, 30)))

if __name__ == "__main__":
    unittest.main()
