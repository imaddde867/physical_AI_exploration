"""Desktop study: pronounced breathing and head sway from the approved still."""
import math

from experiments import occupant_still as still
from sim.screen import HEIGHT, WIDTH, rgb565

_LEVEL5 = [round(i * 255 / 31) for i in range(32)]
_LEVEL6 = [round(i * 255 / 63) for i in range(64)]
_WEIGHTS = []
for y in range(1, HEIGHT - 1):
    cells = []
    for x in range(45, 196):
        head = math.exp(-((x - 166) / 25) ** 2 - ((y - 54) / 38) ** 2)
        body = math.exp(-((x - 120) / 45) ** 2 - ((y - 145) / 75) ** 2)
        body *= math.sin(math.pi * y / (HEIGHT - 1)) ** 2
        if max(head, body) > 0.01:
            cells.append((x, head, body, body * (x - 120) / 60))
    _WEIGHTS.append((y, cells))


def update(screen, t_ms):
    still.update(screen, t_ms)
    breath = 10.0 * math.sin(math.tau * t_ms / 4200)
    head_x = 10.0 * math.sin(math.tau * t_ms / 6500)
    head_y = 4.0 * math.sin(math.tau * t_ms / 7100)
    # shortcut: desktop image warp only; bake frames or use tiles after measuring the board.
    for y, cells in _WEIGHTS:
        row = screen.rows()[y]
        for x, head, body, spread in cells:
            sx = max(0, min(WIDTH - 1, x - head_x * head - breath * spread))
            sy = max(0, min(HEIGHT - 1, y - head_y * head + breath * body))
            x0, y0 = int(sx), int(sy)
            fx, fy = sx - x0, sy - y0
            a = still.RGB[y0 * WIDTH + x0]
            b = still.RGB[y0 * WIDTH + min(x0 + 1, WIDTH - 1)]
            c = still.RGB[min(y0 + 1, HEIGHT - 1) * WIDTH + x0]
            d = still.RGB[min(y0 + 1, HEIGHT - 1) * WIDTH + min(x0 + 1, WIDTH - 1)]
            color = tuple(int((a[i] * (1 - fx) + b[i] * fx) * (1 - fy)
                              + (c[i] * (1 - fx) + d[i] * fx) * fy + 0.5)
                          for i in range(3))
            value = rgb565(color)
            row[x] = "#%02x%02x%02x" % (_LEVEL5[value >> 11],
                                      _LEVEL6[(value >> 5) & 63], _LEVEL5[value & 31])
