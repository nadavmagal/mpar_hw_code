import math
import time
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np

def angle_diff(angle1, angle2):
    return np.arctan2(np.sin(angle1-angle2), np.cos(angle1-angle2))

def error_ellipse(position, sigma):

    covariance = sigma[0:2,0:2]
    eigenvals, eigenvecs = np.linalg.eig(covariance)

    #get largest eigenvalue and eigenvector
    max_ind = np.argmax(eigenvals)
    max_eigvec = eigenvecs[:,max_ind]
    max_eigval = eigenvals[max_ind]

    #get smallest eigenvalue and eigenvector
    min_ind = 0
    if max_ind == 0:
        min_ind = 1

    min_eigvec = eigenvecs[:,min_ind]
    min_eigval = eigenvals[min_ind]

    #chi-square value for sigma confidence interval
    chisquare_scale = 2.2789  

    #calculate width and height of confidence ellipse
    width = 2 * np.sqrt(chisquare_scale*max_eigval)
    height = 2 * np.sqrt(chisquare_scale*min_eigval)
    angle = np.arctan2(max_eigvec[1],max_eigvec[0])

    #generate covariance ellipse
    error_ellipse = Ellipse(xy=[position[0],position[1]], width=width, height=height, angle=angle/np.pi*180)
    error_ellipse.set_alpha(0.25)

    return error_ellipse

def plot_state(particles, landmarks, timestep, gt_trajectory, cur_date_time):
    # Visualizes the state of the particle filter.
    #
    # Displays the particle cloud, mean position and 
    # estimated mean landmark positions and covariances.

    draw_mean_landmark_poses = False
    SAVE_FIG = True

    map_limits = [-1, 12, 0, 10]
    
    #particle positions
    xs = []
    ys = []

    #landmark mean positions
    lxs = []
    lys = []

    for particle in particles:
        xs.append(particle['x'])
        ys.append(particle['y'])
        
        for i in range(len(landmarks)):
            landmark = particle['landmarks'][i+1]
            lxs.append(landmark['mu'][0])
            lys.append(landmark['mu'][1])

    # ground truth landmark positions
    lx=[]
    ly=[]

    for i in range (len(landmarks)):
        lx.append(landmarks[i+1][0])
        ly.append(landmarks[i+1][1])

    # best particle
    if False:
        weights = np.array([cur_p['weight'] for cur_p in particles])
    estimated = get_best_particle(particles)
    robot_x = estimated['x']
    robot_y = estimated['y']
    robot_theta = estimated['theta']

    # estimated traveled path of best particle
    hist = estimated['history']
    hx = []
    hy = []

    for pos in hist:
        hx.append(pos[0])
        hy.append(pos[1])

    # plot filter state
    plt.clf()

    #particles
    plt.plot(xs, ys, 'r.')
    
    if draw_mean_landmark_poses:
        # estimated mean landmark positions of each particle
        plt.plot(lxs, lys, 'b.')

    # estimated traveled path of best particle
    plt.plot(hx, hy, 'r-', label='history')

    # plot_gt
    hist_len = len(hx)
    plt.plot(gt_trajectory[:hist_len, 0], gt_trajectory[:hist_len, 1], color='black', label='GT')
    # true landmark positions
    plt.plot(lx, ly, 'b+',markersize=10)

    # draw error ellipse of estimated landmark positions of best particle 
    for i in range(len(landmarks)):
        landmark = estimated['landmarks'][i+1]

        ellipse = error_ellipse(landmark['mu'], landmark['sigma'])
        plt.gca().add_artist(ellipse)

    # draw pose of best particle
    plt.quiver(robot_x, robot_y, np.cos(robot_theta), np.sin(robot_theta), angles='xy',scale_units='xy')
    
    plt.axis(map_limits)
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.legend()

    plt.pause(0.01)
    if SAVE_FIG:
        save_path = f'/home/nadav/studies/mapping_and_perception_autonomous_robots/project_3/results/fast_slam/{cur_date_time}'
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f'{timestep}.png'), dpi=150)
    a=3

def get_best_particle(particles):
    #find particle with highest weight 

    highest_weight = 0

    best_particle = None
    
    for particle in particles:
        if particle['weight'] > highest_weight:
            best_particle = particle
            highest_weight = particle['weight']

    return best_particle

def get_average_history(particles):
    # find particle with highest weight

    avg_particle = dict()

    num_particles = len(particles)
    total_history = []
    for particle in particles:
        cur_particle_history = np.array(particle['history'])
        total_history.append(cur_particle_history)

    total_history = np.array(total_history)
    mean_history = np.mean(total_history, axis=0)

    return mean_history