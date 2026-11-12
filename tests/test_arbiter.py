import unittest

from daemon.arbiter import Slot, pick, visible_slots

SLEEP = {"v": 1, "t": "sleep"}


def S(name, priority, keys, expires=100.0, hard=False):
    return Slot(name, priority, {k: {"by": name} for k in keys}, expires, hard)


def slots(*items):
    return {s.name: s for s in items}


class PickTests(unittest.TestCase):
    def test_higher_priority_wins_per_key_and_lower_keys_survive(self):
        out = pick(slots(S("idle", "ambient", ["face", "bar1"]), S("brk", "alert", ["face"])),
                   "active", None, now=0)
        self.assertEqual(out, {"face": {"by": "brk"}, "bar1": {"by": "idle"}})

    def test_expired_slot_is_ignored(self):
        out = pick(slots(S("a", "ambient", ["face"], expires=5)), "active", None, now=5)
        self.assertEqual(out, {})

    def test_pin_beats_soft_alert_but_not_hard_alert(self):
        music = S("music", "activity", ["text0"])
        self.assertEqual(
            pick(slots(music, S("ci", "alert", ["text0"])), "active", "music", 0),
            {"text0": {"by": "music"}})
        self.assertEqual(
            pick(slots(music, S("ci", "alert", ["text0"], hard=True)), "active", "music", 0),
            {"text0": {"by": "ci"}})

    def test_locked_and_asleep_send_only_sleep(self):
        s = slots(S("idle", "ambient", ["face"]), S("ci", "alert", ["text0"], hard=True))
        for presence in ("locked", "asleep"):
            self.assertEqual(pick(s, presence, None, 0), {"power": SLEEP})

    def test_focus_allows_only_hard_alerts(self):
        s = slots(S("idle", "ambient", ["face"]), S("brk", "alert", ["text1"]),
                  S("ci", "alert", ["text0"], hard=True))
        self.assertEqual(pick(s, "focus", None, 0), {"text0": {"by": "ci"}})

    def test_cooldown_hides_soft_alerts_only(self):
        s = slots(S("brk", "alert", ["text1"]), S("ci", "alert", ["text0"], hard=True))
        self.assertEqual(pick(s, "active", None, now=10, alert_cooldown_until=50),
                         {"text0": {"by": "ci"}})
        self.assertEqual(set(pick(s, "active", None, now=60, alert_cooldown_until=50)),
                         {"text0", "text1"})

    def test_visible_slots_are_ordered_lowest_rank_first(self):
        s = slots(S("a", "alert", ["x"]), S("i", "ambient", ["x"]), S("c", "activity", ["x"]))
        self.assertEqual([x.name for x in visible_slots(s, "active", None, 0)], ["i", "c", "a"])


if __name__ == "__main__":
    unittest.main()
