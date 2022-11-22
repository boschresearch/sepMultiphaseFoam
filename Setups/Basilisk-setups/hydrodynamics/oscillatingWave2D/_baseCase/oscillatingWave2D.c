#include "navier-stokes/centered.h"
#include "two-phase.h"  //includes vof.h and simplifies setup for separated two-phase flows
#include "tension.h"
#include "vtk.h"
#include "curvature.h"  //to use interface position for evaluation


// Twophase oscillating wave in 2D  for _FLUIDPAIR_, Res:  _GRID_
// Evaluating amplitude over time at center

// based on http://www.basilisk.fr/sandbox/qmagdelaine/marangoni/capwave_integral.c

// to compile: qcc -O2 -Wall oscillatingWave2D.c -o oscillatingWave2D -lm 
 

 
//Initialization

//Wave parameters - amplitude
#define a 5.5e-5

//Domain size
#define WIDTH 0.0026



FILE * fp = NULL;
 

 

//Time and grid constraints
const double tEnd = 0.065;
double dt, CFL;
const double gridRes = _GRID_;
char flPa[] = "_FLUIDPAIR_";
 

 

int main() {

  size (WIDTH);                     //quadratic domain size
  origin (-WIDTH/2., 0.);           

  init_grid (gridRes);              //initialize grid

 
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

  if (!restore (file = "dump-000")) {
    //initializing slightly elliptic drop at center of domain
    fraction (f, a*cos(2.*pi/WIDTH*(x-WIDTH/2.)) + WIDTH/2. - y);

  }
  
  //Set max timestep
  DT=sqrt( (pow(WIDTH/gridRes,3) *(rho1+rho2))/(2.0*3.141*f.sigma) );
  dtnext(DT);
  dt = DT;  
  
  //OUTPUT-FILES for wave height
  char name[80];
  sprintf (name, "waveHeight_res%.0f_%s.basiliskDat",gridRes,flPa);

  if (fp)
      fclose (fp);
  fp = fopen (name, "w");
  fprintf (fp, "%s,%s,%s,%s,%s\n",
	   "SOLVER","FLUID_PAIRING","RESOLUTION","time","amplitude_at_center");
	   
}


 
// At every timestep write interface heigt at center
event logfile (i++; t <= tEnd)
{
  	scalar pos[];
	  position (f, pos, {0,1});
	  double x_min=100., pos_x_0=0;
	  
	  foreach(){
		  if(pos[]!=nodata){
			  if (x_min>x){
				  x_min = x;
				  pos_x_0 = pos[]-WIDTH/2.;
			  }
		  }
	  }

  fprintf (fp,"%s,%s,%g,%g,%g\n",
	   "BASILISK", flPa, gridRes, t, pos_x_0);
	  fflush (fp);	
	
	
	  
	//log-file   
  fprintf (stderr, "i = %d t = %g dt = %g\n", i, t, dt);
}



//Endtime

event end (t = tEnd) {
  fclose (fp); 
}



 

event outvtk (t = 0.0; t += tEnd/10.) {

  char name1[80];

  sprintf (name1, "VTK-Data/oscillatingWave-%.0f.vtk", 1000*t);

  FILE * fpvtk = fopen(name1, "w");

  output_vtk ({f, p, u.x, u.y},N,fpvtk,true);

  fclose(fpvtk);

}

 

 

 
