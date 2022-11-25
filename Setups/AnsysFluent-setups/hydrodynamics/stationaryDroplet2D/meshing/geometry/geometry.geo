// Gmsh project created on Wed May 18 09:46:10 2022
SetFactory("OpenCASCADE");
//+
nx = 64;
dx = 10.;// mm!
Point(1) = {0, 0, 0, 1.0};
Point(2) = {0, dx, 0, 1.0};
Point(3) = {dx, 0, 0, 1.0};
Point(4) = {dx, dx, 0, 1.0};
//+
Line(1) = {1, 3};
Line(2) = {3, 4};
Line(3) = {4, 2};
Line(4) = {2, 1};
//+
Curve Loop(1) = {3, 4, 1, 2}; Plane Surface(1) = {1};
//+
Physical Curve("boundary") = {3, 2, 1, 4};
Physical Surface("domain") = {1};
//+
Save "geometry.step";
//+
Transfinite Curve {1, 2, 3, 4} = nx+1 Using Progression 1;
//+
Transfinite Surface {1} = {1, 3, 4, 2};

Mesh 2;
Recombine Surface {1};
//+
//+

