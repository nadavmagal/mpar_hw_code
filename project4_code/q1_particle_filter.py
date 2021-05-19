import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from read_data import read_world, read_sensor_data


class ParticleFilter:
    def __init__(self, N):
        self.particles = self._init_particles(N)
        self.weights = np.ones(N)
        self.particles_history = []

    @staticmethod
    def _init_particles(N):
        length = 10 * np.sqrt(np.random.uniform(0, 1, N))
        angle = np.pi * np.random.uniform(0, 2, N)
        particles = np.vstack([length * np.cos(angle) + 5, length * np.sin(angle) + 5]).T
        return particles

    def get_particles(self):
        return self.particles

def get_odometry_trajectory(odometry):
    num_of_samples = odometry.shape[0]
    x = [0]
    y = [0]
    theta = [0]
    for ii in range(num_of_samples):
        # delta_rot_1 = sensor_data[(ii, 'odometry')]['r1']
        # delta_rot_2 = sensor_data[(ii, 'odometry')]['r2']
        # delta_trans = sensor_data[(ii, 'odometry')]['t']
        delta_rot_1 = odometry[ii, 0]
        delta_rot_2 = odometry[ii, 2]
        delta_trans = odometry[ii, 1]

        x.append(x[-1] + delta_trans * np.cos(theta[-1] + delta_rot_1))
        y.append(y[-1] + delta_trans * np.sin(theta[-1] + delta_rot_1))
        theta.append(theta[-1] + delta_rot_1 + delta_rot_2)
    trajectory = np.vstack([x, y, theta]).T

    return trajectory


def perform_particle_filter(landmarks, odometry, N):
    particle_filter = ParticleFilter(N)


    plt.figure()
    plt.scatter(landmarks[:, 0], landmarks[:, 1], color='blue', label='landmarks')
    plt.scatter(particle_filter.get_particles()[:, 0], particle_filter.get_particles()[:, 1], color='red', label='particles')
    plt.legend()
    plt.grid()
    plt.title('initial particles distribution')
    plt.xlabel('x[m]')
    plt.ylabel('y[m]')
    plt.show(block=False)
    a = 3


def main():
    landmarks_fp = r'/home/nadav/studies/mapping_and_perception_autonomous_robots/project_3/ParticleEX1/landmarks_EX1.csv'
    odometry_fp = r'/home/nadav/studies/mapping_and_perception_autonomous_robots/project_3/ParticleEX1/odometry.dat'

    landmarks = np.array(pd.read_csv(landmarks_fp, header=None))
    odometry = np.array(pd.read_csv(odometry_fp, header=None, delimiter=' '))[:, 1:]  # r1, trans, r2

    gt_trajectory = get_odometry_trajectory(odometry)

    if True:
        plt.figure()
        plt.scatter(gt_trajectory[:, 0], gt_trajectory[:, 1], color='black', label='GT trajectory')
        plt.scatter(landmarks[:, 0], landmarks[:, 1], color='blue', label='landmarks')
        plt.legend()
        plt.grid()
        plt.title('GT trajecory and landmarks')
        plt.xlabel('x[m]')
        plt.ylabel('y[m]')
        plt.show(block=False)

    sigma_rot1 = 0.01
    sigma_trans = 0.1
    sigma_rot2 = 0.01
    noised_odometry = odometry.copy()
    noised_odometry[:, 0] += np.random.normal(0, sigma_rot1, np.shape(odometry[:, 0]))
    noised_odometry[:, 1] += np.random.normal(0, sigma_trans, np.shape(odometry[:, 1]))
    noised_odometry[:, 2] += np.random.normal(0, sigma_rot2, np.shape(odometry[:, 2]))

    noised_trajectory = get_odometry_trajectory(noised_odometry)

    if True:
        plt.figure()
        plt.scatter(noised_trajectory[:, 0], noised_trajectory[:, 1], color='black', label='noised trajectory')
        plt.scatter(landmarks[:, 0], landmarks[:, 1], color='blue', label='landmarks')
        plt.legend()
        plt.grid()
        plt.title('noised trajecory and landmarks')
        plt.xlabel('x[m]')
        plt.ylabel('y[m]')
        plt.show(block=False)

    N = 100  # number of particles
    perform_particle_filter(landmarks, noised_odometry, N)


if __name__ == "__main__":
    np.random.seed(0)
    main()
