#include "advection.h"
#include "vof.h"
#include "output_vtu_foreach.h"
#include "utils.h"
 
// Sphere in reversed vortex flow to test VoF advection with resolution _GRID_. Velocity field prescribed in each time step.
// based on http://basilisk.fr/src/test/reversed.c#time-reversed-vof-advection-in-a-vortex
// to compile: qcc -O2 -Wall -grid=octree 3DreversedVortexFlow.c -o 3DreversedVortexFlow -lm 
// -grid=octree necessary to run simulation in 3D, default is 2D 

 
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

  init_grid ( gridRes);
  
  run();

}

 



//Initialization

event init (i = 0) {

  fraction (f, sq(D/2.) - sq(x-0.35) - sq(y-0.35) - sq(z-0.35));

  CFL=0.5; 
  DT = 1e-5;
  dtnext(DT);
  dt = DT; 

}



//Background velocity field
event velocity (i++) {
  trash ({u});
  foreach_face(x)   u.x[] = 2.*cos(pi*t/tEnd)*sin(pi*x)*sin(pi*x)*sin(2.*pi*y)*sin(2.*pi*z);
  foreach_face(y)   u.y[] = -1.*cos(pi*t/tEnd)*sin(pi*y)*sin(pi*y)*sin(2.*pi*x)*sin(2.*pi*z);
  foreach_face(z)   u.z[] = -1.*cos(pi*t/tEnd)*sin(pi*z)*sin(pi*z)*sin(2.*pi*x)*sin(2.*pi*y);

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
  fraction (e, sq(D/2.) - sq(x-0.35) - sq(y-0.35) - sq(z-0.35) );
  
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
  sprintf (name, "sphereInReversedVortexFlow3D-res%.0f.basiliskDat",gridRes);

  if (fp)
      fclose (fp);
  fp = fopen (name, "w");
  fprintf (fp, "%s,%s,%s,%s\n",
	   "SOLVER","RESOLUTION","L1_SHAPE_ERROR","VOLUME_ERROR");

  fprintf (fp, "%s,%g,%g,%g\n", "BASILISK", gridRes, err_shape, err_vol);

  fclose (fp); 


}

 
//Outputdata for Paraview
event outvtk (t = 0.00; t += tEnd/10.) {

  char subname[80];

  sprintf (subname, "VTK-Data/vortexTransport-%.0f.vtu", t*1000);

  FILE * fpvtu = fopen(subname, "w");

  output_vtu_bin_foreach  ((scalar *) {f}, (vector *) {u},t,fpvtu,false);

  fclose(fpvtu);


} 

 

 

