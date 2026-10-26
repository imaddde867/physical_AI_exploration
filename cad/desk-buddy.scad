// MacDesk Buddy: original adjustable open-back desktop enclosure.
// All dimensions in mm. Nominal values are placeholders, not verified fit.
// Change part to "fit_coupon" to test the OLED window before printing full case.
$fn = 48;
part = "shell"; // ["shell", "fit_coupon"]
body_w = 74;
body_h = 76;
body_d = 44;
base_w = 90;
base_d = 57;
base_h = 5;
wall = 2.8;
corner_r = 7;
// Visible aperture, not PCB dimensions; OLED nominal PCB ~26-27mm across.
window_w = 21.5;
window_h = 11.0;
window_z_fraction = 0.61;

module rounded_prism(w, d, h, r) {
  hull() for (x = [-w/2 + r, w/2 - r], y = [-d/2 + r, d/2 - r])
    translate([x, y, 0]) cylinder(r = r, h = h);
}
module shell() {
  difference() {
    union() {
      rounded_prism(base_w, base_d, base_h, 7);
      translate([0, 0, base_h])
        rounded_prism(body_w, body_d, body_h, corner_r);
    }
    // Open back (-Y), preserve the top, floor, front and side walls.
    translate([-body_w/2 + wall, -body_d/2 - 2, base_h + wall])
      cube([body_w - 2*wall, body_d - wall + 2, body_h - 2*wall]);
    // Front window: leaves lip around nominal 26-27mm OLED PCB.
    translate([-window_w/2, body_d/2 - wall - 0.3,
               base_h + body_h*window_z_fraction - window_h/2])
      cube([window_w, wall + 1, window_h]);
  }
}
module fit_coupon() {
  difference() {
    cube([40, 40, wall]);
    translate([(40-window_w)/2, (40-window_h)/2, -0.5])
      cube([window_w, window_h, wall + 1]);
  }
}
if (part == "fit_coupon") fit_coupon();
else if (part == "shell") shell();
