import misc_functions as mf
import plot as pt
import threshold_widget as th
from matplotlib import pyplot as plt
from neuron import h
import numpy as np
from scipy.interpolate import BSpline, make_interp_spline
from Axon_Models import hh_cable_geometry
from Axon_Models import simple_cable_geometry
from Axon_Models import mrg_cable_geometry
from Axon_Models import mrg_parameters as ap
from Axon_Models import mhh_model
import sys

sys.path.insert(0, "C:/nrn/lib/python")
import neuron


class NeuronSim:

    def __init__(self, static_e_field_list, radius, nerve_shape, nerve_step_size, axon_model_parameter, time_axis,
                 stimulus, total_time):
        super(NeuronSim, self).__init__()
        self.nerve_shape = nerve_shape
        self.step_size = nerve_step_size
        self.e_field_list = static_e_field_list
        self.interpolation_radius_index = radius

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
        if mp.axon_type == 'HH':
            axon = self.hh(mp.diameter, self.nerve_shape)
        elif mp.axon_type == 'RMG':
            axon = self.mrg(mp.diameter, self.nerve_shape)
        else:
            axon = simple_from_nerve_shape_working(mp.diameter, mp.nseg_node, mp.nseg_internode, self.nerve_shape,
                                                   self.step_size)

        mf.record_membrane_potentials(axon, 0.5)

        return axon

    def quasipot(self):
        self.axon.stim_matrix, self.axon.e_field_along_axon, self.axon.potential_along_axon, = mf.quasi_potentials(
            self.stimulus, self.e_field_list, self.axon, self.interpolation_radius_index)
        self.apply_potential_to_nerve()

    def mdf(self):
        return mf.driving_function(self.axon, self.stimulus)

    def apply_potential_to_nerve(self):
        '''
        This function was created to flatten the electric field at the end and at the start of the axon
        '''
        # --------------------------------- Comparing Stefan's pulses --------------------------------------------------

        # select segment which is closest to start point / stop point
        start = 100  # number of segment from start
        stop = 100  # number of segment from the end

        # Stepwise decrease potential along axon
        last_change_start = self.axon.potential_along_axon[start + 1] - self.axon.potential_along_axon[start]
        for i in range(start, 0, -1):
            self.axon.potential_along_axon[i - 1] = self.axon.potential_along_axon[i] - (0.8 * last_change_start)
            last_change_start = 0.8 * last_change_start

        last_change_stop = self.axon.potential_along_axon[- (stop + 1)] - self.axon.potential_along_axon[-stop]
        for i in range(stop, 1, -1):
            self.axon.potential_along_axon[- (i - 1)] = self.axon.potential_along_axon[-i] - (0.8 * last_change_stop)
            last_change_stop = 0.8 * last_change_stop

        self.axon.stim_matrix = []
        for pot in self.axon.potential_along_axon:
            self.axon.stim_matrix.append(self.stimulus * pot)

        mf.play_stimulus_matrix(self.axon, self.time_axis)

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
