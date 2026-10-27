"""Static imported-CAD overlap checks; no physical-fit or closest-clearance claim."""
from pathlib import Path
from cadgen import read_scene
from cadgen.geometry import overlap_volume

ROOT = Path(__file__).resolve().parents[1]
scene = read_scene(ROOT / "STEP/packaging_study.step")
(board_ref,) = scene.resolve("#vendor_board_no_headers")
(shell_ref,) = scene.resolve("#case_front_shell")
(cover_ref,) = scene.resolve("#separate_back_cover")
board = board_ref.shape()
shell, cover = shell_ref.shape(), cover_ref.shape()
assert len(list(scene.leaves())) == 263
assert shell.is_valid and cover.is_valid
assert shell.volume > 0 and cover.volume > 0
size = board.bounding_box().size
assert all(abs(a - b) < 0.001 for a, b in zip(size, (29.12, 9.6, 44.2)))
count = 0
for component in board.solids():
    for case in (shell, cover):
        assert overlap_volume(component, case.solids()[0]) < 0.001
        count += 1
assert count == 522, count
assert overlap_volume(shell.solids()[0], cover.solids()[0]) < 0.001
print(f"packaging_study: {count} board/case comparisons; no positive overlap above 0.001 mm^3")
print("Limits: vendor revision/header assumptions; no retention, thermal, cable or lid-fit proof")
