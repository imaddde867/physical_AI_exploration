"""Solid-level regression guards. Run with build123d installed (see CAD CI job)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cad/slab/src"))
import params as P  # noqa: E402

try:
    import build123d as bd
    from mount import build, box
except ImportError:
    bd = None


@unittest.skipUnless(bd is not None, "build123d not installed; dedicated CAD CI runs solid tests")
class MountSolidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if bd is None:
            return
        cls.parts, cls.report = build()
        cls.by_label = {s.label: s for s in cls.parts if s.label != "magnet"}

    def assert_no_overlap(self, left, right, message=""):
        intersection = left & right
        self.assertLess(intersection.volume, 1e-5, message)

    def test_all_four_mount_contacts_clear_of_steel_and_each_other(self):
        steel = self.by_label["mount_plate"]
        contacts = [self.by_label[f"mount_contact_{n}"] for n in P.POGO_NAMES]
        self.assertEqual(len(contacts), 4)
        for i, one in enumerate(contacts):
            self.assert_no_overlap(steel, one, "steel touches contact " + P.POGO_NAMES[i])
            for other in contacts[i+1:]:
                self.assert_no_overlap(one, other, "two USB contacts touch")

    def test_dielectric_core_is_through_plate_and_back_retained(self):
        steel = self.by_label["mount_plate"]
        carrier = self.by_label["insulating_contact_carrier"]
        ix0, ix1, iz0, iz1 = P.carrier_outline()
        through_probe = box(ix0, ix1, P.ADH_T+0.05, P.ADH_T+P.PLATE_T-0.05,
                            iz0, iz1, "probe", "#000")
        self.assert_no_overlap(steel, carrier)
        self.assert_no_overlap(steel, through_probe, "connector steel window not through-cut")
        self.assertAlmostEqual(carrier.bounding_box().max.Y,
                               P.ADH_T+P.PLATE_T+P.CARRIER_FLANGE_T, places=5)
        for n in P.POGO_NAMES:
            self.assert_no_overlap(carrier, self.by_label[f"mount_contact_{n}"],
                                   "contact touching solid dielectric instead of an opened recess")

    def test_mating_contacts_are_isolated_from_shell_and_steel(self):
        for n in P.POGO_NAMES:
            tip = self.by_label[f"screen_contact_{n}"]
            pad = self.by_label[f"mount_contact_{n}"]
            self.assert_no_overlap(tip, self.by_label["screen_shell"])
            self.assert_no_overlap(tip, self.by_label["mount_plate"])
            self.assert_no_overlap(tip, pad)  # meet on plane, do not occupy the same volume
            self.assertAlmostEqual(tip.bounding_box().max.Y, P.ADH_T, places=5)
            self.assertAlmostEqual(pad.bounding_box().min.Y, P.ADH_T, places=5)

    def test_cable_and_grommet_clear_of_steel_lid_and_adhesive(self):
        steel = self.by_label["mount_plate"]
        cable = self.by_label["cable"]
        sleeve = self.by_label["cable_insulating_grommet"]
        tape = self.by_label["mount_adhesive"]
        lid = box(-P.LID_W/2, P.LID_W/2, -P.LID_T, 0,
                  P.BASE_T, P.BASE_T+P.LID_H, "lid", "#aaa")
        for item in (cable, sleeve):
            self.assert_no_overlap(item, steel, "cable/sleeve intersects conductive plate")
            self.assert_no_overlap(item, tape, "cable/sleeve intersects mounting tape")
            self.assert_no_overlap(item, lid, "cable/sleeve intersects lid slab")
        self.assert_no_overlap(cable, sleeve, "sleeve bore too narrow for cable")

    def test_actual_screen_glass_faces_and_stack_height(self):
        shell = self.by_label["screen_shell"]
        glass = self.by_label["screen_glass"]
        self.assert_no_overlap(shell, glass, "glass not properly recessed")
        self.assertAlmostEqual(glass.bounding_box().min.Y, -P.LID_T, places=5)
        self.assertAlmostEqual(shell.bounding_box().min.Y, -P.LID_T, places=5)
        self.assertAlmostEqual(shell.bounding_box().max.Y, P.ADH_T, places=5)
        self.assertAlmostEqual(shell.bounding_box().max.Y-glass.bounding_box().min.Y,
                               P.SCREEN_T, places=5)
        stack = self.by_label["insulating_contact_carrier"].bounding_box().max.Y - glass.bounding_box().min.Y
        self.assertLessEqual(stack, P.TARGET_STACK_T+1e-6)

    def test_dynamic_slack_is_explicitly_unverified(self):
        self.assertFalse(self.report["dynamic_hinge_fit_verified"])
        self.assertGreater(self.report["slack_needed_mm"], 0)
        self.assertGreater(self.report["length_mm"], 0)


if __name__ == "__main__":
    unittest.main()
