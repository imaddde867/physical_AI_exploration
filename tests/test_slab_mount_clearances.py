"""Dependency-free dimensional checks, run even without a CAD kernel."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cad/slab/src"))
import params as P  # noqa: E402


class MountClearances(unittest.TestCase):
    def test_four_contacts_have_dielectric_walls(self):
        self.assertEqual(len(P.contact_x_positions()), len(P.POGO_NAMES))
        self.assertGreaterEqual(P.PAD_EDGE_INSULATION, 1.0)
        self.assertGreaterEqual(P.POGO_PITCH-P.POGO_PAD-2*P.PAD_WELL_CLEARANCE, 0.5)
        self.assertGreater(P.CARRIER_FIT_CLEARANCE, 0)
        x0, x1, z0, z1 = P.carrier_outline()
        for x in P.contact_x_positions():
            self.assertGreaterEqual(x-P.POGO_PAD/2-x0, P.PAD_EDGE_INSULATION-1e-6)
            self.assertGreaterEqual(x1-(x+P.POGO_PAD/2), P.PAD_EDGE_INSULATION-1e-6)
        self.assertGreaterEqual(P.screen_z_center()-P.POGO_PAD/2-z0, P.PAD_EDGE_INSULATION)
        self.assertGreaterEqual(z1-(P.screen_z_center()+P.POGO_PAD/2), P.PAD_EDGE_INSULATION)

    def test_insert_and_magnets_clear_one_another(self):
        x0, x1, z0, z1 = P.carrier_outline()
        plate0, plate1 = P.plate_x_range()
        bz0, bz1 = P.plate_z_range()
        lip = P.CARRIER_FLANGE_OVERHANG
        self.assertGreater(x0, plate0)
        self.assertLess(x1, plate1)
        self.assertGreater(z0, bz0)
        self.assertLess(z1, bz1)
        self.assertLess(x1+lip, P.screen_x_center()+P.MAGNET_DX-P.MAGNET_D/2)
        self.assertLess(P.POGO_PAD/2+P.PAD_EDGE_INSULATION+lip,
                        P.MAGNET_DZ-P.MAGNET_D/2)
        self.assertLessEqual(P.SCREEN_T+P.PLATE_T+P.CARRIER_FLANGE_T, P.TARGET_STACK_T)

    def test_notch_fits_cable_sleeve_and_exits_bottom_edge(self):
        nx0, nx1, nz0, nz1 = P.cable_notch_bounds()
        plate_bottom, plate_top = P.plate_z_range()
        xe, _, _ = P.cable_x()
        self.assertLess(nz0, plate_bottom)
        self.assertLess(plate_bottom, P.cable_entry_z())
        self.assertLess(P.cable_entry_z(), nz1)
        self.assertLess(nz1, plate_top)
        self.assertAlmostEqual((nx0+nx1)/2, xe)
        self.assertGreaterEqual((nx1-nx0)/2,
                                P.CABLE_D/2+P.CABLE_GROMMET_WALL+P.CABLE_NOTCH_CLEARANCE)
        self.assertGreaterEqual(P.CABLE_Y-(P.CABLE_D/2+P.CABLE_GROMMET_WALL), P.ADH_T)
        self.assertLess(nx1, P.LID_W/2)
        self.assertGreater(nx0, P.plate_x_range()[0])

    def test_outboard_cable_bend_clears_nominal_lid_side(self):
        # Analytic XY distance along the nominal quarter-turn, sampled densely.
        # This is NOT a moving-hinge clearance test.
        _, xs, _ = P.cable_x()
        edge = P.LID_W/2
        for i in range(1001):
            theta = (math.pi/2)*i/1000
            x = xs+P.CABLE_ARC_R*math.sin(theta)
            y = P.CABLE_Y-P.CABLE_ARC_R*(1-math.cos(theta))
            dx = max(0.0, x-edge)
            dy = (max(0.0, y) if y >= 0 else
                  max(0.0, -P.LID_T-y) if y < -P.LID_T else 0.0)
            self.assertGreater(math.hypot(dx, dy), P.CABLE_D/2 + 0.2)

    def test_slack_estimate_is_sensitive_to_unmeasured_hinge(self):
        self.assertGreater(P.slack_needed(angle_deg=150), P.slack_needed(angle_deg=90))
        self.assertNotAlmostEqual(P.slack_needed(hinge_y=-4.5), P.slack_needed(hinge_y=0))
        self.assertGreater(P.slack_needed(), 0)


if __name__ == "__main__":
    unittest.main()
