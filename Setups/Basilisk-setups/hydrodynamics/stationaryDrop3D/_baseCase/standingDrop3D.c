#include "navier-stokes/centered.h"
#include "two-phase.h"  //includes vof.h and simplifies setup for separated two-phase flows
#include "tension.h"
#include "output_vtu_foreach.h"
 

// Twophase standing droplet in 3D for _FLUIDPAIR_, Res: _GRID_, D=0.002m
// Evaluating max, average and derivation

// based on http://basilisk.fr/src/test/spurious.c a
// and for output see>http://basilisk.fr/sandbox/acastillo/output_fields/output_vtu_foreach.h 
// To compile: qcc -O2 -Wall -grid=octree standingDrop3D.c -o standingDrop3D -lm
// -grid=octree necessary to run simulation in 3D, default is 2D 
 

 
//Initialization

//Diameter of drop
#define D 0.002

//Domain size
#define WIDTH 0.01

FILE * fp = NULL;
  

//Time and grid constraints
const double tEnd = 0.1;
double dt, CFL;
const double gridRes = _GRID_;
char flPa[] = "_FLUIDPAIR_";

//BCs: default Neumann
 
 

int main() {

 
  size (WIDTH);                                 //quadratic domain size
  origin (-WIDTH/2., -WIDTH/2., -WIDTH/2.);    //place origin at center of domain

  init_grid (gridRes);                         //initialize grid

 
 
  //set fluid properties
  if ( strcmp(flPa,"water-air")==0 )
  {
    rho1 = 998.2;
    rho2 = 1.19;
    mu1 = 0.0009982;
    mu2 = 18.21e-6;
    f.sigma = 0.07274;
  }
  else if ( strcmp(flPa,"gearoil-air")==0 )
  {
    rho1 = 888.0;
    rho2 = 1.19;
    mu1 = 0.240648;
    mu2 = 18.21e-6;
    f.sigma = 0.0329;
  }
  else if ( strcmp(flPa,"oil_novec7500-water")==0 )
  {
    rho2 = 998.2;
    rho1 = 1614.0;
    mu2 = 0.0009982;
    mu1 = 0.00124278;
    f.sigma = 0.0495;
  }

  TOLERANCE = 1e-6;                 

  run();

}

 

 

 

//Initial actions
event init (i = 0) {

  //Initialize Drop at center of domain
  if (!restore (file = "dump-000")) {
    fraction (f, sq(D/2.) - sq(x) - sq(y)  - sq(z) );
  }
  
  //Set max timestep
  DT=sqrt( (pow(WIDTH/gridRes,3) *(rho1+rho2))/(2.0*3.141*f.sigma) );
  dtnext(DT);
  dt = DT; 
  //  CFL=0.5;



  //OUTPUT-FILES for spurious currents - max & average velocities
  char name[80];
  sprintf (name, "stationaryDrop3D_res%.0f_%s.basiliskDat",gridRes,flPa);

  if (fp)
      fclose (fp);
  fp = fopen (name, "w");
  fprintf (fp, "%s,%s,%s,%s,%s,%s,%s\n",
	   "SOLVER","FLUID_PAIRING","RESOLUTION","time","max_error_velocity","mean_absolute_error_velocity","root_mean_square_deviation_velocity");

}


// At every Timestep
event logfile (i++; t <= tEnd)
{
  scalar un[];
  foreach()
    un[] = norm(u);
  fprintf (fp, "%s,%s,%g,%g,%g,%g,%g\n",
	   "BASILISK", flPa, gridRes, t, normf(un).max, normf(un).avg, normf(un).rms);  //statsf() can be used as an alternative
	   
	   
   fprintf (stderr, "i = %d t = %g dt = %g\n", i, t, dt);
}
 

 
 
//Outputdata for Paraview
event outvtk (t = 0.00; t += tEnd/10.) {

  char subname[80];

  sprintf (subname, "VTK-Data/standingDrop_%.0f.vtu", 1000*t);

  FILE * fpvtu = fopen(subname, "w");

  output_vtu_bin_foreach  ((scalar *) {f, p}, (vector *) {u},t,fpvtu,false);

  fclose(fpvtu);


} 
 
 

//Endtime

event end (t = tEnd) {
  fclose (fp);
}
