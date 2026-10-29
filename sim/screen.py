"""Pixel-exact stand-in for the 456x280 V2 AMOLED landscape view (stdlib only).

Colors quantize through the firmware's RGB565 path and reconstruct with the
same rounding as assets/amoled-preview.html, so sim pixels match what the
browser preview and the panel driver receive.
"""
from __future__ import annotations

from tools.face_asset import rgb565

WIDTH, HEIGHT = 456, 280

_hex_cache: dict[tuple[int, int, int], str] = {}


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

    def rows(self) -> list[list[str]]:
        return self._rows
