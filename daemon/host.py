"""Slots, presence and resync around one link; modules talk to Ctx, never to the port."""
import asyncio
import time

from daemon import protocol
from daemon.arbiter import ALERT_GAP_S, PRIORITY, Slot, pick, visible_slots
from daemon.reconciler import Reconciler, revert

STABLE_S = 60.0  # a module that ran this long before crashing gets a fresh backoff
MAX_BACKOFF_S = 30.0


class Host:
    def __init__(self, link, clock=time.monotonic):
        self.link, self.clock = link, clock
        self.slots, self.presence, self.pin = {}, "active", None
        self.boot_id, self.caps = None, set()
        self.rec = Reconciler(clock)
        self.cooldown_until, self._alert_shown = 0.0, False

    def show(self, name, priority, state, ttl, hard=False):
        PRIORITY[priority]  # KeyError here, in the module, not later in step()
        for k, v in state.items():  # validate before storing: a bad slot must not reach step()
            protocol.encode(v)
            if (r := revert(k)) is not None:
                protocol.encode(r)
        self.slots[name] = Slot(name, priority, {k: dict(v) for k, v in state.items()},
                                self.clock() + ttl, hard)

    def clear(self, name):
        self.slots.pop(name, None)

    def on_message(self, msg):
        if msg["t"] == "hello":  # a reconnect or a reboot: the device lost our state
            self.boot_id, self.caps = msg.get("boot_id"), set(msg.get("caps", ()))
            self.rec.resync()

    def step(self):
        now = self.clock()
        self.slots = {n: s for n, s in self.slots.items() if s.expires > now}
        args = (self.slots, self.presence, self.pin, now, self.cooldown_until)
        shown = any(s.priority == "alert" for s in visible_slots(*args))
        if self._alert_shown and not shown:
            self.cooldown_until = now + ALERT_GAP_S
        self._alert_shown = shown
        try:
            for msg in self.rec.diff(pick(*args)):
                self.link.send(msg)
        except OSError:
            self.rec.resync()
            raise


class Ctx:
    def __init__(self, host, name):
        self.host, self.name = host, name

    def show(self, priority, state, ttl, hard=False):
        self.host.show(self.name, priority, state, ttl, hard)

    def clear(self):
        self.host.clear(self.name)


async def supervise(name, run, ctx, log=print, sleep=asyncio.sleep, clock=time.monotonic):
    delay = 1.0
    while True:
        started = clock()
        try:
            return await run(ctx)
        except Exception as e:  # CancelledError is a BaseException and passes through
            if clock() - started > STABLE_S:
                delay = 1.0
            log(f"module {name} crashed: {e!r}; restarting in {delay:.0f}s")
            await sleep(delay)
            delay = min(delay * 2, MAX_BACKOFF_S)
