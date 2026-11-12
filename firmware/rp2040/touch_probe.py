"""Bring-up probe: touch coordinates, gestures, frame times. Run from Thonny; see README.md."""
import time

PHASE_MS = 10000
GESTURES = {1: 'down', 2: 'up', 3: 'left', 4: 'right', 0x0B: 'double click', 0x0C: 'long press'}


def watch(touch, mode):
    touch.Mode, touch.Flag, touch.Gestures = mode, 0, 0
    touch.Set_Mode(mode)
    last = None
    end = time.ticks_add(time.ticks_ms(), PHASE_MS)
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        if mode == 1 and touch.Flag:
            touch.Flag = 0
            point = (touch.X_point, touch.Y_point)
            if point != last:
                print('point x=%d y=%d' % point)
                last = point
        elif mode == 0 and touch.Gestures:
            code, touch.Gestures = touch.Gestures, 0
            print('gesture 0x%02X %s' % (code, GESTURES.get(code, '?')))
        time.sleep_ms(5)


def time_draw(lcd, draw, blink, samples=10):
    start = time.ticks_us()
    for _ in range(samples):
        draw(lcd, blink)
    return time.ticks_diff(time.ticks_us(), start) / samples / 1000


def run():
    import gc
    from benchmark_display import measure_show
    from main import draw, set_window
    from waveshare_lcd import LCD_1inch69, Touch_CST816D

    class Display(LCD_1inch69):
        def setWindows(self, x0, y0, x1, y1):
            set_window(self, x0, y0, x1, y1)

    gc.collect()
    lcd = Display()
    try:
        lcd.set_bl_pwm(8192)
        touch = Touch_CST816D(mode=1, LCD=lcd)
        if not hasattr(touch, 'Gestures'):  # the vendor __init__ returns early when undetected
            print('touch not detected: check I2C pins 6/7, IRQ 21, RST 22')
        else:
            print('Touch the screen: corners and centre (10 s). Panel is 240x280.')
            watch(touch, 1)
            print('Swipe up/down/left/right, double tap, long press (10 s).')
            watch(touch, 0)
        draw(lcd, False)
        print('show():', measure_show(lcd, time))
        print('draw() open eyes: %.1f ms' % time_draw(lcd, draw, False))
        print('draw() closed eyes: %.1f ms' % time_draw(lcd, draw, True))
        print('free heap:', gc.mem_free())
    finally:
        lcd.set_bl_pwm(0)


if __name__ == '__main__':
    run()
