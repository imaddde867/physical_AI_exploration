import asyncio
import unittest

from daemon import protocol
from daemon.arbiter import ALERT_GAP_S
from daemon.host import Ctx, Host, supervise

FACE = {"v": 1, "t": "face", "x": 0.5}
TEXT0 = {"v": 1, "t": "text", "slot": 0, "s": "break"}
TEXT1 = {"v": 1, "t": "text", "slot": 1, "s": "ci"}
WAKE = {"v": 1, "t": "wake"}
SLEEP = {"v": 1, "t": "sleep"}
CLEAR0 = {"v": 1, "t": "text", "slot": 0, "s": ""}


class FakeLink:
    def __init__(self):
        self.sent, self.fail = [], False

    def send(self, msg):
        protocol.encode(msg)  # only valid messages may reach the wire
        if self.fail:
            raise OSError("unplugged")
        self.sent.append(msg)


def make():
    now, link = [0.0], FakeLink()
    return Host(link, lambda: now[0]), now, link


def drain(link):
    out, link.sent[:] = list(link.sent), []
    return out


class HostTests(unittest.TestCase):
    def test_slot_state_is_sent_once_then_reverted_on_expiry(self):
        h, now, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=10)
        h.step()
        self.assertEqual(drain(link), [FACE])
        h.step()
        self.assertEqual(drain(link), [])
        now[0] = 10
        h.step()
        self.assertEqual(drain(link), [{"v": 1, "t": "face", "x": 0, "y": 0, "blink": False}])

    def test_show_copies_so_a_module_cannot_mutate_sent_state(self):
        h, _, link = make()
        msg = dict(FACE)
        h.show("idle", "ambient", {"face": msg}, ttl=10)
        h.step()
        msg["x"] = -1
        h.show("idle", "ambient", {"face": msg}, ttl=10)
        h.step()
        self.assertEqual([m["x"] for m in link.sent], [0.5, -1])

    def test_locked_sends_sleep_and_unlock_wakes_and_restores(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        h.step()
        drain(link)
        h.presence = "locked"
        h.step()
        self.assertEqual(drain(link)[-1], SLEEP)
        h.presence = "active"
        h.step()
        self.assertEqual(drain(link), [WAKE, FACE])

    def test_hello_triggers_a_full_resend(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        h.step()
        drain(link)
        h.on_message({"v": 1, "t": "hello", "fw": "0.2", "w": 240, "h": 280,
                      "boot_id": "ab12", "caps": ["touch"]})
        h.step()
        self.assertEqual(drain(link), [FACE])
        self.assertEqual((h.boot_id, h.caps), ("ab12", {"touch"}))

    def test_send_failure_resyncs_for_the_next_connection(self):
        h, _, link = make()
        h.show("idle", "ambient", {"face": FACE}, ttl=100)
        link.fail = True
        with self.assertRaises(OSError):
            h.step()
        link.fail = False
        h.step()
        self.assertEqual(drain(link), [FACE])

    def test_alert_gap_delays_the_next_soft_alert(self):
        h, now, link = make()
        h.show("brk", "alert", {"text0": TEXT0}, ttl=5)
        h.step()
        now[0] = 6
        h.step()  # alert gone: cooldown starts at t=6
        drain(link)
        h.show("ci", "alert", {"text1": TEXT1}, ttl=1000)
        now[0] = 7
        h.step()
        self.assertNotIn(TEXT1, drain(link))
        now[0] = 6 + ALERT_GAP_S
        h.step()
        self.assertIn(TEXT1, drain(link))

    def test_ctx_show_and_clear(self):
        h, _, link = make()
        c = Ctx(h, "brk")
        c.show("alert", {"text0": TEXT0}, ttl=5)
        h.step()
        self.assertEqual(drain(link), [TEXT0])
        c.clear()
        h.step()
        self.assertEqual(drain(link), [CLEAR0])


class SuperviseTests(unittest.IsolatedAsyncioTestCase):
    async def test_restarts_with_growing_delay_then_returns(self):
        calls, delays = [], []

        async def flaky(ctx):
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError("boom")

        async def sleep(d):
            delays.append(d)

        await supervise("x", flaky, None, log=lambda m: None, sleep=sleep, clock=lambda: 0.0)
        self.assertEqual((len(calls), delays), (3, [1.0, 2.0]))

    async def test_a_long_run_resets_the_delay(self):
        calls, delays, t = [], [], [0.0]

        async def flaky(ctx):
            calls.append(1)
            t[0] += 100
            if len(calls) < 3:
                raise RuntimeError("boom")

        async def sleep(d):
            delays.append(d)

        await supervise("x", flaky, None, log=lambda m: None, sleep=sleep, clock=lambda: t[0])
        self.assertEqual(delays, [1.0, 1.0])

    async def test_cancellation_is_not_swallowed(self):
        async def forever(ctx):
            await asyncio.sleep(3600)

        task = asyncio.create_task(supervise("x", forever, None, log=lambda m: None))
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    unittest.main()
