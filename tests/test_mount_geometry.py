"""Nominal solid regressions; executed with build123d in the dedicated CAD CI job.

These checks prove static B-Rep geometry ONLY, not toleranced production fits.
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cad/slab/src"))
import params as P  # noqa: E402

try:
    import build123d as bd
    from mount import build, box, cyl_y
except ImportError:
    bd = None


@unittest.skipUnless(bd is not None, "build123d absent; CAD CI explicitly imports it")
class MountSolidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.report = build()
        cls.by_label = {part.label: part for part in cls.parts}
        cls.magnets = [p for p in cls.parts if p.label == "magnet"]
        cls.bonds = [p for p in cls.parts if p.label == "magnet_bond"]

    def assert_clear(self, a, b, minimum=0.0, description=""):
        self.assertLess((a & b).volume, 1e-5, "overlap: " + description)
        self.assertGreaterEqual(a.distance_to(b) + 1e-4, minimum,
                                "zero distance / inadequate gap: " + description)

    def test_conductive_contact_separations_are_nonzero(self):
        plate = self.by_label["mount_plate"]
        pads = [self.by_label[f"mount_contact_{n}"] for n in P.POGO_NAMES]
        shell = self.by_label["screen_shell"]
        for i, pad in enumerate(pads):
            self.assert_clear(pad, plate, 1.0, f"pad {P.POGO_NAMES[i]} / steel")
            for other in pads[i + 1:]:
                self.assert_clear(pad, other, 0.60, "neighboring conductors")
        for n in P.POGO_NAMES:
            pogo = self.by_label[f"screen_contact_{n}"]
            self.assert_clear(pogo, shell, 0.18, f"{n} / aluminum housing")
            self.assert_clear(pogo, plate, 0.40, f"{n} / steel")
            self.assert_clear(pogo, self.by_label["mount_adhesive"], 0.40,
                              f"{n} / permanent mount region")
            for other in P.POGO_NAMES:
                if other != n:
                    self.assert_clear(pogo, self.by_label[f"mount_contact_{other}"],
                                      0.80, "wrong mating contact")

    def test_well_subtraction_leaves_full_polymer_wall(self):
        carrier = self.by_label["insulating_contact_carrier"]
        ix0, ix1, iz0, iz1 = P.carrier_outline()
        r = P.POGO_PAD/2 + P.PAD_WELL_CLEARANCE
        face = P.pad_face_y()
        y0, y1 = face+0.02, face+0.12
        xs = P.contact_x_positions()
        # This tests the actual post-boolean solid, not a pad-edge parameter.
        wall_probes = [
            box(ix0, xs[0]-r, y0, y1, P.screen_z_center()-0.25,
                P.screen_z_center()+0.25, "left_wall", "#fff"),
            box(xs[-1]+r, ix1, y0, y1, P.screen_z_center()-0.25,
                P.screen_z_center()+0.25, "right_wall", "#fff"),
            box(xs[1]-0.25, xs[1]+0.25, y0, y1, iz0,
                P.screen_z_center()-r, "lower_wall", "#fff"),
            box(xs[1]-0.25, xs[1]+0.25, y0, y1,
                P.screen_z_center()+r, iz1, "upper_wall", "#fff")]
        for probe in wall_probes:
            self.assertGreaterEqual(probe.bounding_box().size.X *
                                    probe.bounding_box().size.Z, 0.45)
            self.assertAlmostEqual((carrier & probe).volume, probe.volume, delta=0.0005)
        for px in xs:
            well = box(px-r, px+r, y0, y1,
                       P.screen_z_center()-r, P.screen_z_center()+r, "well", "#fff")
            self.assertLess((carrier & well).volume, 1e-6)
        self.assertGreaterEqual(xs[1]-xs[0]-2*r, 0.60-1e-8)

    def test_carrier_is_captured_on_both_faces(self):
        carrier, steel = self.by_label["insulating_contact_carrier"], self.by_label["mount_plate"]
        self.assert_clear(carrier, steel, 0.0, "dielectric / steel")
        ix0, _, iz0, iz1 = P.carrier_outline()
        lip, fit = P.CARRIER_FLANGE_OVERHANG, P.CARRIER_FIT_CLEARANCE
        # Side overhang exists on BOTH sides of the plate (overmold required).
        x0, x1 = ix0-lip+0.05, ix0-fit-0.05
        for y0, y1 in ((P.ADH_T-P.CARRIER_FRONT_FLANGE_T+0.02, P.ADH_T-0.02),
                       (P.ADH_T+P.PLATE_T+0.02,
                        P.ADH_T+P.PLATE_T+P.CARRIER_FLANGE_T-0.02)):
            probe = box(x0, x1, y0, y1, iz0+0.3, iz1-0.3, "shoulder", "#fff")
            self.assertAlmostEqual((carrier & probe).volume, probe.volume, delta=0.0005)
        self.assertAlmostEqual(carrier.bounding_box().min.Y,
                               P.ADH_T-P.CARRIER_FRONT_FLANGE_T, places=4)
        self.assertAlmostEqual(carrier.bounding_box().max.Y,
                               P.ADH_T+P.PLATE_T+P.CARRIER_FLANGE_T, places=4)
        self.assert_clear(carrier, self.by_label["screen_shell"], 0.04,
                          "front shoulder / screen relief")

    def test_asymmetric_alignment_and_steel_holes(self):
        plate, shell = self.by_label["mount_plate"], self.by_label["screen_shell"]
        p0, p1 = P.alignment_positions()
        self.assertGreater(math.dist(p0, p1), 30)
        self.assertGreater(math.dist((2*P.screen_x_center()-p0[0],
                                      2*P.screen_z_center()-p0[1]), p1),
                           P.ALIGN_HOLE_D)
        for x, z in (p0, p1):
            dowel = cyl_y(x, z, P.ALIGN_D, P.ADH_T+0.05,
                          P.ADH_T+P.ALIGN_PROJECTION-0.05)
            self.assertAlmostEqual((shell & dowel).volume, dowel.volume, delta=0.001)
            self.assert_clear(plate, dowel, (P.ALIGN_HOLE_D-P.ALIGN_D)/2-0.01,
                              "dowel / steel bore")
        # Clearance limit is a nominal rigid-body bound, NOT a manufacturing tolerance.
        gap = (P.ALIGN_HOLE_D-P.ALIGN_D)/2
        theta = 2*gap / math.dist(p0, p1)
        max_arm = max(math.dist(p0, (x, P.screen_z_center()))
                      for x in P.contact_x_positions())
        possible_drift = gap + theta*max_arm
        self.assertLess(possible_drift + P.POGO_TIP_D/2, P.POGO_PAD/2)
        self.assertGreater(P.POGO_PITCH - P.POGO_PAD/2 -
                           P.POGO_TIP_D/2 - possible_drift, 0.5)

    def test_nominal_pogo_mating_and_insulating_bushings(self):
        self.assertEqual(P.POGO_PART, "Harwin P70-5000045R")
        height = P.pad_face_y()-P.pogo_pcb_y()
        self.assertGreaterEqual(height, P.POGO_WORK_MIN)
        self.assertLessEqual(height, P.POGO_WORK_MAX)
        self.assertAlmostEqual(P.POGO_FREE_H-height, 0.5, places=3)
        for n in P.POGO_NAMES:
            pin = self.by_label[f"screen_contact_{n}"]
            pad = self.by_label[f"mount_contact_{n}"]
            bush = self.by_label[f"contact_insulator_{n}"]
            self.assert_clear(pin, pad, 0, f"mated pair {n}")
            self.assertLess(pin.distance_to(pad), 1e-4)
            self.assertAlmostEqual(pin.bounding_box().max.Y, P.pad_face_y(), places=4)
            self.assert_clear(pin, bush, 0.02, f"spring barrel / insulating bushing")
            self.assert_clear(bush, self.by_label["screen_shell"], 0.02,
                              f"bushing / shell")
            self.assert_clear(bush, self.by_label["insulating_contact_carrier"],
                              0.04, f"bushing / carrier")

    def test_magnet_bondlines_and_clearance(self):
        self.assertEqual(len(self.magnets), 4)
        self.assertEqual(len(self.bonds), 4)
        plate, shell = self.by_label["mount_plate"], self.by_label["screen_shell"]
        for magnet, bond in zip(self.magnets, self.bonds):
            self.assertGreater(bond.volume, 0.1)
            self.assert_clear(magnet, shell, 0.08, "magnet adhesive pocket")
            self.assert_clear(magnet, plate, P.MAGNET_BACK_RECESS-0.01,
                              "magnet set-back / plate")
            self.assertLess(magnet.distance_to(bond), 1e-4)

    def test_grommet_is_snap_captive_and_cable_abraded_nowhere_in_steel(self):
        steel = self.by_label["mount_plate"]
        grommet = self.by_label["captive_cable_grommet"]
        cable = self.by_label["cable"]
        tape = self.by_label["mount_adhesive"]
        self.assertGreater(P.GROMMET_HEAD_D, P.GROMMET_HOLE_D)
        self.assert_clear(steel, grommet, 0.03, "captive grommet / plate")
        self.assert_clear(cable, steel, 0.05, "cable / steel")
        self.assert_clear(cable, grommet, P.CABLE_GROMMET_BORE_CLEARANCE-0.02,
                          "cable / sleeve bore")
        self.assert_clear(grommet, tape, 0, "mushroom heads / tape")
        for ax, az in P.grommet_anchor_positions():
            head = cyl_y(ax, az, P.GROMMET_HEAD_D-0.02, 0.15, 0.34)
            self.assertGreater((grommet & head).volume, 0.01)
            self.assert_clear(head, steel, 0.04, "capture head on opposite steel face")
        lid = box(-P.LID_W/2, P.LID_W/2, -P.LID_T, 0, P.BASE_T,
                  P.BASE_T+P.LID_H, "lid", "#fff")
        for part in (cable, grommet):
            self.assert_clear(part, lid, 0.1, "nominal static lid clearance")

    def test_glass_fit_and_reported_extremities(self):
        shell, glass = self.by_label["screen_shell"], self.by_label["screen_glass"]
        self.assert_clear(shell, glass, 0.019, "glass seat at glass recess back")
        self.assertAlmostEqual(glass.bounding_box().min.Y, -P.LID_T)
        self.assertAlmostEqual(shell.bounding_box().min.Y, -P.LID_T)
        self.assertAlmostEqual(P.ADH_T - glass.bounding_box().min.Y, P.SCREEN_T)
        self.assertAlmostEqual(shell.bounding_box().max.Y, P.ADH_T+P.ALIGN_PROJECTION)
        self.assertAlmostEqual(self.report["screen_body_mm"], 4.9)
        self.assertAlmostEqual(self.report["front_to_carrier_rear_mm"],
                               self.by_label["insulating_contact_carrier"].bounding_box().max.Y
                               - glass.bounding_box().min.Y)
        grommet = self.by_label["captive_cable_grommet"]
        self.assertAlmostEqual(self.report["front_to_grommet_rear_mm"],
                               grommet.bounding_box().max.Y-glass.bounding_box().min.Y)
        self.assertGreater(self.report["front_to_grommet_rear_mm"],
                           self.report["front_to_carrier_rear_mm"])

    def test_dynamic_cable_remains_a_hardware_blocker(self):
        self.assertFalse(self.report["dynamic_hinge_fit_verified"])
        self.assertGreater(self.report["nominal_proxy_deficit_mm"], 0)


if __name__ == "__main__":
    unittest.main()
