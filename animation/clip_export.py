"""PNG sequence -> dithered RGB565 delta clip (Stage 0 of the clip playback plan).

Mac-only, stdlib-only. Pixels are big-endian RGB565, the byte order the LCD
framebuffer holds. Pure black stays exactly 0x0000.

Clip file (little-endian header, all counts u16 unless noted):
  b"CLP1" width height fps nframes
  then nframes + 1 frames: frame 0 is the keyframe (delta against black),
  frame i is the delta from frame i-1, the last frame is the delta from the
  final frame back to frame 0 so the loop wraps with no stale pixels.
  frame = u32 payload_len, then runs: u16 gap, u16 count, count*2 pixel bytes.
  gap is in pixels from the end of the previous run (frame start for the first).
  A run with count 0 is a pure skip, used to cross gaps over 65535 pixels.
"""
import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

MAGIC = b"CLP1"
# Merge runs separated by <= this many unchanged pixels: a new run header (4 B)
# costs more than re-sending the gap (2 B per pixel).
MERGE_GAP = 2
BLACK = 3  # sources with every channel <= this become exact 0x0000 (no dithered glow)
BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def read_png(path):
    """Return (width, height, bytes of RGB) for an 8-bit, non-interlaced PNG."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, header = 8, [], None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat.append(body)
    w, h, depth, ctype, _, _, interlace = header
    channels = {2: 3, 6: 4}.get(ctype)
    if depth != 8 or channels is None or interlace:
        raise ValueError(f"{path}: need 8-bit RGB/RGBA, non-interlaced")
    raw = zlib.decompress(b"".join(idat))
    stride, rgb = w * channels, bytearray()
    prev = bytearray(stride)
    for y in range(h):
        base = y * (stride + 1)
        ft, line = raw[base], bytearray(raw[base + 1:base + 1 + stride])
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + b) & 255
            elif ft == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 255
        prev = line
        px = bytearray(line)  # copy: prev must keep its alpha bytes for the next row's filter
        if channels == 4:
            del px[3::4]
        rgb += px
    return w, h, bytes(rgb)


def dither565(width, height, rgb):
    """Ordered (Bayer 4x4) dither to big-endian RGB565 bytes."""
    out = bytearray(width * height * 2)
    j = 0
    for y in range(height):
        row = BAYER4[y & 3]
        for x in range(width):
            t = row[x & 3]  # 0..15
            r, g, b = rgb[j * 3], rgb[j * 3 + 1], rgb[j * 3 + 2]
            if r <= BLACK and g <= BLACK and b <= BLACK:
                j += 1
                continue
            # add threshold below one quantum step (8 for r/b, 4 for g)
            r = min(31, (r + (t >> 1)) >> 3)
            g = min(63, (g + (t >> 2)) >> 2)
            b = min(31, (b + (t >> 1)) >> 3)
            v = (r << 11) | (g << 5) | b
            out[j * 2] = v >> 8
            out[j * 2 + 1] = v & 255
            j += 1
    return bytes(out)


def delta_runs(prev, cur):
    """Encode cur against prev (equal-length RGB565 byte strings) as a payload."""
    n = len(cur) // 2
    out, end, i = bytearray(), 0, 0
    while i < n:
        if prev[i * 2:i * 2 + 2] == cur[i * 2:i * 2 + 2]:
            i += 1
            continue
        start, last = i, i  # last = index of last changed pixel in this run
        i += 1
        while i < n and i - last <= MERGE_GAP + 1:
            if prev[i * 2:i * 2 + 2] != cur[i * 2:i * 2 + 2]:
                last = i
            i += 1
        gap = start - end
        while gap > 65535:
            out += struct.pack("<HH", 65535, 0)
            gap -= 65535
        count = last - start + 1
        while count > 65535:
            out += struct.pack("<HH", gap, 65535) + cur[start * 2:(start + 65535) * 2]
            gap, start, count = 0, start + 65535, count - 65535
        out += struct.pack("<HH", gap, count) + cur[start * 2:(start + count) * 2]
        end, i = last + 1, last + 1
    return bytes(out)


def encode_clip(frames, width, height, fps):
    black = bytes(width * height * 2)
    blob = bytearray(MAGIC + struct.pack("<HHHH", width, height, fps, len(frames)))
    sizes = []
    for prev, cur in zip([black] + frames, frames + [frames[0]]):
        payload = delta_runs(prev, cur)
        blob += struct.pack("<I", len(payload)) + payload
        sizes.append(len(payload))
    return bytes(blob), sizes


def decode_clip(blob):
    """Host reference decoder: returns (width, height, fps, frames incl. wrap)."""
    if blob[:4] != MAGIC:
        raise ValueError("bad magic")
    w, h, fps, n = struct.unpack("<HHHH", blob[4:12])
    buf, pos, frames = bytearray(w * h * 2), 12, []
    for _ in range(n + 1):
        (size,) = struct.unpack("<I", blob[pos:pos + 4])
        pos += 4
        stop, p = pos + size, 0
        while pos < stop:
            gap, count = struct.unpack("<HH", blob[pos:pos + 4])
            p += gap
            buf[p * 2:(p + count) * 2] = blob[pos + 4:pos + 4 + count * 2]
            p += count
            pos += 4 + count * 2
        frames.append(bytes(buf))
    return w, h, fps, frames


def hold_noise(prev, cur, threshold, luma_threshold=None):
    """Keep prev's value for every pixel that barely changed.

    Blender sampling noise flips ~30% of pixels by 1-2/255 each frame; without
    this the dither turns that into real deltas. Moving shading drifts whole
    areas by 7-20/255, so luma_threshold (default = threshold) can be looser
    than the per-channel colour threshold: a pixel is held when every channel
    moved <= threshold, or its brightness moved <= luma_threshold while its
    colour (r-y, b-y) moved <= threshold.
    """
    if prev is None or cur == prev:
        return cur
    lt = threshold if luma_threshold is None else luma_threshold
    out = bytearray(cur)
    for i in range(0, len(cur), 3):
        r, g, b = cur[i], cur[i + 1], cur[i + 2]
        pr, pg, pb = prev[i], prev[i + 1], prev[i + 2]
        if abs(r - pr) <= threshold and abs(g - pg) <= threshold and abs(b - pb) <= threshold:
            out[i:i + 3] = prev[i:i + 3]
        elif lt > threshold:
            y, py = (2 * r + 5 * g + b) >> 3, (2 * pr + 5 * pg + pb) >> 3
            if abs(y - py) <= lt and abs((r - y) - (pr - py)) <= threshold and abs((b - y) - (pb - py)) <= threshold:
                out[i:i + 3] = prev[i:i + 3]
    return bytes(out)


def load_frames(folder, step=1, threshold=0, luma_threshold=None):
    files = sorted(Path(folder).glob("frame-*.png"))[::step]
    raw, size = [], None
    for f in files:
        w, h, rgb = read_png(f)
        if size not in (None, (w, h)):
            raise ValueError(f"{f}: size changed mid-sequence")
        size = (w, h)
        raw.append(rgb)
    held = None
    for lap in range(2 if threshold else 1):  # lap 2 starts from the end state so the loop wrap is held too
        held_frames = []
        for rgb in raw:
            held = hold_noise(held, rgb, threshold, luma_threshold)
            held_frames.append(held)
    return [dither565(size[0], size[1], r) for r in held_frames], size


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder", type=Path, help="24 fps PNG sequence from render_character.py")
    ap.add_argument("--fps", type=int, choices=(6, 8, 12, 24), required=True)
    ap.add_argument("--threshold", type=int, default=3, help="hold pixels that moved <= this (0-255); 0 disables")
    ap.add_argument("--luma-threshold", type=int, default=None, help="looser brightness-only hold (default = --threshold)")
    ap.add_argument("--output", type=Path, required=True, help="new .clp file")
    a = ap.parse_args()
    frames, (w, h) = load_frames(a.folder, step=24 // a.fps, threshold=a.threshold, luma_threshold=a.luma_threshold)
    blob, sizes = encode_clip(frames, w, h, a.fps)
    if decode_clip(blob)[3] != frames + [frames[0]]:
        sys.exit("decode check failed")
    a.output.write_bytes(blob)
    deltas = sizes[1:]  # exclude the keyframe
    print(json.dumps({
        "clip": a.output.name, "fps": a.fps, "frames": len(frames), "total_bytes": len(blob),
        "keyframe_bytes": sizes[0], "mean_delta_bytes": round(sum(deltas) / len(deltas)),
        "peak_delta_bytes": max(deltas)}))


if __name__ == "__main__":
    main()
