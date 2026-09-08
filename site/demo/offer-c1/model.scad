// Generated from plan.json; millimetres. Not a structural design.
// Open in OpenSCAD. Increase explode_mm to inspect courses.
explode_mm = 0;
$fn = 24;
show_fixing_paths = false;

// offer-bed-01-C1-S
translate([0, 0, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// offer-bed-01-C1-N
translate([0, 1300, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([2400, 100, 200]);
// offer-bed-01-C1-W
translate([0, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1200, 200]);
// offer-bed-01-C1-E
translate([2300, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 1200, 200]);
if (show_fixing_paths) translate([50.0, 1400, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 1400, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1400, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 1400, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([2350.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
