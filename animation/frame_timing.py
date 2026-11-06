"""Sample native animation time without changing its speed or repeating an endpoint."""
from fractions import Fraction
import math


def frame_times(start, end, source_fps, playback_fps):
    if end <= start or source_fps <= 0 or playback_fps <= 0:
        raise ValueError('A positive clip duration and frame rates are required')
    count = math.ceil(Fraction(end-start) * playback_fps / source_fps)
    return [float(Fraction(start) + Fraction(i * source_fps, playback_fps))
            for i in range(count)]
