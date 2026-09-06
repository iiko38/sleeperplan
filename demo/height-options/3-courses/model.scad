// Generated from plan.json; millimetres. Not a structural design.
// Open in OpenSCAD. Increase explode_mm to inspect courses.
explode_mm = 0;
$fn = 24;
show_fixing_paths = false;

// front-01-C1-S
translate([0, 0, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// front-01-C1-N
translate([0, 1100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// front-01-C1-W
translate([0, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1000, 200]);
// front-01-C1-E
translate([2300, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1000, 200]);
// front-01-C2-S
translate([100, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([2200, 100, 200]);
// front-01-C2-N
translate([100, 1100, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([2200, 100, 200]);
// front-01-C2-W
translate([0, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1200, 200]);
// front-01-C2-E
translate([2300, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1200, 200]);
// front-01-C3-S
translate([0, 0, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// front-01-C3-N
translate([0, 1100, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// front-01-C3-W
translate([0, 100, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1000, 200]);
// front-01-C3-E
translate([2300, 100, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1000, 200]);
if (show_fixing_paths) translate([50.0, 1200, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 1200, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1200, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1200, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2400, 50.0, 250.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2400, 50.0, 350.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2400, 1150.0, 250.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2400, 1150.0, 350.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 200.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2350.0, 600.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2350.0, 1000.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([300.0, 1150.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([900.0, 1150.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1500.0, 1150.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2100.0, 1150.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([300.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([900.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1500.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2100.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([0, 50.0, 250.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 50.0, 350.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 1150.0, 250.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 1150.0, 350.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 200.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 600.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 1000.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2350.0, 340.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2350.0, 940.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 1200, 450.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 1200, 550.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1200, 450.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1200, 550.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([240.0, 1150.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([740.0, 1150.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1240.0, 1150.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1740.0, 1150.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2220.0, 1150.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 0, 450.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 550.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 450.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 550.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([240.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([740.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1240.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1740.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([2220.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 340.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 940.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
