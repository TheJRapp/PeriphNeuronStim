import numpy as np
import neuron_sim as ns

# ToDo: Insert distribution of (a) axon diameters, (b) axon starting points within radius around centre point
class Nerve():

    def __init__(self, x, y, z, length, angle, nerv_diam, name):

        self.axon_infos_list = []
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

        self.length = length
        self.name = name
        self.nerve_diameter = nerv_diam
        self.axon_distribution_number = 6
        # self.add_models()

    # def add_models(self):
        # for i in range(self.axon_distribution_number):
        #     alpha = i * (360 / self.axon_distribution_number)
        #
        #     x_offset = np.cos(alpha / 360 * 2 * np.pi)
        #     z_offset = np.sin(alpha / 360 * 2 * np.pi)
        #
        #     x = round(self.x + x_offset)
        #     z = round(self.z + z_offset)
        # if self.hh_diam_list:
        #     for i in self.hh_diam_list:
        #         model_info = ns.AxonInformation(self.x, self.y, self.z, self.length, i, 'HH')
        #         self.axon_infos_list.append(model_info)
        #
        # if self.simple_diam_list:
        #     for j in self.simple_diam_list:
        #         model_info = ns.AxonInformation(self.x, self.y, self.z, self.length, j, 'MHH')
        #         self.axon_infos_list.append(model_info)
        #
        # if self.mrg_diam_list:
        #     for k in self.mrg_diam_list:
        #         model_info = ns.AxonInformation(self.x, self.y, self.z, self.length, k, 'RMG')
        #         self.axon_infos_list.append(model_info)
