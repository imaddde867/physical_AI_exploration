"""Stdlib indexed-PNG reader and RGB565 quantizer used by the screen simulator."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SIZE = 240


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    da, db, dc = abs(p - a), abs(p - b), abs(p - c)
    if da <= db and da <= dc:
        return a
    return b if db <= dc else c


def indexed_png(source: Path, size: tuple[int, int] = (SIZE, SIZE)) -> tuple[list[tuple[int, int, int]], bytes]:
    """Load a CRC-checked, 8-bit indexed PNG (default 240x240), no Pillow dependency."""
    width, height = size
    data = source.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Not a PNG")
    off = len(PNG_SIGNATURE)
    colors: list[tuple[int, int, int]] = []
    compressed: list[bytes] = []
    header_found = end_found = False
    while off + 12 <= len(data):
        count = struct.unpack_from(">I", data, off)[0]
        kind = data[off + 4:off + 8]
        end = off + 12 + count
        if end > len(data):
            raise ValueError("Truncated PNG chunk")
        value = data[off + 8:off + 8 + count]
        crc = struct.unpack_from(">I", data, off + 8 + count)[0]
        if zlib.crc32(kind + value) & 0xffffffff != crc:
            raise ValueError("PNG CRC mismatch")
        off = end
        if kind == b"IHDR":
            vals = struct.unpack(">IIBBBBB", value)
            if vals != (width, height, 8, 3, 0, 0, 0):
                raise ValueError(f"Expected {width}x{height} 8-bit indexed, non-interlaced PNG")
            header_found = True
        elif kind == b"PLTE":
            if len(value) % 3 or not (1 <= len(value) // 3 <= 32):
                raise ValueError("Expected 1..32 palette colors")
            colors = [tuple(value[i:i+3]) for i in range(0, len(value), 3)]
        elif kind == b"IDAT":
            compressed.append(value)
        elif kind == b"IEND":
            end_found = True
            break
    if not (header_found and end_found and colors and compressed):
        raise ValueError("PNG missing required data")
    if sum(map(len, compressed)) > width * height * 3 + 64:  # zlib header/checksum + chunk overhead
        raise ValueError("PNG compressed input unexpectedly large")
    decoded = zlib.decompress(b"".join(compressed))
    if len(decoded) != height * (width + 1):
        raise ValueError("Unexpected PNG scanline length")
    previous = bytearray(width)
    rows = []
    for y in range(height):
        filter_id = decoded[y * (width + 1)]
        if filter_id > 4:
            raise ValueError("Unsupported PNG row filter")
        encoded = decoded[y * (width + 1) + 1:(y + 1) * (width + 1)]
        row = bytearray(width)
        for x, byte in enumerate(encoded):
            left = row[x - 1] if x else 0
            top = previous[x]
            upper = previous[x - 1] if x else 0
            correction = (0, left, top, (left + top) // 2, _paeth(left, top, upper))[filter_id]
            row[x] = (byte + correction) & 255
        rows.append(row)
        previous = row
    pixels = b"".join(rows)
    if max(pixels) >= len(colors):
        raise ValueError("PNG palette index out of bounds")
    return colors, pixels


def rgb565(color: tuple[int, int, int]) -> int:
    r, g, b = color
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
