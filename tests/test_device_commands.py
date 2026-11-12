"""Device-side command channel: framing, replies, and the blink hold timeout."""
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from daemon import protocol
from firmware.rp2040 import main as device
from firmware.rp2040.main import HOLD_MS, OVERFLOW, PARTIAL_LINE_MS, LineReader, handle, run

CLOSE = '{"v":1,"t":"face","blink":true}\n'
OPEN = '{"v":1,"t":"face","blink":false}\n'


class FakeStdin:
    """Characters from each chunk in turn; a finished chunk looks like an idle tick."""

    def __init__(self, *chunks):
        self.pending = [ch for chunk in chunks for ch in list(chunk) + [None]]

    def read(self, n=1):
        item = self.pending.pop(0) if self.pending else None
        return "" if item is None else item


class FakePoll:
    def __init__(self, stdin):
        self.stdin, self.obj = stdin, None

    def register(self, obj, mask=0):
        self.obj = obj

    def poll(self, timeout=0):
        if self.stdin.pending and self.stdin.pending[0] is None:
            self.stdin.pending.pop(0)  # chunk boundary: one idle tick between chunks
            return []
        return [(self.obj, 1)] if self.stdin.pending else []


class Clock:
    """Loop clock: sleeps advance time, and stops the loop the way Ctrl-C would."""

    def __init__(self, step=20, ticks=6):
        self.now, self.step, self.left = 0, step, ticks

    def ticks_ms(self):
        return self.now

    def ticks_diff(self, a, b):
        return (a - b + 4096) % 8192 - 4096

    def sleep_ms(self, ms):
        self.now += self.step
        self.left -= 1
        if self.left <= 0:
            raise KeyboardInterrupt


def reply(text):
    """(decoded reply, hold) for one line, as the host would read it back."""
    line, hold = handle(text)
    return protocol.decode(line), hold


class GazeTests(unittest.TestCase):
    def test_face_xy_updates_gaze_and_is_acked(self):
        gaze = [0.0, 0.0]
        line, hold = handle('{"v":1,"t":"face","x":0.5,"y":-1}', gaze)
        self.assertEqual(protocol.decode(line), {"v": 1, "t": "ok"})
        self.assertEqual((gaze, hold), ([0.5, -1], None))

    def test_omitted_axis_keeps_its_last_value(self):
        gaze = [0.5, -1]
        handle('{"v":1,"t":"face","x":0}', gaze)
        self.assertEqual(gaze, [0, -1])

    def test_mood_is_still_unsupported_and_leaves_gaze_alone(self):
        gaze = [0.0, 0.0]
        line, _ = handle('{"v":1,"t":"face","x":1,"mood":"happy"}', gaze)
        self.assertEqual(protocol.decode(line)["code"], "unsupported")
        self.assertEqual(gaze, [0.0, 0.0])


class LineReaderTests(unittest.TestCase):
    def feed_all(self, reader, text):
        return [reader.feed(ch) for ch in text]

    def test_assembles_a_line_byte_by_byte(self):
        reader = LineReader()
        self.assertEqual(self.feed_all(reader, '{"v":1,"t":"ping"}\n'),
                         [None] * 18 + ['{"v":1,"t":"ping"}'])

    def test_strips_carriage_return_from_crlf(self):
        reader = LineReader()
        self.assertEqual(self.feed_all(reader, '{"v":1,"t":"ping"}\r\n')[-1], '{"v":1,"t":"ping"}')

    def test_blank_line_is_a_line(self):
        reader = LineReader()
        self.assertEqual(reader.feed("\n"), "")

    def test_limit_equals_the_documented_byte_cap_with_newline(self):
        text = "x" * (protocol.MAX_LINE - 1) + "\n"  # 512 bytes including the newline
        self.assertEqual(len(text.encode()), protocol.MAX_LINE)
        self.assertEqual(self.feed_all(LineReader(), text)[-1], "x" * (protocol.MAX_LINE - 1))
        too_big = "x" * protocol.MAX_LINE + "\n"  # 513 bytes including the newline
        self.assertEqual(self.feed_all(LineReader(), too_big)[-1], OVERFLOW)

    def test_overlong_line_is_dropped_once_then_recovers(self):
        reader = LineReader()
        results = self.feed_all(reader, "x" * 600 + "\n")
        self.assertEqual([r for r in results if r is not None], [OVERFLOW])
        self.assertEqual(self.feed_all(reader, '{"v":1,"t":"ping"}\n')[-1], '{"v":1,"t":"ping"}')

    def test_reader_never_buffers_more_than_the_limit(self):
        reader = LineReader()
        for _ in range(600):
            reader.feed("x")
            self.assertLessEqual(reader.size, protocol.MAX_LINE - 1)
            self.assertLessEqual(len(reader.chars), protocol.MAX_LINE - 1)

    def test_limit_counts_utf8_bytes_not_characters(self):
        # 300 two-byte characters: 600 bytes, over the cap even though under it in characters.
        self.assertEqual(self.feed_all(LineReader(), "é" * 300 + "\n")[-1], OVERFLOW)
        line = "é" * 255  # 510 bytes, plus the newline = 511
        self.assertEqual(self.feed_all(LineReader(), line + "\n")[-1], line)

    def test_silence_discards_a_partial_line_so_the_next_sender_starts_clean(self):
        reader = LineReader()
        self.feed_all(reader, '{"v":1,"t":"pi')
        reader.tick(PARTIAL_LINE_MS - 1)
        reader.feed("n")  # input resets the silence clock
        reader.tick(PARTIAL_LINE_MS - 1)
        reader.tick(1)
        self.assertEqual(self.feed_all(reader, '{"v":1,"t":"ping"}\n')[-1], '{"v":1,"t":"ping"}')

    def test_silence_also_ends_an_overlong_drop(self):
        reader = LineReader()
        self.feed_all(reader, "x" * 600)
        reader.tick(PARTIAL_LINE_MS)
        self.assertEqual(self.feed_all(reader, "ok\n")[-1], "ok")


class HandleTests(unittest.TestCase):
    def test_valid_blink_closes_and_opens(self):
        self.assertEqual(reply('{"v":1,"t":"face","blink":true}'),
                         ({"v": 1, "t": "ok"}, HOLD_MS))
        self.assertEqual(reply('{"v":1,"t":"face","blink":false}'),
                         ({"v": 1, "t": "ok"}, 0))

    def test_face_without_blink_and_ping_are_ok_noops(self):
        self.assertEqual(reply('{"v":1,"t":"face"}'), ({"v": 1, "t": "ok"}, None))
        self.assertEqual(reply('{"v":1,"t":"ping"}'), ({"v": 1, "t": "ok"}, None))

    def test_valid_but_unrendered_commands_are_unsupported(self):
        for line in ('{"v":1,"t":"bar","id":0,"value":50}',
                     '{"v":1,"t":"brightness","value":10}',
                     '{"v":1,"t":"sleep"}',
                     '{"v":1,"t":"face","mood":"happy"}',
                     '{"v":1,"t":"face","x":0.5}'):
            with self.subTest(line=line):
                self.assertEqual(reply(line), ({"v": 1, "t": "err", "code": "unsupported"}, None))

    def test_documented_error_codes(self):
        cases = {
            "not json": "bad_json",
            '{"v":1,"t":"ping"}\x00': "bad_json",
            "": "bad_json",
            '{"v":2,"t":"ping"}': "bad_version",
            '{"v":1,"t":"zzz"}': "unknown_type",
            '{"v":1,"t":"face","blink":1}': "bad_field",
            '{"v":1,"t":"ping","extra":1}': "bad_field",
        }
        for line, code in cases.items():
            with self.subTest(line=line):
                self.assertEqual(reply(line), ({"v": 1, "t": "err", "code": code}, None))

    def test_hostile_input_never_raises(self):
        for line in ("\x00" * 10, "[" * 500, '{"v":1,"t":"text","slot":0,"s":"\\u0000"}',
                     '{"v":1,"t":"face","blink":null}', "\xff\xfe", "{}"):
            with self.subTest(line=line):
                self.assertIn(reply(line)[0]["t"], ("ok", "err"))


class LoopTests(unittest.TestCase):
    class Display:
        def __init__(self):
            self.set_bl_pwm = lambda value: None

        def setWindows(self, x0, y0, x1, y1):
            pass

    def loop(self, clock, *chunks):
        stdin, out, drawn = FakeStdin(*chunks), io.StringIO(), []
        modules = {"select": SimpleNamespace(POLLIN=1, poll=lambda: FakePoll(stdin)),
                   "time": clock,
                   "gc": SimpleNamespace(collect=lambda: None, mem_free=lambda: 50000),
                   "waveshare_lcd": SimpleNamespace(LCD_1inch69=self.Display)}
        with patch.dict("sys.modules", modules), patch("builtins.print"), \
                patch("sys.stdin", stdin), patch("sys.stdout", out), \
                patch("firmware.rp2040.main.draw",
                      side_effect=lambda lcd, blink, *gaze: drawn.append((clock.now, blink, *gaze))):
            with self.assertRaises(KeyboardInterrupt):
                run()
        return out.getvalue(), drawn

    def test_autonomous_blink_keeps_running_without_a_host(self):
        _, drawn = self.loop(Clock(step=20, ticks=210))
        self.assertEqual([d[:2] for d in drawn[:3]], [(0, False), (3860, True), (4000, False)])

    def test_command_blinks_immediately_and_releases_after_two_seconds(self):
        # 50 ms ticks: a per-tick countdown would take 2000 ticks, not 40, so this fails loudly.
        out, drawn = self.loop(Clock(step=50, ticks=80), CLOSE)
        self.assertEqual(drawn[0][:2], (0, True))  # closed on the tick the command arrived
        released_at = next(t for t, blink, *_ in drawn[1:] if blink is False)
        self.assertEqual(released_at, HOLD_MS)  # a dead sender cannot hold the eyes shut
        self.assertIn(True, [blink for t, blink, *_ in drawn if t > released_at])  # idle blink resumes
        self.assertEqual(protocol.decode(out), {"v": 1, "t": "ok"})

    def test_blink_false_reopens_the_eyes_and_restarts_the_idle_cycle(self):
        _, drawn = self.loop(Clock(step=20, ticks=210), CLOSE, OPEN)
        self.assertEqual([d[:2] for d in drawn[:2]], [(0, True), (40, False)])  # one tick per chunk boundary
        # phase restarted at 140 ms on the release, so the next idle blink lands 4 s later
        self.assertEqual(drawn[2][:2], (3900, True))

    def test_gaze_command_redraws_with_the_pixel_offset(self):
        out, drawn = self.loop(Clock(step=20, ticks=10), '{"v":1,"t":"face","x":0.5,"y":-1}\n')
        self.assertEqual([d[1:] for d in drawn], [(False, 5, -10)])  # drawn once, on the command's tick
        self.assertEqual(protocol.decode(out), {"v": 1, "t": "ok"})

    def test_garbage_and_overlong_input_are_answered_and_survived(self):
        out, _ = self.loop(Clock(step=20, ticks=8),
                           "x" * 600 + "\n" + "junk\n" + '{"v":1,"t":"ping"}\n')
        self.assertEqual([protocol.decode(line) for line in out.splitlines()],
                         [{"v": 1, "t": "err", "code": "too_long"},
                          {"v": 1, "t": "err", "code": "bad_json"},
                          {"v": 1, "t": "ok"}])

    def test_a_sender_that_died_mid_line_does_not_corrupt_the_next_command(self):
        # one idle tick per empty chunk; 60 ticks x 20 ms outlasts PARTIAL_LINE_MS
        out, _ = self.loop(Clock(step=20, ticks=70), '{"v":1,"t":"pi', *[""] * 60,
                           '{"v":1,"t":"ping"}\n')
        self.assertEqual([protocol.decode(line) for line in out.splitlines()],
                         [{"v": 1, "t": "ok"}])


class DrawTests(unittest.TestCase):
    class Canvas:
        def __init__(self):
            self.px, self.blits = {}, []

        def fill(self, color): pass
        def show(self): pass
        def blit(self, eye, x, y): self.blits.append((eye, x, y))

        def fill_rect(self, x, y, w, h, color):
            for i in range(w):
                for j in range(h):
                    self.px[(x + i, y + j)] = color

    def test_eye_fits_its_box_and_is_symmetric(self):
        c, mid = self.Canvas(), device.EYE_R + 1
        device.paint_eye(c, mid, mid)
        self.assertTrue(all(0 <= x < device.EYE_BOX and 0 <= y < device.EYE_BOX for x, y in c.px))
        self.assertTrue(all(c.px.get((2 * mid - x, y)) == v for (x, y), v in c.px.items()))
        self.assertEqual(c.px[(mid, mid)], device.EYE_COLOR)

    def test_open_eyes_are_blitted_once_built(self):
        lcd, eye = self.Canvas(), object()
        with patch.object(device, "make_open_eye", return_value=eye) as make, \
                patch.object(device, "_open_eye", []):
            device.draw(lcd, False)
            device.draw(lcd, False)
        make.assert_called_once()
        left, right = lcd.blits[0], lcd.blits[1]
        self.assertEqual((left[0], left[1], right[1]), (eye, 120 - 42 - 19, 120 + 42 - 19))
        self.assertEqual(left[2], 140 - 19)
        self.assertEqual(len(lcd.blits), 4)

    def test_closed_eyes_skip_the_cache(self):
        lcd = self.Canvas()
        with patch.object(device, "make_open_eye") as make:
            device.draw(lcd, True)
        make.assert_not_called()
        self.assertEqual(lcd.blits, [])


if __name__ == "__main__":
    unittest.main()
