#include "navier-stokes/centered.h"
#include "two-phase.h"  //includes vof.h and simplifies setup for separated two-phase flows
#include "tension.h"
#include "output_vtu_foreach.h"

#include "curvature.h"  //to use interface position for evaluation
 
// Twophase oscillating drop in 3D for _FLUIDPAIR_, Res:  _GRID_
// Evaluating half axis over time at center, drop with diameter 0.001

//based on http://basilisk.fr/src/test/oscillation.c
// to compile: qcc -O2 -Wall -grid=octree oscillatingDrop3D.c -o oscillatingDrop3D -lm 
 

 
//Initialization

//semiaxis of initialized drop
#define a 0.000525
#define b 0.00048795

//Domain size
#define WIDTH 0.005
#define BBOX  0.0064//bounding box to ensure 2^n grid


FILE * fp = NULL;
 

 

//Time and grid constraints
const double tEnd = 0.02;
double dt, CFL;
const double gridRes = _GRID_;
char flPa[] = "_FLUIDPAIR_";

 


int main() {

  size (BBOX);                                  //quadratic domain size
  origin (-WIDTH/2., -WIDTH/2.,-WIDTH/2.);      //place origin at center of domain
  init_grid (gridRes * BBOX/WIDTH);   //initialize grid

 
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

  //Reduce simulation domain to WIDTH size
  mask (y > WIDTH/2. ? top : none);
  mask (z > WIDTH/2. ? back : none);
  mask (x > WIDTH/2. ? right : none);


  //initializing slightly elliptic drop at center of domain
  if (!restore (file = "dump-000")) {

    fraction (f, 1. - ( sq(x)/sq(a) + (sq(y)+sq(z))/sq(b) ) ) ;
  }
  
  
  
  //Set max timestep
  DT=sqrt( (pow(WIDTH/gridRes,3) *(rho1+rho2))/(2.0*3.141*f.sigma) );
  dtnext(DT);
  dt = DT; 
  //  CFL=0.5;

  
  
  //OUTPUT-FILES for half axis
  char name[80];
  sprintf (name, "oscillatingDrop3D_res%.0f_%s.basiliskDat",gridRes,flPa);

  if (fp)
      fclose (fp);
  fp = fopen (name, "w");
  fprintf (fp, "%s,%s,%s,%s,%s\n",
	   "SOLVER","FLUID_PAIRING","RESOLUTION","time","major_semi_axis_length");
}



 

 
// At every Timestep 
event logfile (i++; t <= tEnd)
{
  //Determine IF postion und write max in x-direction
  scalar posx[];
  position (f, posx, {1,0,0});
  fprintf (fp,"%s,%s,%g,%g,%g\n",
	   "BASILISK", flPa, gridRes, t, statsf(posx).max);
	   
	//log-file   
  fprintf (stderr, "i = %d t = %g dt = %g\n", i, t, dt);
}




//Endtime
event end (t = tEnd) {
  fclose (fp); 
}



//Outputdata for Paraview
event outvtk (t = 0.00; t += tEnd/10.) {

  char subname[80];

  sprintf (subname, "VTK-Data/oscDrop3D_%.0f.vtu", 1000*t);
  FILE * fpvtu = fopen(subname, "w");
  output_vtu_bin_foreach  ((scalar *) {f, p}, (vector *) {u},t,fpvtu,false);

  fclose(fpvtu);
} 


 

 

 
