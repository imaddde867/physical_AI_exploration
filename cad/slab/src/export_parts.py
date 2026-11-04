import os, build123d as bd
from placement import placement

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "render-parts")
os.makedirs(out, exist_ok=True)

doc = placement()
parts = doc.shape.children
assert len(parts) == 16 and all(s.label for s in parts), "Expected 16 named assembly parts for the preview"
doc.export(os.path.join(out, "..", "current-draft.glb"))

for i, s in enumerate(parts):
    name = f"{i:02d}_{s.label}"
    print("part", name, round(s.volume, 1))
    bd.export_stl(s, os.path.join(out, f"{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
