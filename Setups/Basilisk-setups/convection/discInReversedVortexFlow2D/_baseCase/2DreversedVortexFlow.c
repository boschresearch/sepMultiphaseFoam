#include "grid/cartesian.h"  
#include "advection.h"
#include "vof.h"
#include "vtk.h"
#include "utils.h"
 
// Disc in reversed vortex flow to test VoF advection with resolution _GRID_. Velocity field prescribed in each time step.
//  Speed up  with Cartesin mesh compared to Quadree
//based on http://basilisk.fr/src/test/reversed.c#time-reversed-vof-advection-in-a-vortex
// to compile: qcc -O2 -Wall 2DreversedVortexFlow.c -o 2DreversedVortexFlow -lm 
 

 
//Parameters
#define D 0.3       //Diameter of drop
#define WIDTH 1.0   //Domain size

FILE * fp = NULL;

//Time and grid constraints
const double tEnd = 3.0;
const double gridRes = _GRID_;
double dt, CFL;
 
scalar f[];
scalar * interfaces = {f}, * tracers = NULL;
 

 

int main()

{

  size (WIDTH);

  DT = 1e-5;  //max time step

  init_grid ( gridRes);
  
  run();


}

 



//Initialization

event init (i = 0) {

  fraction (f, sq(D/2.) - sq(x-0.5) - sq(y-0.75) );

  CFL=0.5; 
  DT = 1e-5;
  dtnext(DT);
  dt = DT; 

}



//Background velocity field
event velocity (i++) {
  trash ({u});

  foreach_face(x) u.x[] = cos(pi*t/tEnd)*(-2.*sin(pi*x)*sin(pi*x)*sin(pi*y)*cos(pi*y));
  foreach_face(y) u.y[] = cos(pi*t/tEnd)*(2.*sin(pi*y)*sin(pi*y)*sin(pi*x)*cos(pi*x));
}

 



 
// Log-File
event logfile (i++; t <= tEnd)
{
  fprintf (stderr, "i = %d t = %g dt = %g\n", i, t, dt);
}
 

 

//Evaluation
//reinitialise field e at end of simulation with the initial shape and compute the difference
event field (t = tEnd) {

  scalar e[];
  fraction (e, sq(D/2.) - sq(x-0.5) - sq(y-0.75) );
  
  double vol_end=statsf(e).sum;   //Volume sum, see utils.h -->  sum += dv()*f[];
  double vol_start=statsf(f).sum;

  foreach(){
    e[] -= f[];
    e[] = fabs(e[]);
  }
   
  double err_shape= statsf(e).sum;
  double err_vol=fabs(vol_end-vol_start);
   
  //OUTPUT-FILE for error
  char name[80];
  sprintf (name, "discInReversedVortexFlow2D-res%.0f.basiliskDat",gridRes);

  if (fp)
      fclose (fp);
  fp = fopen (name, "w");
  fprintf (fp, "%s,%s,%s,%s\n",
	   "SOLVER","RESOLUTION","L1_SHAPE_ERROR","VOLUME_ERROR");

  fprintf (fp, "%s,%g,%g,%g\n", "BASILISK", gridRes, err_shape, err_vol);

  fclose (fp); 


}

 

//VTK output
event outvtk (t = 0.0; t += tEnd/10.) {
  
  char name1[80];

  sprintf (name1, "VTK-Data/vortexTransport-%04g.vtk", t*1000);
  FILE * fpvtk = fopen(name1, "w");

  output_vtk ({f, u.x, u.y},N,fpvtk,true);

  fclose(fpvtk);

}


 

