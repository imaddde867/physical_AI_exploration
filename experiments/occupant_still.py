"""Approved Occupant checkpoint, without animation."""
import struct
from pathlib import Path

from sim.screen import HEIGHT, WIDTH

data = Path(__file__).with_name("assets").joinpath("occupant.rgb565").read_bytes()
if len(data) != WIDTH * HEIGHT * 2:
    raise ValueError("Occupant asset must be one 240x280 RGB565 frame")
RGB = [(round((v >> 11) * 255 / 31), round(((v >> 5) & 63) * 255 / 63),
        round((v & 31) * 255 / 31)) for (v,) in struct.iter_unpack("<H", data)]
ROWS = [["#%02x%02x%02x" % color for color in RGB[y * WIDTH:(y + 1) * WIDTH]]
        for y in range(HEIGHT)]


def update(screen, t_ms):
    for target, source in zip(screen.rows(), ROWS):
        target[:] = source
