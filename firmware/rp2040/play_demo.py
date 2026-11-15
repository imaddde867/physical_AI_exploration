"""Cycle every state on the panel. Run with mpremote; do not replace main.py.

Needs <state>-12.clp for all 8 states on the board (animation/clip_export.py output).
"""


def run():
    import gc
    import time
    from clip_player import STATES, ClipPlayer
    from main import set_window
    from waveshare_lcd import LCD_1inch69

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    gc.collect()
    lcd = Display()
    try:
        lcd.set_bl_pwm(8192)
        player = ClipPlayer(lcd.buffer, lambda: lcd.fill(0))
        gc.collect()
        print("heap start", gc.mem_free())
        order = [s for s in STATES if s != "watch"]
        for state in order:
            player.request(state)
            # idle plays until the boundary, the gesture once, then idle again
            seen = False
            while True:
                t = time.ticks_ms()
                now = player.step()
                lcd.show()
                seen = seen or now == state
                if seen and now == "watch":
                    break
                time.sleep_ms(max(0, player.period_ms - time.ticks_diff(time.ticks_ms(), t)))
            print("played", state, "heap", gc.mem_free())
    finally:
        lcd.set_bl_pwm(0)


if __name__ == "__main__":
    run()
