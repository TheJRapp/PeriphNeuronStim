import misc_functions as mf
import plot as pt
import threshold as th
from neuron import h
import numpy as np
from Axon_Models import hh_cable_geometry
from Axon_Models import simple_cable_geometry
from Axon_Models import mrg_cable_geometry
from Axon_Models import mrg_parameters as ap
import sys
sys.path.insert(0, "C:/nrn/lib/python")
import neuron

from matplotlib import pyplot as plt

class NeuronSimNerveShape:

    def __init__(self, axon_model_parameter, nerve_shape, time_axis, stimulus, total_time):
        super(NeuronSimNerveShape, self).__init__()

        h.load_file('stdrun.hoc')
        h.celsius = 37
        h.dt = 0.001  # ms

        self.axon = self.generate_axon(axon_model_parameter, nerve_shape)
        self.nerve_shape = nerve_shape
        self.time_axis = time_axis
        self.stimulus = stimulus
        self.total_time = total_time
        self.e_field_along_axon = []
        self.potential_along_axon = []

    def generate_axon(self, mp, nerve_shape):
        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, nerve_shape)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, nerve_shape)
        else:
            axon = self.simple(mp.diameter, nerve_shape)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self, x):  # x not used here
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = self.quasi_potentials(self.stimulus, self.nerve_shape, self.axon)
        mf.play_stimulus_matrix(self.axon, self.time_axis)

    def simple(self, diameter, nerve_shape):
        segments = 1
        node_diameter = 0.3449 * diameter - 0.1484  # um; the formula is from Olivar Izard Master's thesis
        internode_diameter = diameter
        node_length = 1
        if diameter > 4:
            internode_length = 969.3 * np.log(diameter) - 1144.6
        else:
            internode_length = 100 * diameter

        x = nerve_shape.x[0]
        y = nerve_shape.y[0]
        z = nerve_shape.z[0]
        theta = []
        phi = []
        node_internode_pairs = []
        axons_number = 0
        step_size = 5
        for i in range(len(nerve_shape.x)-step_size)[::step_size]:
            length = np.sqrt((nerve_shape.x[i+step_size] - nerve_shape.x[i]) ** 2 + (nerve_shape.y[i+step_size] - nerve_shape.y[i]) ** 2
                             + (nerve_shape.z[i+step_size] - nerve_shape.z[i]) ** 2)
            # phi_c = np.arctan((nerve_shape.y[i+step_size] - nerve_shape.y[i]) / (nerve_shape.x[i+step_size] - nerve_shape.x[i]))
            phi_c = np.arctan2(
                (nerve_shape.y[i + step_size] - nerve_shape.y[i]), (nerve_shape.x[i + step_size] - nerve_shape.x[i]))
            theta_c = np.arctan(length / nerve_shape.z[i])
            node_internode_pairs_c = int(round(length / (node_length + internode_length)))
            if node_internode_pairs_c > 0:
                phi.append(phi_c)
                theta.append(theta_c)
                node_internode_pairs.append(node_internode_pairs_c)
                axons_number += 1

        simple_model = simple_cable_geometry.BendedAxon(theta, phi, axons_number, x, y, z, segments,
                                                        internode_diameter,
                                                        node_diameter, node_length, internode_length,
                                                        node_internode_pairs)
        # plt.figure()
        # plt.plot(simple_model.x)
        # plt.show()
        # plt.figure()
        # plt.plot(nerve_shape.x)
        # plt.show()
        # plt.figure()
        # plt.plot(simple_model.y)
        # plt.show()
        # plt.figure()
        # plt.plot(nerve_shape.y)
        # plt.show()
        # plt.figure()
        # plt.plot(simple_model.z)
        # plt.show()
        # plt.figure()
        # plt.plot(nerve_shape.z)
        # plt.show()

        return simple_model

    def quasi_potentials(self, stimulus, nerve_shape, cable):
        # quasi potential described by Aberra 2019
        # for(each segment)
        #   find e_field coordinates within segment +- deltaX +- deltaY +- deltaZ
        #   e_field_current = interpolate e_field
        #   quasi_pot_current = quasi_pot_prev - (1/2)(e_field_current + e_field_previous) * displacement #calc displacement from model?
        #   generate h.vector with (stimulus and e_field as amplitude) and (time_vector)
        #   play generated vector on segment.e_extracellular
        segment_list = cable.get_segments()

        stim_matrix = []  # contains a row for each segment where the corresponding e-field is multiplied w. stimulus
        e_field_along_axon = []
        quasi_pot_along_axon = []

        e_average_prev = 0
        quasi_pot_prev = 0
        step_vector = cable.get_segment_indices()
        segment_counter = 0
        for i, axon in zip(range(len(cable.axon_list)), cable.axon_list):
            for section in axon.sections:
                e_field_current = cable.get_unitvector()[int(step_vector[segment_counter])][0] * nerve_shape.e_x[i] + \
                                    cable.get_unitvector()[int(step_vector[segment_counter])][1] * nerve_shape.e_y[i] + \
                                    cable.get_unitvector()[int(step_vector[segment_counter])][2] * nerve_shape.e_z[i]

                if segment_counter == 0:
                    k = 1
                else:
                    k = segment_counter
                e_field_integral = (1 / 2) * (e_field_current + e_average_prev)
                displacement = np.sqrt(
                    (cable.x[k] - cable.x[k - 1]) ** 2 + (cable.y[k] - cable.y[k - 1]) ** 2 + (
                            cable.z[k] - cable.z[k - 1]) ** 2) * 1e-3
                quasi_pot_current = quasi_pot_prev - (e_field_integral * displacement)
                segment_counter += 1
                # quasi_pot_current in mV; displacement given in um
                #  units? displacement given in um, must me converted with 10e-6 for quasipotentials in V,
                #  but v_ext from NEURON is in mV !!!!!! --> 1e-3

                quasi_pot_prev = quasi_pot_current

                e_field_along_axon.append(e_field_current)
                stim_matrix.append(stimulus * quasi_pot_current)
                quasi_pot_along_axon.append(quasi_pot_current)

        return stim_matrix, e_field_along_axon, quasi_pot_along_axon
