#include "navier-stokes/centered.h"
#include "two-phase.h"  //includes vof.h and simplifies setup for separated two-phase flows
#include "tension.h"
#include "vtk.h"

 

// Translating droplet in 2D for _FLUIDPAIR_, Res: _GRID_, D=0.002m
// To compile: qcc -O2 -Wall translatingDrop2D.c -o translatingDrop2D -lm 
 

 
//Initialization

//Diameter of drop
#define D 0.002

//Domain size
#define WIDTH 0.02
#define HEIGHT 0.01
FILE * fp = NULL;
 

 

//Time and grid constraints
const double tEnd = 0.015;
double dt, CFL;
const double gridRes = _GRID_;
char flPa[] = "_FLUIDPAIR_";
 
//BCs:
u.n[left]  = dirichlet(1); 
p[left]    = neumann(0.);   

u.n[right] = neumann(0.);
p[right]   = dirichlet(0.);

u.n[bottom]  = dirichlet(0.);
u.t[bottom]  = neumann(0.);
p[bottom]   =  neumann(0.);

u.t[top]   = neumann(0.);
u.n[top]   = dirichlet(0.);
p[top]   =  neumann(0.)
 

int main() {

 
  size (WIDTH);                     //quadratic domain size
  init_grid (gridRes*WIDTH/HEIGHT);   //initialize grid

 
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

  //Reduce simulation domain to rectangle size
  mask (y > HEIGHT ? top : none);

  //Initialize Drop at center of domain
  if (!restore (file = "dump-000")) {

    fraction (f, sq(D/2.) - sq(x-0.002) - sq(y-0.005) );
  }


  //Initialize velocity
  foreach() {
      u.x[] = 1.;
  }
  boundary((scalar *){u});


  //Set max timestep
  CFL=0.2;

  
  //OUTPUT-FILES for spurious currents - max & average velocities
  char name[80];
  sprintf (name, "translatingDrop2D_res%.0f_%s.basiliskDat",gridRes,flPa);

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
  vector ured[]; 
  
  foreach()
  {
    ured.x[]= u.x[] - 1.;
    ured.y[]= u.y[];
  }
  
  foreach()
    un[] = norm(ured);
  fprintf (fp, "%s,%s,%g,%g,%g,%g,%g\n",
	   "BASILISK", flPa, gridRes, t, normf(un).max, normf(un).avg, normf(un).rms); 	   
	   
   fprintf (stderr, "i = %d t = %g dt = %g\n", i, t, dt);
}
 
 
 
 

//Endtime

event end (t = tEnd) {
  fclose (fp); 
}



 

event outvtk (t = 0.0; t += tEnd/10.) {

  char name1[80];

  sprintf (name1, "VTK-Data/translatingDrop-%.0f.vtk", 1000*t);

  FILE * fpvtk = fopen(name1, "w");
  output_vtk ({f, p, u.x, u.y},N,fpvtk,true);

  fclose(fpvtk);

}

 

 
