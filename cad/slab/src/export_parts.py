import os, build123d as bd
from placement import placement

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "parts")
os.makedirs(out, exist_ok=True)

for i, s in enumerate(placement().shape.solids()):
    name = f"{i:02d}_{s.label or 'part'}"
    print("part", name, round(s.volume, 1))
    bd.export_stl(s, os.path.join(out, f"{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
