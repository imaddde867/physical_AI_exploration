import unittest

from experiments import occupant_still
from sim.screen import HEIGHT, WIDTH, Screen, rgb565


class OccupantTests(unittest.TestCase):
    def test_checkpoint_is_full_rgb565_frame_and_does_not_change(self):
        self.assertEqual(len(occupant_still.data), WIDTH * HEIGHT * 2)
        screen = Screen()
        occupant_still.update(screen, 0)
        snapshot = [row[:] for row in screen.rows()]
        occupant_still.update(screen, 5000)
        self.assertEqual(screen.rows(), snapshot)
        self.assertTrue(any(c != "#000000" for row in snapshot for c in row))
        self.assertTrue(all(row[0] == row[-1] == "#000000" for row in snapshot))
        for i, color in enumerate(occupant_still.RGB):
            self.assertEqual(rgb565(color), int.from_bytes(occupant_still.data[2*i:2*i+2], "little"))

    def test_idle_preserves_checkpoint_then_moves_only_local_regions(self):
        from experiments import occupant_idle
        screen = Screen()
        occupant_idle.update(screen, 0)
        self.assertEqual(screen.rows(), occupant_still.ROWS)
        occupant_idle.update(screen, 1450)
        moving = [row[:] for row in screen.rows()]
        self.assertNotEqual(moving, occupant_still.ROWS)
        self.assertEqual(moving[0], occupant_still.ROWS[0])
        self.assertEqual(moving[-1], occupant_still.ROWS[-1])
        for actual, original in zip(moving, occupant_still.ROWS):
            self.assertEqual(actual[:45], original[:45])
            self.assertEqual(actual[196:], original[196:])
        occupant_idle.update(screen, 8000)
        occupant_idle.update(screen, 1450)
        self.assertEqual(screen.rows(), moving)
        self.assertEqual(len(screen.rows()), HEIGHT)
        self.assertTrue(all(len(row) == WIDTH for row in screen.rows()))
        self.assertEqual(occupant_still.ROWS, [
            ["#%02x%02x%02x" % c for c in occupant_still.RGB[y * WIDTH:(y + 1) * WIDTH]]
            for y in range(HEIGHT)])


if __name__ == "__main__":
    unittest.main()
