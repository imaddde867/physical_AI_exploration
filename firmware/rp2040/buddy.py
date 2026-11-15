"""Live buddy: idle with autonomous glances, reacts to touch. Run with mpremote; do not replace main.py.

Needs <state>-12.clp for all 8 states on the board. Ctrl-C leaves the last frame up.
"""
import os

GESTURE_STATE = {0x05: "lean_in", 0x0B: "look_around", 0x0C: "scratch",
                 3: "look_left", 4: "look_right", 1: "lean_back", 2: "lean_back"}
# Weighted, so the character mostly shifts and glances and scratches rarely.
IDLE_PICKS = ("shift", "shift", "shift", "look_left", "look_left", "look_right", "look_right",
              "look_around", "lean_in", "lean_back", "scratch")
GESTURE_CHANCE = 70  # percent per idle loop that a gesture follows
BACKLIGHT = 40000


def pick(last):
    while True:
        s = IDLE_PICKS[os.urandom(1)[0] % len(IDLE_PICKS)]
        if s != last:
            return s


def run():
    import gc
    import time
    from clip_player import IDLE, ClipPlayer
    from main import set_window
    from waveshare_lcd import LCD_1inch69, Touch_CST816D

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    gc.collect()
    lcd = Display()
    lcd.set_bl_pwm(BACKLIGHT)
    touch = Touch_CST816D(mode=0, LCD=lcd)
    if hasattr(touch, "Gestures"):
        touch.Gestures = 0  # the vendor init leaves the string "None"
    else:
        touch = None
        print("touch not detected; autonomous only")
    player = ClipPlayer(lcd.buffer, lambda: lcd.fill(0))
    gc.collect()
    print("buddy ready; heap", gc.mem_free())
    last = None
    try:
        while True:
            t = time.ticks_ms()
            code = touch.Gestures if touch else 0
            if code:
                touch.Gestures = 0
                last = GESTURE_STATE.get(code, "lean_in")
                player.request(last, now=True)
            state = player.step()
            lcd.show()
            # idx 2 = the first frame after an idle loop (re)starts: decide what follows it
            if state == IDLE and player.idx == 2 and player.pending == IDLE \
                    and os.urandom(1)[0] * 100 < GESTURE_CHANCE * 256:
                last = pick(last)
                player.request(last)
            time.sleep_ms(max(0, player.period_ms - time.ticks_diff(time.ticks_ms(), t)))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
