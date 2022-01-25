import misc_functions as mf
import plot as pt
import threshold_widget as th
from neuron import h
import numpy as np
from Axon_Models import hh_cable_geometry
from Axon_Models import simple_cable_geometry
from Axon_Models import mrg_cable_geometry
from Axon_Models import mrg_parameters as ap
import sys
sys.path.insert(0, "C:/nrn/lib/python")
import neuron


class NeuronSim:

    def __init__(self, axon_model_parameter, static_e_field_list, time_axis, stimulus, total_time):
        super(NeuronSim, self).__init__()

        h.load_file('stdrun.hoc')
        h.celsius = 37
        h.dt = 0.001  # ms

        self.axon = self.generate_axon(axon_model_parameter)
        self.e_field_list = static_e_field_list
        self.time_axis = time_axis
        self.stimulus = stimulus
        self.total_time = total_time
        self.e_field_along_axon = []
        self.potential_along_axon = []

    def generate_axon(self, mp):
        # mp = model parameters

        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
        else:
            axon = self.simple(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self, interpolation_radius_index):
        a = h.dt
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = mf.quasi_potentials(self.stimulus, self.e_field_list, self.axon, interpolation_radius_index)
        mf.play_stimulus_matrix(self.axon, self.time_axis)

    def simple_simulation(self):

        h.finitialize(-80)
        h.continuerun(self.total_time)

        ax1, ax2 = pt.plot_traces_and_field('Nodes: ' + self.axon.name, self.time_axis, self.stimulus, self.axon)
        return ax1, ax2

    def threshold_simulation(self, uni_stimulus, threshold_widget):
        threshold = threshold_widget.rough_to_fine_search(self.axon, self.total_time, self.time_axis, uni_stimulus)
        return threshold

    def hh(self, diameter, x, y, z, angle, length):
        segments = 1

        node_diameter = diameter  # um (?)
        node_length = 82
        axons_number = 1
        amount = round((length / node_length) / axons_number)
        number_of_nodes_per_unit_vector = amount
        phi = [angle / 360 * 2 * np.pi]
        theta = [90 / 360 * 2 * np.pi, 90 / 360 * 2 * np.pi]
        # phi = [np.pi / 2, np.pi / 2]

        hh_model = hh_cable_geometry.BendedAxon(theta, phi, axons_number, x, y, z, segments, node_diameter,
                                                node_length,
                                                number_of_nodes_per_unit_vector)

        return hh_model

    def simple(self, diameter, x, y, z, angle, length):
        segments = 1
        node_internode_pairs_per_unit_vector = []
        node_diameter = 0.3449 * diameter - 0.1484  # um; the formula is from Olivar Izard Master's thesis
        internode_diameter = diameter
        node_length = 1
        if diameter > 4:
            internode_length = 969.3 * np.log(diameter) - 1144.6
        else:
            internode_length = 100 * diameter
        axons_number = 1
        amount = int((length / (node_length + internode_length)) / axons_number)
        node_internode_pairs_per_unit_vector.append(amount)
        phi = [angle / 360 * 2 * np.pi]
        theta = [90 / 360 * 2 * np.pi, 90 / 360 * 2 * np.pi]
        # phi = [np.pi / 2, np.pi / 2]

        simple_model = simple_cable_geometry.BendedAxon(theta, phi, axons_number, x, y, z, segments,
                                                        internode_diameter,
                                                        node_diameter, node_length, internode_length,
                                                        node_internode_pairs_per_unit_vector)

        return simple_model

    def mrg(self, diameter, x, y, z, angle, length):
        parameter_collection = ap.AxonParameter(1, diameter)  # number of segments, cable diameter
        node_internode_length = parameter_collection.total_internode_length + parameter_collection.L_node
        axons_number = 1
        amount = round((length / node_internode_length) / axons_number)
        node_internode_pairs_per_unit_vector = amount

        phi = [angle / 360 * 2 * np.pi]
        theta = [90 / 360 * 2 * np.pi, 90 / 360 * 2 * np.pi]
        # phi = [np.pi / 2, np.pi / 2]

        mrg_model = mrg_cable_geometry.BendedAxon(parameters=parameter_collection, theta=theta, phi=phi,
                                                  axons_number=axons_number, x=x, y=y, z=z, STIN_number=6,
                                                  node_internode_pairs=node_internode_pairs_per_unit_vector)

        return mrg_model


class AxonInformation:
    def __init__(self, start_x, start_y, start_z, angle, length, diameter, axon_type):
        super(AxonInformation, self).__init__()
        self.x = start_x
        self.y = start_y
        self.z = start_z
        self.angle = angle
        self.length = length
        self.diameter = diameter
        self.axon_type = axon_type
