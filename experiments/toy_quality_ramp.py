"""Color/pixel-density showcase for the 456x280 RGB565 screen.

Cycles 4 static patterns every 3s: hue sweep, 2D hue x brightness ramp,
saturation/value ramp, 1px checkerboard. Only re-renders on pattern change.
"""
from sim import screen as scr


def _hue(h_deg, v):
    """RGB from hue (0-360) scaled by brightness v in 0..1."""
    h = (h_deg % 360) / 60.0
    i = int(h)
    f = h - i
    p, q = 1 - f, f
    if i == 0:   r, g, b = 1, q, 0
    elif i == 1: r, g, b = p, 1, 0
    elif i == 2: r, g, b = 0, 1, q
    elif i == 3: r, g, b,  = 0, p, 1
    elif i == 4: r, g, b = q, 0, 1
    else:        r, g, b = 1, 0, p
    return (round(255 * r * v), round(255 * g * v), round(255 * b * v))


def _hue_sweep(s):
    for x in range(scr.WIDTH):
        s.fill_rect(x, 0, 1, scr.HEIGHT, _hue(x * 360 / scr.WIDTH, 1.0))


def _hue_ramp(s):
    mid = scr.HEIGHT // 2
    for x in range(scr.WIDTH):
        h = x * 360 / scr.WIDTH
        s.fill_rect(x, 0, 1, mid, _hue(h, 1.0))
        # diagonal brightness falloff exposes RGB565 quantization banding
        s.fill_rect(x, mid, 1, scr.HEIGHT - mid, _hue(h, 1.0 - x / (scr.WIDTH - 1)))


def _sat_value(s):
    # left 2/3: grayscale 0->255 by column; right: pure red fading down
    band = scr.WIDTH - 120
    for x in range(band):
        v = round(255 * x / (band - 1))
        s.fill_rect(x, 0, 1, scr.HEIGHT, (v, v, v))
    for y in range(scr.HEIGHT):
        s.fill_rect(band, y, 120, 1, (255 - y * 255 // (scr.HEIGHT - 1), 0, 0))


def _checker(s):
    on = "#ffffff"
    for row_i, row in enumerate(s.rows()):
        row[:] = [on if (x + row_i) % 2 == 0 else "#000000" for x in range(scr.WIDTH)]
    # 1px grid lines for line sharpness
    for g in range(0, scr.WIDTH, scr.WIDTH // 4):
        s.fill_rect(g, 0, 1, scr.HEIGHT, (255, 0, 0))
    for g in range(0, scr.HEIGHT, scr.HEIGHT // 4):
        s.fill_rect(0, g, scr.WIDTH, 1, (0, 0, 255))


_PATTERNS = (_hue_sweep, _hue_ramp, _sat_value, _checker)


def update(screen, t_ms) -> None:
    pat = int(t_ms // 3000) % len(_PATTERNS)
    if pat != getattr(update, "_last", -1):
        update._last = pat
        screen.clear((0, 0, 0))
        _PATTERNS[pat](screen)
