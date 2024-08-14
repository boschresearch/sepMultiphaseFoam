import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"]

def select_images(path_images, start, end):
    """
    Select images for processing.
    
    Arg:
    - path_images (string): Path for images.
    - start (int): Start number of images.
    - end (int): End number of images.
    
    Returns:
    - selected_files (list): Selected images as list.
    """    
    
    # Regular expression to match the required filenames
    pattern = re.compile(r'^NX4-S3 Camera(\d{6})\.jpg$')
    
    # List to store the selected filenames
    selected_files = []

    # Iterate over each file in the directory
    for filename in os.listdir(path_images):
        match = pattern.match(filename)
        if match:
            file_number = int(match.group(1))
            if start <= file_number <= end:
                selected_files.append(filename)
                
    return selected_files


def define_ROI(region):
    """
    Extract the region of interest (ROI) for image processing.
    
    Arg:
    - region (string): Possible ROI (upstream, downstream, crevice, x-axis, y-axis).
    
    Returns:
    - x, y, w, h (int): Start x and y coordinates with width and height as pixels.
    """    
    # ROI for contact angle calculation
    if region == 'upstream':
        x, y, w, h = 30, 450, 420, 250
    elif region == 'downstream':
        x, y, w, h = 610, 450, 410, 250
    elif region == 'crevice':
        x, y, w, h = 460, 20, 120, 420
        
    # ROI for interface tracking
    elif region == 'x-axis':
        x, y, w, h = 30, 450, 970, 250
    elif region == 'y-axis':
        x, y, w, h = 460, 20, 120, 450
    else:
        print("Error: unknown ROI: " + region + ". Exiting.")
    
    return x, y, w, h

def detect_walls(image, roi_coords, n_lines, direction):    
    """
    Detect the channel walls in ROI via finding the darkest pixels along vertical/horizontal lines,
    the median value of the y/x-coordinates of the darkest pixels is returned.
    
    Arg:
    - image: Input image.
    - roi_coords (list): Coordinates of ROI as x, y, w, h.
    - n_lines (int): Number of vertical/horizontal lines for wall detection. 
    - direction (str): Direction of lines for wall detection ("vertical" for detecting vertical walls with 
                       horizontal lines, "horitonzal" for detecting horizontal walls with vertical lines).
    
    Returns:
    - top_wall_y (int): The y-coordinate of the top wall (median).
    - bottom_wall_y (int): The y-coordinate of the bottom wall (median).
    - left_wall_x (int): The x-coordinate of the left wall (median).
    - right_wall_x (int): The x-coordinate of the right wall (median).
    """    

    x, y, w, h = roi_coords
    roi_image = image[y:y+h, x:x+w]

    # Copy the image to draw the lines on
    #image_with_lines = cv2.cvtColor(roi_image, cv2.COLOR_GRAY2BGR)

    all_darkest_points = []
    
    if direction == 'horizontal':
        spacing = w // n_lines

        for i in range(n_lines):
            line_x = x + i * spacing

            # Draw the vertical line on the image_with_lines
            #cv2.line(image_with_lines, (line_x, y), (line_x, y + h), (0, 255, 0), 1)

            # Extract the column of pixels along the current line within the ROI
            line_pixels = roi_image[:, i * spacing]

            # Find the darkest points along this line
            min_val = np.min(line_pixels)
            min_indices = np.where(line_pixels == min_val)[0]

            # Save the coordinates of the darkest points
            darkest_points = [(line_x, y + idx) for idx in min_indices]
            all_darkest_points.extend(darkest_points)
            
    elif direction == 'vertical':
        spacing = h // n_lines

        for i in range(n_lines):
            line_y = y + i * spacing

            # Draw the horizontal line on the image_with_lines
            #cv2.line(image_with_lines, (x, line_y), (x + w, line_y), (0, 255, 0), 1)

            # Extract the row of pixels along the current line within the ROI
            line_pixels = roi_image[i * spacing, :]

            # Find the darkest points along this line
            min_val = np.min(line_pixels)
            min_indices = np.where(line_pixels == min_val)[0]

            # Save the coordinates of the darkest points
            darkest_points = [(x + idx, line_y) for idx in min_indices]
            all_darkest_points.extend(darkest_points)
            
    # Identify the y-coordinates of the horizontal walls
    if direction == 'horizontal':
        y_coords = [point[1] for point in all_darkest_points]
        unique_y_coords = sorted(set(y_coords))

        if len(unique_y_coords) >= 2:
            top_wall_y_coords = [coord for coord in y_coords if coord == unique_y_coords[0]]
            bottom_wall_y_coords = [coord for coord in y_coords if coord == unique_y_coords[-1]]

            # Calculate the median y-coordinates
            top_wall_y = int(np.median(top_wall_y_coords))
            bottom_wall_y = int(np.median(bottom_wall_y_coords))
        else:
            top_wall_y = None
            bottom_wall_y = None

        return top_wall_y, bottom_wall_y
    
    # Identify the x-coordinates of the vertical walls
    elif direction == 'vertical':
        x_coords = [point[0] for point in all_darkest_points]
        unique_x_coords = sorted(set(x_coords))

        if len(unique_x_coords) >= 2:
            left_wall_x_coords = [coord for coord in x_coords if coord == unique_x_coords[0]]
            right_wall_x_coords = [coord for coord in x_coords if coord == unique_x_coords[-1]]

            # Calculate the median x-coordinates
            left_wall_x = int(np.median(left_wall_x_coords))
            right_wall_x = int(np.median(right_wall_x_coords))
        else:
            left_wall_x = None
            right_wall_x = None

        return left_wall_x, right_wall_x
    
def detect_interface(roi_image, thres, poly_degree, residual_thres, max_trials, min_samples, direction):
    """
    Detect the interface as the darktest pixels in ROI and fit a polynomial for the interface pixels.
    
    Arg:
    - roi_image: ROI image.
    - thres (int): Threshold value to classify the pixel values.
    - poly_degree (int): Degree of the fitted polynomial.
    - residual_thres (float): Maximum residual for a data sample to be classified as an inlier.
    - max_trials (int): Maximum number of iterations for random sample selection.
    - min_samples (int or float): Minimum number of samples chosen randomly from original data.
    - direction (str): Direction of ROI (horizontal, vertical).
    
    Returns:
    - outlier_coordinates (list): Outlier coordinates of the darkest pixels.
    - inlier_coordinates (list): Inlier coordinates of the darkest pixels.
    - fitted_coordinates (list): Fitted polynomial coordinates of the darkest pixels.
    - full_coefficients (list): Coefficients of the fitted polynomial.
    """    
    
    _, dark_pixels_mask = cv2.threshold(roi_image, thres, 255, cv2.THRESH_BINARY_INV)

    # Find coordinates of dark pixels
    dark_pixels_coords = np.column_stack(np.where(dark_pixels_mask == 255))
    edge_points = dark_pixels_coords
    
    # Create RANSACRegressor with adjusted parameters
    ransac = make_pipeline(
        PolynomialFeatures(poly_degree),
        RANSACRegressor(
            residual_threshold=residual_thres,  # Adjust this threshold based on your data
            max_trials=max_trials,        # Increase the number of trials
            min_samples=min_samples        # Minimum number of samples to consider a fit
        )
    )

    if direction == 'horizontal':

        y_points = edge_points[:, 0].reshape(-1, 1)
        x_points = edge_points[:, 1]
        
        ransac.fit(y_points, x_points)
        #y_fit = y_points
        y_fit = np.linspace(min(y_points), max(y_points), 1000).reshape(-1, 1)
        x_ransac = ransac.predict(y_fit)
    
    elif direction == 'vertical':
        
        x_points = edge_points[:, 1].reshape(-1, 1)
        y_points = edge_points[:, 0]
        
        ransac.fit(x_points, y_points)
        #x_fit = x_points
        x_fit = np.linspace(min(x_points), max(x_points), 1000).reshape(-1, 1)
        y_ransac = ransac.predict(x_fit)


    # Get inliers mask
    inlier_mask = ransac.named_steps['ransacregressor'].inlier_mask_
    
    # Get the polynomial coefficients and intercept
    coeffs = ransac.named_steps['ransacregressor'].estimator_.coef_
    intercept = ransac.named_steps['ransacregressor'].estimator_.intercept_
    
    # Merge the intercept into the coefficients
    full_coefficients = np.insert(coeffs[1:], 0, intercept)
    
    outlier_coordinates = np.column_stack((x_points[~inlier_mask], y_points[~inlier_mask]))
    inlier_coordinates = np.column_stack((x_points[inlier_mask], y_points[inlier_mask]))
    
    if direction == 'horizontal':
        fitted_coordinates = np.column_stack((x_ransac, y_fit))                                             
    elif direction == 'vertical':
        fitted_coordinates = np.column_stack((x_fit, y_ransac))
    
    return outlier_coordinates, inlier_coordinates, fitted_coordinates, full_coefficients

def detect_interface_front(roi_image, thres, poly_degree, residual_thres, max_trials, min_samples, direction):
    """
    Detect the interface as the darktest pixels in ROI and fit a polynomial for the interface front pixels.
    
    Arg:
    - roi_image: ROI image.
    - thres (int): Threshold value to classify the pixel values.
    - poly_degree (int): Degree of the fitted polynomial.
    - residual_thres (float): Maximum residual for a data sample to be classified as an inlier.
    - max_trials (int): Maximum number of iterations for random sample selection.
    - min_samples (int or float): Minimum number of samples chosen randomly from original data.
    - direction (str): Direction of ROI (horizontal, vertical).
    
    Returns:
    - outlier_coordinates (list): Outlier coordinates of the darkest pixels.
    - inlier_coordinates (list): Inlier coordinates of the darkest pixels.
    - fitted_coordinates (list): Fitted polynomial coordinates of the darkest pixels.
    - full_coefficients (list): Coefficients of the fitted polynomial function.
    """    
    
    _, dark_pixels_mask = cv2.threshold(roi_image, thres, 255, cv2.THRESH_BINARY_INV)

    # Find coordinates of dark pixels
    dark_pixels_coords = np.column_stack(np.where(dark_pixels_mask == 255))
    
    # Keep only the darkest pixels for each y-coordinate with the largest x-coordinate (interface front)
    unique_y_coords = np.unique(dark_pixels_coords[:, 0])
    filtered_dark_pixels_coords = []

    for y_coord in unique_y_coords:
        x_coords_at_y = dark_pixels_coords[dark_pixels_coords[:, 0] == y_coord][:, 1]
        max_x_coord = np.max(x_coords_at_y)
        filtered_dark_pixels_coords.append([y_coord, max_x_coord])

    filtered_dark_pixels_coords = np.array(filtered_dark_pixels_coords)
    
    # Create RANSACRegressor with adjusted parameters
    ransac = make_pipeline(
        PolynomialFeatures(poly_degree),
        RANSACRegressor(
            residual_threshold=residual_thres,  # Adjust this threshold based on your data
            max_trials=max_trials,        # Increase the number of trials
            min_samples=min_samples        # Minimum number of samples to consider a fit
        )
    )

    if direction == 'horizontal':

        y_points = filtered_dark_pixels_coords[:, 0].reshape(-1, 1)
        x_points = filtered_dark_pixels_coords[:, 1]
        
        ransac.fit(y_points, x_points)
        y_fit = y_points
        #y_fit = np.linspace(min(y_points), max(y_points), 1000).reshape(-1, 1)
        x_ransac = ransac.predict(y_fit)
    
    elif direction == 'vertical':
        
        x_points = filtered_dark_pixels_coords[:, 1].reshape(-1, 1)
        y_points = filtered_dark_pixels_coords[:, 0]
        
        ransac.fit(x_points, y_points)
        x_fit = x_points
        #x_fit = np.linspace(min(x_points), max(x_points), 1000).reshape(-1, 1)
        y_ransac = ransac.predict(x_fit)


    # Get inliers mask
    inlier_mask = ransac.named_steps['ransacregressor'].inlier_mask_
    
    # Get the polynomial coefficients and intercept
    coeffs = ransac.named_steps['ransacregressor'].estimator_.coef_
    intercept = ransac.named_steps['ransacregressor'].estimator_.intercept_
    
    # Merge the intercept into the coefficients
    full_coefficients = np.insert(coeffs[1:], 0, intercept)
    
    outlier_coordinates = np.column_stack((x_points[~inlier_mask], y_points[~inlier_mask]))
    inlier_coordinates = np.column_stack((x_points[inlier_mask], y_points[inlier_mask]))
    
    if direction == 'horizontal':
        fitted_coordinates = np.column_stack((x_ransac, y_fit))                                             
    elif direction == 'vertical':
        fitted_coordinates = np.column_stack((x_fit, y_ransac))
    
    return outlier_coordinates, inlier_coordinates, fitted_coordinates, full_coefficients


def calculate_contact_angle(coeffs, wall_coordinate, direction):
    """
    Calculate the contact angle between the interface (fitted polynomial with a degree of three) and wall in a global approach.
    
    Arg:
    - coeffs (list): Coefficients of fitted polynomial function, starting with the coefficient of the lowest degree term.
    - wall_coordinate (int): Coordinate of wall (horizontal is y-coordinate and vertical is x-coordinate).
    - direction (str): Direction of ROI (horizontal, vertical).
    
    Returns:
    - theta_degree (float): The contact angle between the interface and wall in degree.
    """    
    
    # Calculate the derivative of the polynomial
    slope = coeffs[1] + 2*coeffs[2]*wall_coordinate + 3*coeffs[3]*wall_coordinate**2
    
    if direction == 'horizontal':
        theta_radian = np.arctan(1/slope)
        theta_degree = 180 - abs(np.degrees(theta_radian))
        
    elif direction == 'vertical':
        theta_radian = np.arctan(slope)
        theta_degree = 90 + abs(np.degrees(theta_radian))
        
    return theta_degree

def get_x_coordinate(points, y_value):
    """
    Get the x-coordinate of a pixel with known y-coordinate.
    
    Arg:
    - points (list): Interface pixels.
    - y_value (int): y-coordinate of the pixel.
    
    Returns:
    - x_value (int): x-coordinate of the pixel.
    """
    x_list = [x for x , y in points if y == y_value]
    x_value = np.median(x_list)
    return x_value

def get_y_coordinate(points, x_value):
    """
    Get the y-coordinate of a pixel with known x-coordinate.
    
    Arg:
    - points (list): Interface pixels.
    - x_value (int): x-coordinate of the pixel.
    
    Returns:
    - y_value (int): y-coordinate of the pixel.
    """
    y_list = [y for x , y in points if x == x_value]
    y_value = np.median(y_list)
    return y_value

def get_interface_points(points, wall1_cor, wall2_cor, n_pixels, direction):
    """
    Get the boundary points and middle point of the interface.
    
    Arg:
    - points (list): Interface pixels.
    - wall1_cor (int): Coordinate of one side wall (horizontal is y-coordinate and vertical is x-coordinate).
    - wall2_cor (int): Coordinate of the other side wall (horizontal is y-coordinate and vertical is x-coordinate).
    - n_pixels (int): Number of offset-pixels away from the channel wall as interface boundary.
    - direction (str): Direction of ROI (horizontal, vertical).
    
    Returns:
    - interface1_x, interface1_y (int): The x- and y-coordinate of the first boundary point of interface.
    - interface2_x, interface2_y (int): The x- and y-coordinate of the second boundary point of interface.
    - interfaceM_x, interfaceM_y (int): The x- and y-coordinate of the middle point of interface.
    """    
    
    if direction == 'horizontal':
        interface1_y = wall1_cor + n_pixels
        interface1_x = get_x_coordinate(points, interface1_y)
        interface2_y = wall2_cor - n_pixels
        interface2_x = get_x_coordinate(points, interface2_y)
        interfaceM_y = int((wall1_cor+wall2_cor)/2)
        interfaceM_x = get_x_coordinate(points, interfaceM_y)
        
    elif direction == 'vertical':
        interface1_x = wall1_cor + n_pixels
        interface1_y = get_y_coordinate(points, interface1_x)
        interface2_x = wall2_cor - n_pixels
        interface2_y = get_y_coordinate(points, interface2_x)
        interfaceM_x = int((wall1_cor+wall2_cor)/2)
        interfaceM_y = get_y_coordinate(points, interfaceM_x)
        
        
    return interface1_x, interface1_y, interface2_x, interface2_y, interfaceM_x, interfaceM_y

def cal_interface_movement(df, pixel_size, framerate, resolution):
    """
    Calculate the interface movement over time using pixel size and framerate.
    
    Args:
    - df: Dataframe from detect_interface/detect_interface_front.
    - pixel_size (float): Image pixel size.
    - framerate (int): Optical framerate for time calculation.
    - resolution (int): Image resolution.
    
    Return:
    - df: New dataframe.
    """
    
    # Time step size
    dt = 1/framerate
    
    for i in range(len(df.Image)):
        
        df.loc[i, 'time'] = (i + 1) * dt
        
        # Calculate interface displacement along x-axis
        df['X1'].values[i] *= pixel_size
        df['X2'].values[i] *= pixel_size
        df['Xm'].values[i] *= pixel_size
        df.loc[i, 'X_mean'] = (df['X1'].values[i] + df['X2'].values[i]) / 2
        df.loc[i, 'X_velocity'] = (df['X_mean'].values[i] - df['X_mean'].values[i-1])/dt
        
        # Calculate interface displacement along y-axis
        df['Y1'].values[i] = (resolution - df['Y1'].values[i]) * pixel_size
        df['Y2'].values[i] = (resolution - df['Y2'].values[i]) * pixel_size
        df['Ym'].values[i] = (resolution - df['Ym'].values[i]) * pixel_size
        df.loc[i, 'Y_mean'] = (df['Y1'].values[i] + df['Y2'].values[i]) / 2
        df.loc[i, 'Y_velocity'] = (df['Y_mean'].values[i] - df['Y_mean'].values[i-1])/dt
                
        # Calculate mean value of contact angle
        df.loc[i, 'theta_mean'] = (df['theta1'].values[i] + df['theta2'].values[i]) / 2
    
    return df

def data_visualization(df, model, path_results, title):
    """
    Visualize the temporal evolution of data using different models and save figure.
    
    Args:
    - df: Dataframe from detect_interface/detect_interface_front.
    - model (str): Model used for data visualization. 
                   (displacement-y, displacement-x, velocity, contact angle)
    - path_results (str): Path for saving the figures.
    - title (str): Title of figures.
    """
    
    # Plot interface displacement along y-axis: relevant for ROI "vertical"
    if model == 'displacement-y':
        plt.plot(df['time'].values, df['Y1'].values*1000, marker='x', color='#1f77b4', label='left')
        plt.plot(df['time'].values, df['Y2'].values*1000, marker='+', color='#ff7f0e', label='right')
        plt.plot(df['time'].values, df['Ym'].values*1000, marker='o', color='#2ca02c', label='middle')
        plt.xlabel('t [s]', fontsize=12)
        plt.ylabel('Interface displacement [mm]', fontsize=12)
        plt.grid()
        plt.legend()
        
    # Plot interface displacement along x-axis: relevant for ROI "horizontal"
    elif model == 'displacement-x':
        plt.plot(df['time'].values, df['X1'].values*1000, marker='x', color='#1f77b4', label='top')
        plt.plot(df['time'].values, df['X2'].values*1000, marker='+', color='#ff7f0e', label='bottom')
        plt.plot(df['time'].values, df['Xm'].values*1000, marker='o', color='#2ca02c', label='middle')
        plt.xlabel('t [s]', fontsize=12)
        plt.ylabel('Interface displacement [mm]', fontsize=12)
        plt.grid()
        plt.legend()
        
    # Plot interface velocity
    elif model == 'velocity':
        plt.plot(df['time'].values, df['X_velocity'].values*1000, marker='x', color='#1f77b4', label='x-direction')
        plt.plot(df['time'].values, df['Y_velocity'].values*1000, marker='+', color='#ff7f0e', label='y-direction')
        plt.xlabel('t [s]', fontsize=12)
        plt.ylabel('Interface velocity [mm/s]', fontsize=12)
        plt.grid()
        plt.legend()
    
    # Plot dynamic contact angle
    elif model == 'contact angle':
        plt.plot(df['time'].values, df['theta1'].values, marker='x', color='#1f77b4', label='top')
        plt.plot(df['time'].values, df['theta2'].values, marker='+', color='#ff7f0e', label='bottom')
        plt.plot(df['time'].values, df['theta_mean'].values, marker='o', color='#2ca02c', label='mean')
        plt.xlabel('t [s]', fontsize=12)
        plt.ylabel('Dynamic contact angle [degree]', fontsize=12)
        plt.grid()
        plt.legend()

    else:
        print("Error: unknown model: " + model + ". Exiting.")
        
    plt.savefig(os.path.join(path_results, model + '_' + title + '.png'), bbox_inches='tight', dpi=300)

def write_text(image, text, position):
    """
    Write text on the image with defined position.

    Args:
    - image : Orinigal image.
    - text (str): The text need to be written on image.
    - position (numpy.array):  The position of text on image.

    Returns:
    - image: Image with text.
    """
    # Define the font and size
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 0, 0)
    font_thickness = 2

    # Put the text on the image
    cv2.putText(image, text, position, font, font_scale, font_color, font_thickness)
    
    return image
