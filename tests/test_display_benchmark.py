import unittest

from firmware.rp2040.benchmark_display import measure_show


class DisplayBenchmarkTests(unittest.TestCase):
    def test_transfer_statistics_survive_tick_wrap(self):
        class Clock:
            now = 250
            def ticks_us(self): return self.now % 256
            def ticks_diff(self, a, b): return (a-b+128) % 256-128
        clock = Clock()
        class LCD:
            calls = 0
            def show(self):
                self.calls += 1
                clock.now += self.calls
        lcd = LCD()
        report = measure_show(lcd, clock, 20)
        self.assertEqual(lcd.calls, 20)
        self.assertEqual(report['mean_us'], 10.5)
        self.assertEqual(report['p95_us'], 19)
        self.assertEqual(report['max_us'], 20)
        self.assertAlmostEqual(report['transfer_only_fps'], 1000000/10.5)

    def test_bad_sample_count_never_touches_display(self):
        for count in (0, -1, 1001):
            with self.assertRaises(ValueError):
                measure_show(None, None, count)
