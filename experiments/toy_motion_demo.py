"""60fps motion demo: scrolling RGB565 gradient, bouncing ball, spinning arc gauge.

Redraws gradient by column each frame (456 fill_rects, C-speed row slices).
"""
import math

from sim.screen import HEIGHT, WIDTH


def arc_px(cx, cy, r, a0, a1, step_deg=2.0):
    out = []
    a = a0
    while a <= a1:
        out.append((cx + r * math.cos(math.radians(a)),
                    cy + r * math.sin(math.radians(a))))
        a += step_deg
    return out


def update(screen, t_ms) -> None:
    # scrolling hue gradient (quantization banding visible while moving)
    shift = t_ms * 0.08
    scale = 360 / WIDTH
    for x in range(WIDTH):
        h = (x * scale * 2 + shift) % 360
        i = h // 60
        f = h / 60 - i
        if i == 0:   r, g, b = 255, round(255 * f), 0
        elif i == 1: r, g, b = round(255 * (1 - f)), 255, 0
        elif i == 2: r, g, b = 0, 255, round(255 * f)
        elif i == 3: r, g, b = 0, round(255 * (1 - f)), 255
        elif i == 4: r, g, b = round(255 * f), 0, 255
        else:        r, g, b = 255, 0, round(255 * (1 - f))
        screen.fill_rect(x, 0, 1, HEIGHT, (r, g, b))

    # bounce on a full-black card so motion contrast is visible
    card_w = 200
    screen.fill_rect((WIDTH - card_w) // 2, 20, card_w, 70, (0, 0, 0))
    bx = (WIDTH - card_w) // 2 + 10
    by = 30
    bw, bh = card_w - 20, 50
    px = bx + 8 + (bw - 26) * (0.5 + 0.5 * math.sin(t_ms * 0.004))
    py = by + 8 + (bh - 26) * (0.5 + 0.5 * math.sin(t_ms * 0.0073))
    screen.fill_rect(round(px), round(py), 10, 10, (255, 255, 255))

    # spinning arc gauge, round panel style
    cx, cy = 62, HEIGHT - 62
    screen.fill_rect(0, HEIGHT - 124, 124, 124, (0, 0, 0))
    for ring_r in (58, 50):
        for i in range(64):  # fading trailing arc
            a = t_ms * 0.2 - i * 4
            x = round(cx + ring_r * math.cos(math.radians(a - 90)))
            y = round(cy + ring_r * math.sin(math.radians(a - 90)))
            v = max(0, 255 - i * 4 + 64)
            g = min(255, max(0, v))
            screen.set_pixel(x, y, (0, g, 0))
    for i in range(12):
        a = math.radians(i * 30)
        x1 = round(cx + 40 * math.cos(a))
        y1 = round(cy + 40 * math.sin(a))
        x2 = round(cx + 46 * math.cos(a))
        y2 = round(cy + 46 * math.sin(a))
        screen.fill_rect(min(x1, x2), min(y1, y2), max(1, abs(x2 - x1)),
                         max(1, abs(y2 - y1)), (60, 60, 60))
