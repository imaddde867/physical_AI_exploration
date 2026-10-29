import os

from sim.screen import HEIGHT, WIDTH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def update(screen, t_ms) -> None:
    screen.clear((0, 0, 0))
    screen.blit_image(os.path.join(ROOT, "assets", "face-idle-240.png"), (WIDTH - 240) // 2, (HEIGHT - 240) // 2)
    warm = (255, 205, 157) if int(t_ms / 500) % 2 == 0 else (120, 96, 78)
    screen.fill_rect(0, 0, WIDTH, 8, warm)
    screen.fill_rect(0, HEIGHT - 8, WIDTH, 8, warm)
