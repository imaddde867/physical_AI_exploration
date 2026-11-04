"""800x600 concept display simulator (stdlib only); the final panel is not selected.

Colors quantize to RGB565 and reconstruct with round(), so sim pixels match
what a 16-bit panel driver receives.
"""
from __future__ import annotations

import math

WIDTH, HEIGHT = 800, 600

_hex_cache: dict[tuple[int, int, int], str] = {}


def rgb565(color: tuple[int, int, int]) -> int:
    r, g, b = color
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _hex(rgb: tuple[int, int, int]) -> str:
    if rgb not in _hex_cache:
        v = rgb565(rgb)
        _hex_cache[rgb] = "#%02x%02x%02x" % (round((v >> 11) * 255 / 31),
                                             round(((v >> 5) & 63) * 255 / 63),
                                             round((v & 31) * 255 / 31))
    return _hex_cache[rgb]


class Screen:
    def __init__(self) -> None:
        self._rows = [["#000000"] * WIDTH for _ in range(HEIGHT)]

    def set_pixel(self, x: int, y: int, rgb: tuple[int, int, int]) -> None:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self._rows[y][x] = _hex(rgb)

    def fill_rect(self, x: int, y: int, w: int, h: int, rgb: tuple[int, int, int]) -> None:
        if w <= 0 or h <= 0:
            return
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, WIDTH), min(y + h, HEIGHT)
        if x0 >= x1 or y0 >= y1:
            return
        color = _hex(rgb)
        for row in self._rows[y0:y1]:
            row[x0:x1] = [color] * (x1 - x0)

    def clear(self, rgb: tuple[int, int, int]) -> None:
        self.fill_rect(0, 0, WIDTH, HEIGHT, rgb)

    def fill_circle(self, cx: int, cy: int, r: int, rgb: tuple[int, int, int]) -> None:
        for dy in range(-r, r + 1):
            half = int(math.sqrt(r * r - dy * dy) + 0.5)
            self.fill_rect(cx - half, cy + dy, 2 * half + 1, 1, rgb)

    def rows(self) -> list[list[str]]:
        return self._rows
