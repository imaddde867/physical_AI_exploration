"""Diff the desired device state against what was last sent."""
import time

HEARTBEAT_S = 1.5  # protocol: at least one valid message every 2 s
PING = {"v": 1, "t": "ping"}


def revert(key):
    if key == "face":
        return {"v": 1, "t": "face", "x": 0, "y": 0, "blink": False}
    if key == "power":
        return {"v": 1, "t": "wake"}
    # ponytail: the protocol has no bar-hide, so value 0 is the closest; add a message if it matters
    if key.startswith("bar"):
        return {"v": 1, "t": "bar", "id": int(key[3:]), "value": 0}
    if key.startswith("text"):
        return {"v": 1, "t": "text", "slot": int(key[4:]), "s": ""}
    return None


class Reconciler:
    """Messages in `sent` are shared, not copied: callers must treat them as immutable."""

    def __init__(self, clock=time.monotonic):
        self.clock, self.sent, self.last_tx = clock, {}, None

    def resync(self):
        self.sent = {}

    def diff(self, desired):
        out = [m for k in sorted(self.sent.keys() - desired.keys()) if (m := revert(k))]
        out += [msg for k, msg in desired.items() if self.sent.get(k) != msg]
        self.sent = dict(desired)
        now = self.clock()
        if out:
            self.last_tx = now
        elif self.last_tx is None or now - self.last_tx >= HEARTBEAT_S:
            out.append(PING)
            self.last_tx = now
        return out
