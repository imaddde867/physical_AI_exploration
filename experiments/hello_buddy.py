from sim.screen import HEIGHT, WIDTH

EYE_R, EYE_DX, BLINK_MS, BLINK_EVERY_MS = 34, 78, 140, 4000


def update(screen, t_ms) -> None:
    screen.clear((0, 0, 0))
    blink = t_ms % BLINK_EVERY_MS < BLINK_MS
    for sign in (-1, 1):
        cx, cy = WIDTH // 2 + sign * EYE_DX, HEIGHT // 2
        if blink:
            screen.fill_rect(cx - EYE_R, cy - 3, 2 * EYE_R + 1, 6, (235, 235, 235))
        else:
            screen.fill_circle(cx, cy, EYE_R, (235, 235, 235))
