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

    def __init__(self, axon_model_parameter, time_axis, stimulus, total_time):
        super(NeuronSim, self).__init__()

        h.load_file('stdrun.hoc')
        h.celsius = 37
        h.dt = 0.001  # ms

        self.axon = self.generate_axon(axon_model_parameter)
        self.time_axis = time_axis
        self.stimulus = stimulus[0]
        self.uni_stimulus = stimulus[1]
        self.total_time = total_time
        self.e_field_along_axon = []
        self.potential_along_axon = []

    def generate_axon(self, mp):
        raise NotImplementedError()

    def quasipot(self):
        raise NotImplementedError()

    def simple_simulation(self):

        h.finitialize(-80)
        h.continuerun(self.total_time)

    def plot_simulation(self):
        ax1, ax2 = pt.plot_traces_and_field('Nodes: ' + self.axon.name, self.time_axis, self.stimulus, self.axon)
        return ax1, ax2

    def threshold_simulation(self, threshold_widget):
        threshold = threshold_widget.rough_to_fine_search(self.axon, self.total_time, self.time_axis, self.uni_stimulus)
        return threshold

    def is_axon_stimulated(self, threshold_widget):
        if not self.axon.potential_vector_list:
            print('No potential list in model')
            return False
        event = threshold_widget.event_detector(self.axon.potential_vector_list)
        if event == 2:
            return True
        else:
            return False


class NeuronSimEField(NeuronSim):

    def __init__(self, static_e_field_list, radius, axon_model_parameter, time_axis, stimulus, total_time):
        super(NeuronSimEField, self).__init__(axon_model_parameter, time_axis, stimulus, total_time)

        self.e_field_list = static_e_field_list
        self.interpolation_radius_index = radius

    def generate_axon(self, mp):
        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
        else:
            axon = self.simple(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self):
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = mf.quasi_potentials(
            self.stimulus, self.e_field_list, self.axon, self.interpolation_radius_index)
        mf.play_stimulus_matrix(self.axon, self.time_axis)

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


class NeuronSimNerveShape(NeuronSim):

    def __init__(self, nerve_shape, nerve_step_size, axon_model_parameter, time_axis, stimulus, total_time):
        self.nerve_shape = nerve_shape
        self.step_size = nerve_step_size

        super(NeuronSimNerveShape, self).__init__(axon_model_parameter, time_axis, stimulus, total_time)

    def generate_axon(self, mp):
        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, self.nerve_shape)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, self.nerve_shape)
        else:
            axon = simple_from_nerve_shape(mp.diameter, self.nerve_shape, self.step_size)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self):  # x not used here
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = self.quasi_potentials(self.stimulus, self.nerve_shape, self.axon)
        mf.play_stimulus_matrix(self.axon, self.time_axis)

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
        offset = 0
        for i, axon in zip(range(len(cable.axon_list)), cable.axon_list):
            for section in axon.sections:

                min_dist = np.argmin(np.sqrt((nerve_shape.x - cable.x[segment_counter]) ** 2 +
                                             (nerve_shape.y - cable.y[segment_counter]) ** 2 +
                                             (nerve_shape.z - cable.z[segment_counter]) ** 2))

                e_field_current = cable.get_unitvector()[int(step_vector[segment_counter])][0] * nerve_shape.e_x[
                    min_dist] + \
                                  cable.get_unitvector()[int(step_vector[segment_counter])][1] * nerve_shape.e_y[
                                      min_dist] + \
                                  cable.get_unitvector()[int(step_vector[segment_counter])][2] * nerve_shape.e_z[
                                      min_dist]

                e_field_current = e_field_current - offset
                if segment_counter == 0:
                    k = 1
                    offset = e_field_current
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

                e_average_prev = e_field_current
                quasi_pot_prev = quasi_pot_current

                e_field_along_axon.append(e_field_current)
                stim_matrix.append(stimulus * quasi_pot_current)
                quasi_pot_along_axon.append(quasi_pot_current)

        return stim_matrix, e_field_along_axon, quasi_pot_along_axon


class NeuronSimEFieldWithNerveShape(NeuronSim):

    def __init__(self, static_e_field_list, radius, nerve_shape, nerve_step_size, axon_model_parameter, time_axis, stimulus, total_time):
        self.nerve_shape = nerve_shape
        self.step_size = nerve_step_size

        super(NeuronSimEFieldWithNerveShape, self).__init__(axon_model_parameter, time_axis, stimulus, total_time)

        self.e_field_list = static_e_field_list
        self.interpolation_radius_index = radius

    def generate_axon(self, mp):
        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, self.nerve_shape)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, self.nerve_shape)
        else:
            axon = simple_from_nerve_shape(mp.diameter, self.nerve_shape, self.step_size)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self):
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = mf.quasi_potentials(
            self.stimulus, self.e_field_list, self.axon, self.interpolation_radius_index)
        mf.play_stimulus_matrix(self.axon, self.time_axis)

    def mdf(self):
        return mf.driving_function(self.axon, self.stimulus)


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


def simple_from_nerve_shape_old(diameter, nerve_shape, step_size):
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
    step_size = step_size
    for i in range(len(nerve_shape.x) - step_size)[::step_size]:
        length = np.sqrt((nerve_shape.x[i + step_size] - nerve_shape.x[i]) ** 2 + (
                    nerve_shape.y[i + step_size] - nerve_shape.y[i]) ** 2
                         + (nerve_shape.z[i + step_size] - nerve_shape.z[i]) ** 2)
        phi_c = np.arctan2(
            (nerve_shape.y[i + step_size] - nerve_shape.y[i]),
            (nerve_shape.x[i + step_size] - nerve_shape.x[i]))
        theta_c = np.arccos(((nerve_shape.z[i + step_size] - nerve_shape.z[i]) / length))
        test = nerve_shape.z[i] / length
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
    return simple_model


def simple_from_nerve_shape(diameter, nerve_shape, step_size):
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
    step_size = step_size
    for i in range(len(nerve_shape.x) - step_size)[::step_size]:
        if i == 0:
            last_x = nerve_shape.x[i]
            last_y = nerve_shape.y[i]
            last_z = nerve_shape.z[i]

        length = np.sqrt((nerve_shape.x[i + step_size] - last_x) ** 2 + (
                    nerve_shape.y[i + step_size] - last_y) ** 2
                         + (nerve_shape.z[i + step_size] - last_z) ** 2)
        phi_c = np.arctan2(
            (nerve_shape.y[i + step_size] - last_y),
            (nerve_shape.x[i + step_size] - last_x))
        theta_c = np.arccos(((nerve_shape.z[i + step_size] - last_z) / length))
        test = nerve_shape.z[i] / length
        node_internode_pairs_c = int(round(length / (node_length + internode_length)))
        if node_internode_pairs_c > 0:
            phi.append(phi_c)
            theta.append(theta_c)
            node_internode_pairs.append(node_internode_pairs_c)
            axons_number += 1
            # for pair in range(node_internode_pairs_c):
            #     phi.append(phi_c/node_internode_pairs_c)
            #     theta.append(theta_c/node_internode_pairs_c)
            #     axons_number += 1
            #     node_internode_pairs.append(1)

            last_x = nerve_shape.x[i+step_size]
            last_y = nerve_shape.y[i+step_size]
            last_z = nerve_shape.z[i+step_size]

    simple_model = simple_cable_geometry.BendedAxon(theta, phi, axons_number, x, y, z, segments,
                                                    internode_diameter,
                                                    node_diameter, node_length, internode_length,
                                                    node_internode_pairs)
    return simple_model