import unittest

from firmware.rp2040.main import draw, run, set_window
from experiments.hello_buddy import update
from sim.screen import Screen


class FakeLCD:
    def __init__(self):
        self.screen = Screen()
        self.frames = 0
        self.commands = []

    def fill(self, color):
        self.screen.clear((255, 255, 255) if color else (0, 0, 0))

    def fill_rect(self, x, y, w, h, color):
        self.screen.fill_rect(x, y, w, h, (255, 255, 255) if color else (0, 0, 0))

    def show(self):
        self.frames += 1

    def write_cmd(self, value):
        self.commands.append(("cmd", value))

    def write_data(self, value):
        self.commands.append(("data", value))


class DeviceBlinkTests(unittest.TestCase):
    def test_open_blink_open_matches_simulator_geometry(self):
        lcd, expected = FakeLCD(), Screen()
        for blink, t_ms in ((False, 200), (True, 4000), (False, 4200)):
            draw(lcd, blink)
            update(expected, t_ms)
            actual_mask = [[c != "#000000" for c in row] for row in lcd.screen.rows()]
            expected_mask = [[c != "#000000" for c in row] for row in expected.rows()]
            self.assertEqual(actual_mask, expected_mask)
        self.assertEqual(lcd.frames, 3)

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
        self.assertEqual(displays[0].set_bl_pwm.call_args_list, [((32768,),), ((0,),)])
        self.assertIn(("data", 43), displays[0].commands)


if __name__ == "__main__":
    unittest.main()
