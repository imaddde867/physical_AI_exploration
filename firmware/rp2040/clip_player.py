"""Delta-clip player (CLP1, see animation/clip_export.py) for the one LCD framebuffer.

Streams a clip from flash in small chunks so the heap stays free. `step()` applies
one frame to `fb`; the caller then calls `lcd.show()` and sleeps `period_ms`.

States: `watch` loops; every other state plays once, then returns to `watch`.
`request(state)` takes effect at the next loop boundary, where every clip shares
the idle pose. A switch clears the framebuffer and applies the new clip's
keyframe, so no clip depends on the previous clip's pixels.
"""
import struct

STATES = ("watch", "look_left", "look_right", "look_around",
          "lean_back", "lean_in", "shift", "scratch")
IDLE = "watch"
CHUNK = 4096

try:
    import micropython

    @micropython.viper
    def _apply(buf, n: int, fb, st) -> int:
        """Apply buf[:n] to fb, resumable mid-run. st = [dest byte offset, run bytes left].

        Returns bytes consumed; only a header split across the end is left over (< 4 bytes).
        """
        b = ptr8(buf)
        f = ptr8(fb)
        s = ptr32(st)
        d = int(s[0])
        rem = int(s[1])
        i = 0
        while i < n:
            if rem:
                k = n - i
                if k > rem:
                    k = rem
                e = i + k
                while i < e:
                    f[d] = b[i]
                    d += 1
                    i += 1
                rem -= k
            else:
                if i + 4 > n:
                    break
                d += (int(b[i]) | (int(b[i + 1]) << 8)) * 2
                rem = (int(b[i + 2]) | (int(b[i + 3]) << 8)) * 2
                i += 4
        s[0] = d
        s[1] = rem
        return i
except (ImportError, AttributeError):  # host tests: same contract in plain Python
    def _apply(buf, n, fb, st):
        d, rem = st
        i = 0
        while i < n:
            if rem:
                k = min(n - i, rem)
                fb[d:d + k] = buf[i:i + k]
                d, i, rem = d + k, i + k, rem - k
            elif i + 4 > n:
                break
            else:
                d += (buf[i] | buf[i + 1] << 8) * 2
                rem = (buf[i + 2] | buf[i + 3] << 8) * 2
                i += 4
        st[0], st[1] = d, rem
        return i


class ClipPlayer:
    def __init__(self, fb, clear, path="{}-12.clp", chunk=CHUNK):
        self.fb, self.clear, self.path = fb, clear, path
        self.chunk = bytearray(chunk)
        self.view = memoryview(self.chunk)
        self.st = [0, 0]
        try:
            from array import array
            self.st = array("i", [0, 0])  # viper needs a real int32 buffer
        except ImportError:
            pass
        self.f = None
        self.state = None
        self.pending = IDLE
        self.cut = False
        self.idx = self.total = self.loop_off = 0
        self.period_ms = 83

    def request(self, state, now=False):
        """Queue `state` for the next loop boundary; now=True jump-cuts from idle (touch reactivity)."""
        if state not in STATES:
            raise ValueError("unknown state " + str(state))
        self.pending = state
        self.cut = now and self.state == IDLE and state != IDLE

    def _open(self, state):
        if self.f:
            self.f.close()
        self.f = open(self.path.format(state), "rb")
        head = self.f.read(12)
        if head[:4] != b"CLP1":
            raise ValueError("bad clip " + state)
        w, h, fps, n = struct.unpack("<HHHH", head[4:12])
        if w * h * 2 != len(self.fb):
            raise ValueError("clip size mismatch " + state)
        self.state, self.total, self.idx = state, n + 1, 0  # keyframe + n deltas, last is the wrap
        self.period_ms = 1000 // fps
        self.clear()

    def _frame(self):
        """Apply the frame at the file position; returns nothing."""
        f, chunk, view, st = self.f, self.chunk, self.view, self.st
        (remaining,) = struct.unpack("<I", f.read(4))
        st[0] = st[1] = left = 0
        while remaining or left:
            want = min(len(chunk) - left, remaining)
            if want:
                f.readinto(view[left:left + want])
                remaining -= want
            n = left + want
            used = _apply(chunk, n, self.fb, st)
            left = n - used
            if left:
                chunk[0:left] = chunk[used:n]
            if not used and not want:
                raise ValueError("corrupt clip")

    def step(self):
        """Apply the next frame. Returns the state it belongs to."""
        if self.f is None or self.idx >= self.total or self.cut:
            self.cut = False
            nxt, self.pending = self.pending, IDLE  # a gesture plays once, then idle
            if nxt == IDLE and self.state == IDLE:
                self.f.seek(self.loop_off)  # idle loops without redrawing the keyframe
                self.idx = 1
            else:
                self._open(nxt)
        self._frame()
        if self.idx == 0:
            self.loop_off = self.f.tell()
        self.idx += 1
        return self.state
