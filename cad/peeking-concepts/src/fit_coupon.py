"""Fit-only; not latch/retention/strength qualification."""
from cadgen import build123d as bd, srgb, step, stl


@step(out="../STEP/fit_coupon.step")
@stl(out="../STL/fit_coupon.stl")
def fit_coupon():
    strip = bd.Box(45.0, 15.0, 3.0).moved(bd.Location((0.0, 0.0, 1.5)))
    for x, clearance in ((-14.0, 0.2), (0.0, 0.4), (14.0, 0.6)):
        hole = bd.Box(4.0 + clearance, 8.0 + clearance, 3.2)
        strip = strip - hole.moved(bd.Location((x, 0.0, 1.5)))
    strip.label = "fit_coupon_strip"
    strip.color = srgb("#3F718A")

    foot = bd.Box(8.0, 12.0, 2.0).moved(bd.Location((0.0, 14.0, 1.0)))
    peg = bd.Box(4.0, 8.0, 6.0).moved(bd.Location((0.0, 14.0, 5.0)))
    test_peg = foot + peg
    test_peg.label = "test_peg_with_foot"
    test_peg.color = srgb("#D68A35")
    return bd.Compound(children=[strip, test_peg], label="fit_coupon")


if __name__ == "__main__":
    fit_coupon()
