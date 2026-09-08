// Generated from plan.json; millimetres. Not a structural design.
// Open in OpenSCAD. Increase explode_mm to inspect courses.
explode_mm = 0;
$fn = 24;
show_fixing_paths = false;

// side-01-C1-S
translate([0, 0, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([1800, 100, 200]);
// side-01-C1-N
translate([0, 800, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([1800, 100, 200]);
// side-01-C1-W
translate([0, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 700, 200]);
// side-01-C1-E
translate([1700, 100, 0+0*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 700, 200]);
// side-01-C2-S
translate([100, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([1600, 100, 200]);
// side-01-C2-N
translate([100, 800, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([1600, 100, 200]);
// side-01-C2-W
translate([0, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 900, 200]);
// side-01-C2-E
translate([1700, 0, 200+1*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 900, 200]);
// side-01-C3-S
translate([0, 0, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([1800, 100, 200]);
// side-01-C3-N
translate([0, 800, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([1800, 100, 200]);
// side-01-C3-W
translate([0, 100, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 700, 200]);
// side-01-C3-E
translate([1700, 100, 400+2*explode_mm])
  color([0.70,0.52,0.33]) cube([100, 700, 200]);
if (show_fixing_paths) translate([50.0, 900, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 900, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 900, 50.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 900, 150.0+0*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 0, 50.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 0, 150.0+0*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1800, 50.0, 250.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1800, 50.0, 350.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1800, 850.0, 250.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1800, 850.0, 350.0+1*explode_mm]) rotate([0,-90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 200.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1750.0, 700.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([300.0, 850.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([900.0, 850.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1500.0, 850.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([300.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([900.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1500.0, 50.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([0, 50.0, 250.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 50.0, 350.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 850.0, 250.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([0, 850.0, 350.0+1*explode_mm]) rotate([0,90,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 200.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 700.0, 400+1*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1750.0, 340.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1750.0, 640.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 900, 450.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 900, 550.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 900, 450.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 900, 550.0+2*explode_mm]) rotate([90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([240.0, 850.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([706.667, 850.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1173.333, 850.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1620.0, 850.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 0, 450.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([50.0, 0, 550.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 0, 450.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([1750.0, 0, 550.0+2*explode_mm]) rotate([-90,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=150);
if (show_fixing_paths) translate([240.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([706.667, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1173.333, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([1620.0, 50.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 340.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
if (show_fixing_paths) translate([50.0, 640.0, 600+2*explode_mm]) rotate([180,0,0]) color([0.8,0.1,0.1]) cylinder(d=7, h=250);
