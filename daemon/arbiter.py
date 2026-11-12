"""Which module's state reaches the device. Pure logic; see the buddy-os spec."""
from dataclasses import dataclass

PRIORITY = {"ambient": 0, "activity": 1, "alert": 2}
PRESENCE = ("active", "idle", "locked", "asleep", "focus")
ALERT_GAP_S = 30.0
SLEEP = {"v": 1, "t": "sleep"}


@dataclass
class Slot:
    name: str
    priority: str
    state: dict  # state key -> complete protocol message
    expires: float  # absolute, same clock as `now`
    hard: bool = False  # a hard alert breaks through Focus, the alert gap and a pin


def _rank(slot, pin):
    if slot.priority == "alert" and slot.hard:
        return 3
    if slot.name == pin:
        return 2.5
    return PRIORITY[slot.priority]


def visible_slots(slots, presence, pin, now, alert_cooldown_until=0.0):
    live = [s for s in slots.values() if s.expires > now]
    if presence in ("locked", "asleep"):
        return []
    if presence == "focus":
        live = [s for s in live if s.priority == "alert" and s.hard]
    elif now < alert_cooldown_until:
        live = [s for s in live if s.priority != "alert" or s.hard]
    return sorted(live, key=lambda s: _rank(s, pin))  # stable: later insertion wins ties


def pick(slots, presence, pin, now, alert_cooldown_until=0.0):
    if presence in ("locked", "asleep"):
        return {"power": dict(SLEEP)}
    state = {}
    for s in visible_slots(slots, presence, pin, now, alert_cooldown_until):
        state.update(s.state)
    return state
