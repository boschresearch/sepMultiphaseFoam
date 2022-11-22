#include "advection.h"
#include "vof.h"
#include "vtk.h"
#include "utils.h"

// Disc transported in 2D with diagonal frozen flow field to test VoF advection
// Flow field reversed after t=2s with resolution _GRID_ .
// based on http://basilisk.fr/src/test/reversed.c#time-reversed-vof-advection-in-a-vortex
// to compile: qcc -O2 -Wall 2DreversedDiagonalFlow.c -o 2DreversedDiagonalFlow -lm 
 

 

 
//Parameters
#define D 0.5         //Diameter of drop
#define WIDTH 3.0     //Domain width
#define HEIGHT 2.0    //Domain height
#define BBOX 4.26666  //Grid bounding box

FILE * fp = NULL;

//Time and grid constraints
const double tEnd = 4.0;
const double gridRes = _GRID_;
double dt, CFL;

scalar f[];
scalar * interfaces = {f}, * tracers = NULL;

 

int main()
{

  size (BBOX);
  
  init_grid (ceil(gridRes*BBOX/HEIGHT));
  
  run();

}

 



//Initialization

event init (i = 0) {
  //Reduce simulation domain to rectangle size 3x2
  mask (y > HEIGHT ? top : none);
  mask (x > WIDTH ? right : none);
  
  fraction (f, sq(D/2.) - sq(x-0.5) - sq(y-0.5) );


  CFL=0.5; 
  DT = 1e-5;
  dtnext(DT);
  dt = DT; 

}

 

//Backround velocity field

event velocity (i++) {
  trash ({u});
  struct { double x, y; } vel = {1.,0.5}; 
  if (t <= 2.0){
    foreach_face()
      u.x[]= vel.x;
      }
  else{
      foreach_face()
        u.x[]= -1.*vel.x; 
      }
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
  fraction (e, sq(D/2.) - sq(x-0.5) - sq(y-0.5) );
  
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
  sprintf (name, "discInReversedDiagonalFlow2D-res%.0f.basiliskDat",gridRes);

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

  sprintf (name1, "VTK-Data/diagonalTransport-%04g.vtk", t*1000);
  FILE * fpvtk = fopen(name1, "w");

  output_vtk ({f, u.x, u.y},N,fpvtk,true);

  fclose(fpvtk);

}



 

