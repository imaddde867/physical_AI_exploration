"""Check saved concept envelopes; this does not validate a real mount or motion."""
from pathlib import Path
import sys

from cadgen import read_scene
from cadgen.geometry import overlap_volume

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from common import (HEAD_DEPTH, HEAD_DIAMETER, LID_HEIGHT, LID_THICKNESS,
                    MAC_DEPTH, MAC_WIDTH, REAR_GAP, SCREEN_DIAMETER)


def close(actual, expected):
    assert abs(actual - expected) < 0.001, (actual, expected)


for filename, laptops, pods in (("placement_study", 3, 3),
                                ("retractable_study", 2, 2),
                                ("detachable_study", 2, 2)):
    scene = read_scene(ROOT / "STEP" / f"{filename}.step")
    leaves = [(leaf.label, leaf.shape()) for leaf in scene.leaves()]
    solids = [solid for _, shape in leaves for solid in shape.solids()]
    assert solids and all(s.is_valid and s.volume > 0 for s in solids), filename
    lids = [s for label, s in leaves if label == "reference_lid_assumed"]
    bases = [s for label, s in leaves if label == "reference_base"]
    heads = [s for label, s in leaves if label == "pod_envelope"]
    assert len(lids) == len(bases) == laptops, filename
    assert len(heads) == pods, filename
    for lid in lids:
        size = lid.bounding_box().size
        close(size.X, MAC_WIDTH)
        close(size.Y, LID_THICKNESS)
        close(size.Z, LID_HEIGHT)
    for base in bases:
        close(base.bounding_box().size.X, MAC_WIDTH)
        close(base.bounding_box().size.Y, MAC_DEPTH)
    for label, shape in leaves:
        if not label.startswith("reference_"):
            assert shape.bounding_box().min.Y >= REAR_GAP - 0.001, label
        if label == "screen_placeholder":
            close(shape.bounding_box().size.X, SCREEN_DIAMETER)
        if label == "rear_pad":
            close(shape.bounding_box().min.Y, REAR_GAP)
    for head in heads:
        size = head.bounding_box().size
        close(size.X, HEAD_DIAMETER)
        close(size.Y, HEAD_DEPTH)
        close(size.Z, HEAD_DIAMETER)
        for lid in lids:
            assert all(overlap_volume(a, b) < 0.001
                       for a in head.solids() for b in lid.solids()), filename
    if filename == "placement_study":
        for head, lid, side in zip(heads, lids, ("left", "right", "top")):
            h, l = head.bounding_box(), lid.bounding_box()
            gap = {"left": l.min.X - h.max.X,
                   "right": h.min.X - l.max.X,
                   "top": h.min.Z - l.max.Z}[side]
            close(gap, 3)
    if filename == "retractable_study":
        h, l = heads[1].bounding_box(), lids[1].bounding_box()
        assert l.min.X < h.min.X < h.max.X < l.max.X
        assert l.min.Z < h.min.Z < h.max.Z < l.max.Z
        close(heads[0].volume, heads[1].volume)
    print(f"{filename}: {len(solids)} valid positive-volume solids; "
          f"{laptops} reference laptops, {pods} pods; scale and rear envelope OK")
