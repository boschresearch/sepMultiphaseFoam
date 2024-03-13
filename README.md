# Automated image analysis for contact angle calculation

This branch contains the jupyter notebook for the automated image analysis procedure for dynamic contact angle calculation proposed in the publication "Experimental study of dynamic wetting behavior through curved mictochannels with automated image analysis" [paper source].  

A subset of images from experimental results is provided here for users to test the algorithm.

## Contents

- Jupyter notebook for automated image analysis
- Images from experimental results with two working fluids and four microchannels. The number of pixels for defining the local tangents `n_pixels = 10` and the threshold value for contour detection `thres_value = 160` hold for all images, while the threshold distance value for finding the start and end point of interface contour`thres_dist` differentiates between different tests and is listed in following tables:
	- Water:
	
   Microchannel | 0.00011ml/s | 0.00025ml/s | 0.00067ml/s | 0.0011ml/s | 0.0018ml/s 
   --- | --- | --- | --- | --- |---   
   Variation 1  | 1.5         | 1.5         | -           | 2.5        | -        
   Variation 2  | 1.5         | 1.5         | -           | 1          | -        
   Variation 3  | 1.2         | 1.5         | -           | -          | 1.5        
  
	- 50% Glycerin-water mixture: 
	
   Microchannel | 0.00011ml/s | 0.00025ml/s | 0.0011ml/s 
   --- | --- | --- | ---
   Straight     | 1.2         | 1.2         | 1.2        
   
- Under each folder there are:
	- pre-processed images
	- sub-folder `postprocessed`: post-processed images with deteced interface contour and calculated dynamic conatct angle
	- sub-folder `results` : saved data in csv file, figures for temporal evolution of interface displcement and dynamic contact angle
      
For more details refer to paper [source].

## Usage

The algorithm can be used either with the provided serial of images or with own dataset from users.  

- With the provided serial of images: please use the above recommmanded `thres_value`, `thres_dist` and `n_pixels` for each dataset
- With own dataset: the users are suggested conduct testing with their own datasets to ascertain the optimal parameters `thres_value`, `thres_dist` and `n_pixels` before deploying the provided code directly
	
It should be mentioned that this method might not be suitable for images with either substantial or minimal differences (for example, images taken with low or high frame rate), which could lead to less reliable results.

## Packages

- opencv-python: 4.8.0.76
- numpy: 1.25.2
- pandas: 1.3.4

## Authors

Robert Bosch GmbH
