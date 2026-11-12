# Buddy OS: system design

Date 2026-11-12. Status: approved design, not implemented. Reviewed twice by an independent Opus pass; throughput figures below are estimates until the benchmark (slice 0) runs.

## Goal

An always-on companion that idles by itself (looking, blinking, small animations), reacts to Mac events (music, AirPods, CI, usage limits, break reminders, later screen content), and accepts touch (tap to switch lyrics / album art). Smooth visuals, but reliable first: it must behave sanely when the Mac sleeps, the cable is pulled, or a module crashes.

## Decisions

| Question | Decision |
|---|---|
| Who draws pixels | **Hybrid.** Device owns face, idle, blink, touch feedback, fallback. Mac may paint regions under a time-limited frame lease. |
| Where modules run | **One Mac asyncio daemon, in-process plugins.** A module may later move to a helper process without changing the core. |
| Module coordination | **Desired-state reconciler**, not an event bus (see below). |

Hybrid is conditional on slice 0. If USB sustains >= 500 KB/s, full regions; 150-500 KB/s, dirty rectangles only; < 150 KB/s, the MicroPython CDC stack is the bottleneck: add a C/viper module or fall back to device-only rendering with clips in flash.

## Architecture

```
modules (idle, music, usage, ci, airpods, breaks, ...)
   each owns ONE slot: {scene, priority, ttl, dedupe_key}
        |
   pick(slots, presence, pin, now)   pure function, unit-tested with a fake clock
        |
   reconciler: diff vs last sent state -> link
        |
   USB CDC  <->  RP2040 (face, idle, touch, badges, leased regions)
```

- **Module** = a Python file with `async run(ctx)`. It writes its slot (`ctx.show(...)`, `ctx.clear()`); it never touches the serial port and never calls other modules. One slot per module means the newest value wins and nothing queues, which absorbs notification storms. A minimum gap between alerts is enforced in `pick`.
- **Crash guard**: each module task is wrapped in try/except with backoff restart. A dead module's slot expires by TTL, so nothing can stick on screen.
- **Priority classes**: ambient < activity < alert. Higher preempts lower; an alert times out and the previous scene resumes.
- **Touch**: a tap pins or cycles the current module's views (lyrics <-> album art). A pin outranks everything except a hard alert.
- **Presence** is a global input checked before priority: active, idle, locked, Mac asleep, Focus on. Locked or asleep sends `sleep`. Focus allows hard alerts only.

## Layout

Fixed, no per-module full-screen scenes: a main region (face or leased content) plus a badge strip. Small indicators (CI result, AirPods connected, break due) are badges, not extra priority classes.

## Protocol changes (additive, gated on `caps`)

Current firmware rejects unknown fields and any `v` other than 1, so features are gated on capabilities, not version bumps.

| Message | Direction | Purpose |
|---|---|---|
| `hello` {fw, proto, caps[], boot_id, w, h} | dev -> host | Sent on connect. New `boot_id` or reconnect: host resends full state and all leases are cancelled. |
| `lease` {id, rect, ttl_ms} | host -> dev | Device accepts Mac pixels for `rect` until TTL expires. |
| `frame` {id, seq, x, y, w, h, len} then `len` raw bytes | host -> dev | JSON header line + raw RGB565. No magic or CRC: USB bulk transfers are already checksummed. Device acks each frame before the next. |
| `touch` {kind: tap/hold/swipe, x, y} | dev -> host | Touch input. |
| `badge` {slot, icon, state} | host -> dev | Badge strip. |

Failure rule: lease expiry, a stall over 200 ms, or a malformed frame makes the device drop the frame and repaint its local face. Recovery never depends on the Mac.

`docs/protocol.md` ("pixel data out of scope") and `docs/product-brief.md` ("do not stream") must be updated when slice 4 lands.

## Device constraints to respect

- USB serial is shared with the REPL: byte 0x03 in binary data raises Ctrl-C. Call `micropython.kbd_intr(-1)` during a lease.
- Reads are currently capped at 256 chars per 20 ms tick (about 12.8 KB/s). Use `sys.stdin.buffer.readinto` into a preallocated buffer.
- Single framebuffer (134,400 B) only; write rows straight into it. Free heap is about 29 KB once touch is loaded: measure heap after every slice.
- `show()` measured about 23 ms (about 43 fps). Smooth motion stays on the device; Mac regions are 10 fps or less.

## Screen reaction (last, opt-in)

macOS grants Screen Recording per process, so granting it to `python3` grants it to every script. Run it as a separate helper with its own permission, **off by default**, a visible "watching" mark on the device, a local model only, and no frames saved. Before planning music features, verify the Now Playing source still works on current macOS (it uses a private API).

## Build order and tests

0. **USB throughput benchmark**, on the real path, measured while `show()` runs; includes unplug-mid-frame recovery. Runs in parallel with 1.
1. **Daemon skeleton**: slots, `pick`, reconciler, crash guard, presence input, `hello` / `boot_id` resync, fake link. Reuses `daemon/protocol.py` and `daemon/link.py`. Hardware-free tests: a fake device over a pty reusing the device `handle` and `LineReader`, and the `sim/` renderer.
2. **Modules `idle` and `break_reminder`**: gaze/blink hints from the daemon, timer to alert.
3. **Touch events** end to end (device -> daemon -> pin/cycle).
4. **Frame leases**, if slice 0 passes. First consumer: usage bars or album art.
5. **Then, any order, each a new module file**: music vibe and lyrics, AirPods, CI status. Screen reaction last.

Tests: `pick` (priority, preemption, TTL, alert gap, presence, pin) is pure logic with a fake clock. Device behaviour gets a scripted serial smoke test after each flash.

## Out of scope for now

Typed inter-module events and manifests; CRC/magic framing; full-screen scenes per module; streaming full-screen video.
