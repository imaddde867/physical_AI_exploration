import unittest

from animation.frame_timing import frame_times


class FrameTimingTests(unittest.TestCase):
    def test_eight_second_clip_keeps_duration_at_all_export_rates(self):
        for fps in (12, 15, 20, 24, 25, 30, 60):
            times = frame_times(1, 193, 24, fps)
            self.assertEqual(len(times), 8*fps)
            self.assertEqual(times[0], 1)
            self.assertLess(times[-1], 193)
            self.assertAlmostEqual(times[1]-times[0], 24/fps)

    def test_thirty_fps_evaluates_subframes_instead_of_duplicating_frames(self):
        self.assertEqual(frame_times(1, 193, 24, 30)[:4], [1., 1.8, 2.6, 3.4])

    def test_short_clip_excludes_duplicate_endpoint_at_fractional_frame_count(self):
        times = frame_times(1, 20, 24, 12)
        self.assertEqual(times, list(range(1, 20, 2)))

    def test_invalid_rates_or_duration_are_rejected(self):
        for args in ((1, 1, 24, 30), (1, 193, 0, 30), (1, 193, 24, 0)):
            with self.assertRaises(ValueError):
                frame_times(*args)
