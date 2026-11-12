import unittest

from firmware.rp2040.main import draw, gray, run, set_window
from sim.screen import Screen


class FakeLCD:
    def __init__(self):
        self.screen = Screen()
        self.frames = 0
        self.commands = []

    def fill(self, color):
        self.screen.clear((255, 255, 255) if color else (0, 0, 0))

    def fill_rect(self, x, y, w, h, color):
        packed = ((color & 255) << 8) | (color >> 8)
        rgb = ((packed >> 11) * 255 // 31,
               ((packed >> 5) & 63) * 255 // 63, (packed & 31) * 255 // 31)
        self.screen.fill_rect(x, y, w, h, rgb)

    def show(self):
        self.frames += 1

    def write_cmd(self, value):
        self.commands.append(("cmd", value))

    def write_data(self, value):
        self.commands.append(("data", value))


class DeviceBlinkTests(unittest.TestCase):
    def test_smooth_eyes_blink_and_restore_without_a_halo(self):
        lcd = FakeLCD()
        frames = []
        for blink in (False, True, False):
            draw(lcd, blink)
            frames.append([row[:] for row in lcd.screen.rows()])
        self.assertEqual(frames[0], frames[2])
        self.assertNotEqual(frames[0], frames[1])
        for cx in (78, 162):
            center, edge = frames[0][140][cx], frames[0][140][cx + 18]
            self.assertTrue("#000000" < edge < center < "#ffffff")
            self.assertEqual(frames[0][140][cx + 19], "#000000")
            self.assertEqual(frames[0][121][cx], "#000000")
            self.assertEqual(frames[1][140][cx], center)
            self.assertEqual(frames[1][142][cx], "#000000")
        self.assertEqual(lcd.frames, 3)

    def test_gray_wire_byte_order(self):
        self.assertEqual(gray(0), 0)
        self.assertEqual(gray(255), 0xFFFF)
        self.assertEqual(gray(232), 0x5DEF)

    def test_full_window_includes_all_280_rows(self):
        lcd = FakeLCD()
        set_window(lcd, 0, 0, 240, 280)
        self.assertEqual(lcd.commands, [
            ("cmd", 0x2A), ("data", 0), ("data", 0), ("data", 0), ("data", 239),
            ("cmd", 0x2B), ("data", 0), ("data", 20), ("data", 1), ("data", 43),
            ("cmd", 0x2C),
        ])

    def test_invalid_window_sends_nothing(self):
        for bounds in ((0, 0, 241, 280), (0, 0, 240, 281), (-1, 0, 1, 1),
                       (0, 0, 0, 1), (0, 2, 1, 1)):
            lcd = FakeLCD()
            with self.assertRaises(ValueError):
                set_window(lcd, *bounds)
            self.assertEqual(lcd.commands, [])

    def test_loop_survives_tick_wrap_and_turns_backlight_off_on_stop(self):
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        displays = []

        class Driver(FakeLCD):
            def __init__(self):
                super().__init__()
                self.set_bl_pwm = Mock()
                self.setWindows(0, 0, 240, 280)
                displays.append(self)

        clock = SimpleNamespace(
            ticks_ms=Mock(side_effect=[8000, 8000, 3668, 3808]),
            ticks_diff=lambda a, b: (a - b + 4096) % 8192 - 4096,
            sleep_ms=Mock(side_effect=[None, None, KeyboardInterrupt]),
        )
        modules = {"waveshare_lcd": SimpleNamespace(LCD_1inch69=Driver), "time": clock,
                   "gc": SimpleNamespace(collect=lambda: None, mem_free=lambda: 50000)}
        with patch.dict("sys.modules", modules), patch("builtins.print"):
            with self.assertRaises(KeyboardInterrupt):
                run()
        self.assertEqual(displays[0].frames, 3)
        self.assertEqual(displays[0].set_bl_pwm.call_args_list, [((8192,),), ((0,),)])
        self.assertIn(("data", 43), displays[0].commands)


if __name__ == "__main__":
    unittest.main()
