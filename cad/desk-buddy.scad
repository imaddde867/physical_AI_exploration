// Original adjustable desk companion enclosure (millimeters).
// Measurements below are illustrative; measure actual components before printing.
// Open back allows service, USB and initial foam-tape mounting.
$fn = 36;
body_w = 78;
body_h = 76;
body_d = 44;
wall = 2.8;
screen_w = 28;  // visible window width: revise for purchased OLED
screen_h = 15;  // visible window height: revise for purchased OLED
base_w = 90;
base_d = 55;
base_h = 5;

module rounded_box(w,d,h,r=5) {
  hull() for(x=[-w/2+r,w/2-r],y=[-d/2+r,d/2-r])
    translate([x,y,0]) cylinder(r=r,h=h);
}
module shell() {
  difference() {
    union() {
      translate([0,0,base_h]) rounded_box(body_w,body_d,body_h,7);
      rounded_box(base_w,base_d,base_h,8);
    }
    // cavity opens at rear (negative Y), leaving front wall
    translate([0,-wall,base_h+wall])
      rounded_box(body_w-2*wall,body_d+wall,body_h,5);
    // display window on front face (+Y), at eye level
    translate([-screen_w/2,body_d/2-wall-1,base_h+body_h*0.54])
      cube([screen_w,wall+3,screen_h]);
    // USB/service exit in the bottom rear (size to be measured)
    translate([-7,-base_d/2-1,base_h+8])
      cube([14,wall+10,10]);
  }
}
shell();
