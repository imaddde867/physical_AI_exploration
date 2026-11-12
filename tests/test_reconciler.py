import unittest

from daemon import protocol
from daemon.reconciler import HEARTBEAT_S, PING, Reconciler, revert

FACE = {"v": 1, "t": "face", "x": 0.5}
FACE2 = {"v": 1, "t": "face", "x": -0.5}
TEXT1 = {"v": 1, "t": "text", "slot": 1, "s": "hi"}
SLEEP = {"v": 1, "t": "sleep"}


def make():
    now = [0.0]
    return Reconciler(lambda: now[0]), now


class ReconcilerTests(unittest.TestCase):
    def test_sends_changes_only_then_heartbeats(self):
        r, now = make()
        self.assertEqual(r.diff({"face": FACE}), [FACE])
        self.assertEqual(r.diff({"face": FACE}), [])
        now[0] = HEARTBEAT_S
        self.assertEqual(r.diff({"face": FACE}), [PING])
        self.assertEqual(r.diff({"face": FACE}), [])  # the ping reset the timer

    def test_only_the_changed_key_is_resent(self):
        r, _ = make()
        r.diff({"face": FACE, "text1": TEXT1})
        self.assertEqual(r.diff({"face": FACE2, "text1": TEXT1}), [FACE2])

    def test_removed_keys_are_reverted(self):
        r, _ = make()
        r.diff({"face": FACE, "text1": TEXT1})
        self.assertEqual(r.diff({}), [revert("face"), revert("text1")])

    def test_wake_goes_out_before_new_state(self):
        r, _ = make()
        r.diff({"power": SLEEP})
        self.assertEqual(r.diff({"face": FACE}), [{"v": 1, "t": "wake"}, FACE])

    def test_resync_resends_everything(self):
        r, _ = make()
        r.diff({"face": FACE})
        r.resync()
        self.assertEqual(r.diff({"face": FACE}), [FACE])

    def test_unknown_keys_have_no_revert_and_every_message_is_valid(self):
        self.assertIsNone(revert("brightness"))
        for msg in (PING, revert("face"), revert("power"), revert("bar3"), revert("text0")):
            protocol.encode(msg)


if __name__ == "__main__":
    unittest.main()
