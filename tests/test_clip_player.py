import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "firmware/rp2040")]
from animation.clip_export import decode_clip, encode_clip  # noqa: E402
import clip_player  # noqa: E402

W, H = 8, 4


def frames(seed):
    out = []
    for k in range(3):
        f = bytearray(W * H * 2)
        for p in range(W * H):
            if (p + k * seed) % 5 == 0:
                f[p * 2:p * 2 + 2] = bytes([seed + k, 0x21])
        out.append(bytes(f))
    return out


class PlayerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ref = {}
        for name, seed in (("watch", 1), ("scratch", 2)):
            blob, _ = encode_clip(frames(seed), W, H, 12)
            Path(self.dir.name, name + "-12.clp").write_bytes(blob)
            self.ref[name] = decode_clip(blob)[3]  # frames incl. wrap
        self.fb = bytearray(W * H * 2)

    def player(self):
        def clear():
            self.fb[:] = bytes(len(self.fb))
        # tiny chunk forces runs to straddle chunk edges
        return clip_player.ClipPlayer(self.fb, clear, self.dir.name + "/{}-12.clp", chunk=6)

    def tearDown(self):
        if getattr(self, "p", None) and self.p.f:
            self.p.f.close()
        self.dir.cleanup()

    def test_real_clip_matches_reference(self):
        real = ROOT / "animation/tmp/look_around-12.clp"
        if not real.exists():
            self.skipTest("render and export look_around first")
        ref = decode_clip(real.read_bytes())
        w, h = ref[0], ref[1]
        fb = bytearray(w * h * 2)
        p = self.p = clip_player.ClipPlayer(
            fb, lambda: fb.__setitem__(slice(None), bytes(len(fb))), str(real.parent) + "/{}-12.clp")
        p.pending = "look_around"
        for i, frame in enumerate(ref[3]):
            p.step()
            self.assertEqual(bytes(fb), frame, i)

    def test_pixels_match_reference_through_loop_and_switch(self):
        p = self.p = self.player()
        plan = []
        for i in range(14):
            if i == 5:
                p.request("scratch")
            state = p.step()
            plan.append((state, bytes(self.fb)))
        # replay expectation: after each step fb == ref frame (idle loops skip the keyframe)
        idx = {"watch": 0, "scratch": 0}
        last = None
        for state, got in plan:
            ref = self.ref[state]
            if last != state or idx[state] >= len(ref):
                idx[state] = 0 if last != state else 1
            self.assertEqual(got, ref[idx[state]], (state, idx[state]))
            idx[state] += 1
            last = state


if __name__ == "__main__":
    unittest.main()
