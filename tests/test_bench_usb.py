import unittest

from tools.bench_usb import decide, payload, summarize


class BenchHelpers(unittest.TestCase):
    def test_payload_has_every_byte_including_ctrl_c_and_newline(self):
        p = payload(1000)
        self.assertEqual(len(p), 1000)
        self.assertTrue({0x03, 0x0A, 0x00, 0xFF} <= set(p))

    def test_summarize(self):
        s = summarize([0.1] * 19 + [0.3], 28800, failures=1)
        self.assertEqual((s["frames"], s["failures"]), (20, 1))
        self.assertAlmostEqual(s["ms_mean"], 110.0)
        # nearest-rank p95 of 20 samples is the 19th smallest, so one slow frame does not show
        self.assertAlmostEqual(s["ms_p95"], 100.0)
        self.assertAlmostEqual(s["kb_s_mean"], 28.8 / 0.11, places=1)
        self.assertAlmostEqual(s["kb_s_p95_worst"], 28.8 / 0.1, places=1)

    def test_decision_rule_thresholds(self):
        self.assertIn("full regions", decide(500))
        self.assertIn("dirty rectangles", decide(499.9))
        self.assertIn("dirty rectangles", decide(150))
        self.assertIn("bottleneck", decide(149.9))


if __name__ == "__main__":
    unittest.main()
