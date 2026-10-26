// MacDesk Buddy: open-back compact case with circular IPS LCD aperture.
// Parametric prototype in mm; measure physical boards before final printing.
// Round GC9A01 active area diameter 32.4 mm, supplier PCB ~44 x 36 x 5 mm.
// To test the window cheaply first, set part = "fit_coupon".
$fn = 96;
part = "shell"; // ["shell","fit_coupon"]
body_w = 72;
body_h = 73;
body_d = 43;
body_r = 12;
base_w = 82;
base_d = 54;
base_h = 5.5;
wall = 2.8;
opening_d = 31.4;       // hides ~0.5mm of screen edge per side
face_height = 48.0;     // center of display above top of base
bezel_outer_d = 37.0;  // rim surrounds circular aperture
bezel_rise = 0.9;

module rounded_prism(w,d,h,r) {
  hull() {
    for (x=[-w/2+r,w/2-r], y=[-d/2+r,d/2-r])
      translate([x,y,0]) cylinder(r=r,h=h);
  }
}
module front_round_hole(diameter, length) {
  translate([0,body_d/2-wall-0.8,base_h+face_height])
    rotate([-90,0,0]) cylinder(d=diameter,h=length);
}
module shell() {
  difference() {
    union() {
      rounded_prism(base_w,base_d,base_h,9);
      translate([0,0,base_h])
        rounded_prism(body_w,body_d,body_h,body_r);
      translate([0,body_d/2-0.2,base_h+face_height])
        rotate([-90,0,0]) difference() {
          cylinder(d=bezel_outer_d,h=bezel_rise+0.2);
          translate([0,0,-0.1])
            cylinder(d=opening_d,h=bezel_rise+0.5);
        }
    }
    // Rear open, front wall preserved; no unverified board mount geometry.
    translate([-body_w/2+wall,-body_d/2-3,base_h+wall])
      cube([body_w-2*wall,body_d-wall+3,body_h-2*wall]);
    front_round_hole(opening_d,wall+bezel_rise+2);
  }
}
module fit_coupon() {
  difference() {
    rounded_prism(47,47,wall,5);
    translate([0,0,-0.3]) cylinder(d=opening_d,h=wall+0.6);
  }
}
if (part=="shell") shell();
else if (part=="fit_coupon") fit_coupon();
