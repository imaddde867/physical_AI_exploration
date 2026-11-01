import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cad/slab/src"))
import params as P  # noqa: E402


class SlabParamsTests(unittest.TestCase):
    def test_glass_flush_with_lid_front(self):
        self.assertAlmostEqual(P.SCREEN_T, P.LID_T + P.ADH_T)

    def test_stack_within_target(self):
        self.assertLessEqual(P.SCREEN_T + P.PLATE_T, P.TARGET_STACK_T)

    def test_plate_under_screen_and_bonded_to_lid(self):
        x0, x1 = P.plate_x_range()
        self.assertEqual(P.LID_W / 2 - x0, P.PLATE_BOND_W)
        self.assertLess(x1, P.screen_x_center() + P.W / 2)

    def test_magnets_and_pads_fit_on_plate(self):
        x0, x1 = P.plate_x_range()
        xc = P.screen_x_center()
        self.assertLess(xc + P.MAGNET_DX + P.MAGNET_D / 2, x1)
        self.assertLess(P.MAGNET_DZ + P.MAGNET_D / 2, P.PLATE_H / 2)
        self.assertLess(1.5 * P.POGO_PITCH + P.POGO_PAD / 2, P.MAGNET_DX - P.MAGNET_D / 2)
        self.assertGreater(P.MAGNET_POCKET, P.MAGNET_T)

    def test_cable_route(self):
        xe, xs, xo = P.cable_x()
        x0, _ = P.plate_x_range()
        self.assertGreater(xe, x0)                      # leaves the plate inside the bonded strip
        self.assertGreaterEqual(P.CABLE_ARC_R, P.MIN_BEND_R)
        self.assertLess(xo, P.LID_W / 2 + P.PLUG_L)     # meets the plug body
        self.assertGreater(P.slack_needed(), 0)


if __name__ == "__main__":
    unittest.main()
