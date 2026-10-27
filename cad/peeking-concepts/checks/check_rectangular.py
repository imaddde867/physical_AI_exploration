"""Saved CAD checks for form envelopes and a fit coupon, not mount qualification."""
from pathlib import Path
import sys

from cadgen import build123d as bd, read_scene
from cadgen.geometry import overlap_volume

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rectangular_study import ACTIVE_H, ACTIVE_W, CONCEPTS, DEPTH_TARGET, EDGE_GAP


def close(actual, expected):
    assert abs(actual - expected) < 0.001, (actual, expected)


scene = read_scene(ROOT / "STEP/rectangular_study.step")
leaves = [(o.label, o.shape().rotate(bd.Axis.X, 15)) for o in scene.leaves()]
solids = [s for _, shape in leaves for s in shape.solids()]
assert len(solids) == 42 and all(s.is_valid and s.volume > 0 for s in solids)
bodies = [s for label, s in leaves if label == "appearance_envelope"]
lids = [s for label, s in leaves if label == "reference_lid_assumed"]
screens = [s for label, s in leaves if label == "active_area_placeholder"]
assert len(bodies) == len(lids) == len(screens) == 3
for body, lid, screen, (_, width, height, _, _) in zip(bodies, lids, screens, CONCEPTS):
    box = body.bounding_box()
    close(box.size.X, width)
    close(box.size.Y, DEPTH_TARGET)
    close(box.size.Z, height)
    close(box.min.X - lid.bounding_box().max.X, EDGE_GAP)
    size = screen.bounding_box().size
    close(size.X * size.Z, ACTIVE_W * ACTIVE_H)
    assert overlap_volume(body.solids()[0], lid.solids()[0]) < 0.001
for label, shape in leaves:
    if not label.startswith("reference_"):
        assert shape.bounding_box().min.Y >= 1 - 0.001, label
print("rectangular_study: 42 valid solids; matching display areas; 2 mm edge gaps; rear-only envelope")

scene = read_scene(ROOT / "STEP/fit_coupon.step")
(strip_ref,) = scene.resolve("#fit_coupon_strip")
(peg_ref,) = scene.resolve("#test_peg_with_foot")
strip, peg = strip_ref.shape(), peg_ref.shape()
assert len(strip.solids()) == len(peg.solids()) == 1
assert all(s.is_valid and s.volume > 0 for s in (strip, peg))
assert overlap_volume(strip.solids()[0], peg.solids()[0]) < 0.001
close(strip.bounding_box().min.Z, 0)
close(peg.bounding_box().min.Z, 0)
close(strip.volume, 45 * 15 * 3 - sum((4 + c) * (8 + c) * 3 for c in (0.2, 0.4, 0.6)))
close(peg.volume, 8 * 12 * 2 + 4 * 8 * 6)
(top,) = [f for f in strip.faces() if abs(f.center().Z - 3) < 0.001]
holes = sorted(top.inner_wires(), key=lambda w: w.center().X)
assert len(holes) == 3
for hole, clearance in zip(holes, (0.2, 0.4, 0.6)):
    close(hole.bounding_box().size.X, 4 + clearance)
    close(hole.bounding_box().size.Y, 8 + clearance)
print("fit_coupon: 2 valid separated solids; holes and volumes match; both rest at Z=0")
