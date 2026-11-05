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


if __name__ == "__main__":
    unittest.main()
