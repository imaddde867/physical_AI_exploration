import os, build123d as bd
from placement import placement

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "parts")
os.makedirs(out, exist_ok=True)

def walk(n, depth=0):
    if n.children:
        for c in n.children:
            yield from walk(c, depth + 1)
    else:
        yield n

names = ['lid','deck','pod_shell','pod_glass','arm','clip']
for i, s in enumerate(placement().shape.solids()):
    s.label = names[i]
    print("leaf", repr(s.label), s.volume)
    bd.export_stl(s, os.path.join(out, f"{s.label}.stl"), tolerance=0.02, angular_tolerance=0.1)
