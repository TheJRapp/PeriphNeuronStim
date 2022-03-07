import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
import pandas as pd
import neuron_sim as ns
import neuron_sim_nerve_shape as ns_ns

import numpy as np
from numpy import random
from matplotlib import pyplot as pt
import threading, queue
import time
import copy
Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_monte_carlo_widget.ui")
Ui_AxonDiamSweepWidget, QWidget_AxonDiamSweep = uic.loadUiType("ui_parameter_widget.ui")

parameter_list = ['Axon Diam', 'Axon Position']


class MonteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):

    def __init__(self, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidget, self).__init__(parent)

        self.setupUi(self)
        self.stimulus = stimulus
        self.time_axis = time_axis
        self.total_time = total_time
        self.threshold_widget = threshold_widget
        self.parameter_list = []
        self.parameter_list_item_model = QtGui.QStandardItemModel(self.parameter_list_view)

        self.parameter_combobox.addItems(parameter_list)

        self.parameter_widget_list = []

        self.parameter_push_button.clicked.connect(self.add_parameter)
        self.parameter_list_view.clicked.connect(self.set_parameter_widget)
        self.delete_all_pushbutton.clicked.connect(self.delete_parameters)
        self.start_mc_button.clicked.connect(self.start_monte_carlo)

    def add_parameter(self):
        item = QtGui.QStandardItem(self.parameter_combobox.currentText())
        self.parameter_list.append(self.parameter_combobox.currentText())
        paramter_widget = ParameterWidget()
        paramter_widget.type = self.parameter_combobox.currentText()
        self.parameter_widget_list.append(paramter_widget)
        self.parameter_layout.addWidget(paramter_widget)
        self.parameter_list_item_model.appendRow(item)
        self.parameter_list_view.setModel(self.parameter_list_item_model)
        self.set_parameter_widget()

    def set_parameter_widget(self):
        for i, widget in zip(range(len(self.parameter_widget_list)), self.parameter_widget_list):
            if widget:
                self.parameter_widget_list[i].setVisible(False)
                if i == self.parameter_list_view.currentIndex().row():
                    self.parameter_widget_list[i].setVisible(True)

    def delete_parameters(self):
        self.parameter_list_item_model.clear()
        self.parameter_list_view.setModel(self.parameter_list_item_model)
        self.set_parameter_widget()
        self.parameter_list = []

    def start_monte_carlo(self):
        if self.parameter_combobox.currentText() == 'Axon Diam':
            self.start_mc_diam_pos_sweep()

    def start_mc_diam_pos_sweep(self):

        mean_gamma = 9.33  # micrometer
        stdev_gamma = 2.1  # micrometer

        mean_alpha = 15.287  # micrometer
        stdev_alpha = 2.133  # micrometer

        start_pos_offset_mean = 0
        start_pos_offset_stdev = 15000

        mean_stim_gamma = 1
        stdev_stim_gamma = 0.1

        mean_stim_alpha = 0.5
        stdev_stim_alpha = 0.05

        runs = 100

        diameters_gamma = []
        diameters_alpha = []
        start_pos_offset_x = []
        start_pos_offset_y = []
        start_pos_offset_z = []
        stimulus_gamma = []
        stimulus_alpha = []
        for i in range(runs):
            helper = False
            while not helper:
                normal_distribution_1 = random.normal(mean_gamma, stdev_gamma)
                if (mean_gamma + 2*stdev_gamma) > normal_distribution_1 > (mean_gamma - 2*stdev_gamma):
                    helper = True
                    diameters_gamma.append(normal_distribution_1)
            helper = False
            while not helper:
                normal_distribution_2 = random.normal(mean_alpha, stdev_alpha)
                if (mean_alpha + 2*stdev_alpha) > normal_distribution_2 > (mean_alpha - 2*stdev_alpha):
                    helper = True
                    diameters_alpha.append(normal_distribution_2)

            # normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
            # start_pos_offset_x.append(normal_distribution_3)
            # normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
            # start_pos_offset_y.append(normal_distribution_3)
            helper = False
            while not helper:
                normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
                if (start_pos_offset_mean + 2*start_pos_offset_stdev) > normal_distribution_3 > (start_pos_offset_mean - 2*start_pos_offset_stdev):
                    helper = True
                    start_pos_offset_z.append(normal_distribution_3)
            helper = False
            while not helper:
                normal_distribution = random.normal(mean_stim_gamma, stdev_stim_gamma)
                if (mean_stim_gamma + 2*stdev_stim_gamma) > normal_distribution > (mean_stim_gamma - 2*stdev_stim_gamma):
                    helper = True
                    stimulus_gamma.append(normal_distribution)
            helper = False
            while not helper:
                normal_distribution = random.normal(mean_stim_alpha, stdev_stim_alpha)
                if (mean_stim_alpha + 2*stdev_stim_alpha) > normal_distribution > (mean_stim_alpha - 2*stdev_stim_alpha):
                    helper = True
                    stimulus_alpha.append(normal_distribution)

        # ----- diameter / coil distance -------------------------------------------------------------------------------
        diameters_gamma.sort()
        start_pos_offset_z.sort()
        start = time.time()
        stimulation_success_1 = []
        result_dict = {}
        result_dict['Offset'] = start_pos_offset_z
        for diam, i in zip(diameters_gamma, range(len(diameters_gamma))):
            # stimulation_success_1.append(self.run_diam_position_simulation(diam, -6000))
            print('Diam: ', diam, ', ', stimulation_success_1)
            result_dict[str(diam)] = []

            for j in range(len(start_pos_offset_z)):
                print('Run, ', j, '/', runs)
                is_stimulated = self.run_diam_position_simulation(diam, start_pos_offset_z[j])
                stimulation_success_1.append(is_stimulated)
                result_dict[str(diam)].append(is_stimulated)
        print("Elapsed time:  %s " % (time.time() - start))

        df = pd.DataFrame(result_dict)
        df.to_csv('20220304_mc_diam_vs_coil_distance_gamma_half_cosine_200us_intensity1_volume_300mm.csv', index=False, header=True)
        results = np.asarray(stimulation_success_1)
        results = np.reshape(results, (runs, runs))

        fig8 = pt.figure(2)
        ax8 = fig8.gca()
        ax8 = pt.imshow(results, extent=[start_pos_offset_z[0]/1000, start_pos_offset_z[-1]/1000, diameters_gamma[-1], diameters_gamma[0]])

        original_stimulus = self.stimulus
        self.stimulus = [number / 2 for number in self.stimulus]
        diameters_alpha.sort()
        start_pos_offset_z.sort()
        start = time.time()
        stimulation_success_2 = []
        result_dict = {}
        result_dict['Offset'] = start_pos_offset_z
        for diam, i in zip(diameters_alpha, range(len(diameters_alpha))):
            # stimulation_success_1.append(self.run_diam_position_simulation(diam, -6000))
            print('Diam: ', diam, ', ', stimulation_success_2)
            result_dict[str(diam)] = []

            for j in range(len(start_pos_offset_z)):
                print('Run, ', j, '/', runs)
                is_stimulated = self.run_diam_position_simulation(diam, start_pos_offset_z[j])
                stimulation_success_2.append(is_stimulated)
                result_dict[str(diam)].append(is_stimulated)
        print("Elapsed time:  %s " % (time.time() - start))

        df = pd.DataFrame(result_dict)
        df.to_csv('20220304_mc_diam_vs_coil_distance_alpha_half_cosine_200us_intensity1_volume_300mm.csv', index=False, header=True)
        results = np.asarray(stimulation_success_2)
        results = np.reshape(results, (runs, runs))

        fig3 = pt.figure(3)
        ax3 = fig3.gca()
        ax3 = pt.imshow(results, extent=[start_pos_offset_z[0]/1000, start_pos_offset_z[-1]/1000, diameters_gamma[-1], diameters_gamma[0]])

        self.stimulus = original_stimulus

        # ----- diameter / coil current --------------------------------------------------------------------------------
        stimulus_gamma.sort()
        start = time.time()
        stimulation_success_3 = []
        result_dict = {}
        result_dict['Stimulus'] = stimulus_gamma
        for diam, i in zip(diameters_gamma, range(len(diameters_gamma))):
            # stimulation_success_1.append(self.run_diam_position_simulation(diam, -6000))
            print('Diam: ', diam, ', ', stimulation_success_3)
            print('Run, ', i, '/', runs)
            result_dict[str(diam)] = []

            for j in range(len(stimulus_gamma)):
                print('Run, ', j, '/', runs)

                self.stimulus = [number * stimulus_gamma[j] for number in self.stimulus]
                is_stimulated = self.run_diam_position_simulation(diam, 0)
                stimulation_success_3.append(is_stimulated)
                result_dict[str(diam)].append(is_stimulated)
                self.stimulus = original_stimulus
        print("Elapsed time:  %s " % (time.time() - start))

        df = pd.DataFrame(result_dict)
        df.to_csv('20220304_mc_diam_vs_coil_current_gamma_half_cosine_200us_volume_300mm.csv', index=False, header=True)
        results = np.asarray(stimulation_success_3)
        results = np.reshape(results, (runs, runs))

        fig4 = pt.figure(4)
        ax4 = fig4.gca()
        ax4 = pt.imshow(results, extent=[start_pos_offset_z[0]/1000, start_pos_offset_z[-1]/1000, diameters_gamma[-1], diameters_gamma[0]])

        stimulus_alpha.sort()
        start = time.time()
        stimulation_success_4 = []
        result_dict = {}
        result_dict['Stimulus'] = stimulus_alpha
        for diam, i in zip(diameters_alpha, range(len(diameters_alpha))):
            # stimulation_success_1.append(self.run_diam_position_simulation(diam, -6000))
            print('Diam: ', diam, ', ', stimulation_success_4)
            print('Run, ', i, '/', runs)
            result_dict[str(diam)] = []

            for j in range(len(stimulus_alpha)):
                print('Run, ', j, '/', runs)

                self.stimulus = [number * stimulus_alpha[j] for number in self.stimulus]
                is_stimulated = self.run_diam_position_simulation(diam, 0)
                stimulation_success_4.append(is_stimulated)
                result_dict[str(diam)].append(is_stimulated)
                self.stimulus = original_stimulus
        print("Elapsed time:  %s " % (time.time() - start))

        df = pd.DataFrame(result_dict)
        df.to_csv('20220304_mc_diam_vs_coil_current_alpha_half_cosine_200us_volume_300mm.csv', index=False, header=True)
        results = np.asarray(stimulation_success_3)
        results = np.reshape(results, (runs, runs))

        fig5 = pt.figure(5)
        ax5 = fig5.gca()
        ax5 = pt.imshow(results, extent=[start_pos_offset_z[0]/1000, start_pos_offset_z[-1]/1000, diameters_gamma[-1], diameters_gamma[0]])


        pt.show()

        return stimulation_success_1

    def run_diam_simulation(self, diam):
        raise NotImplementedError()

    # def run_diam_position_simulation(self, diam, start_pos_offset_x, start_pos_offset_y, start_pos_offset_z):
    #     raise NotImplementedError()

    def run_diam_position_simulation(self, diam, start_pos_offset_z):
        raise NotImplementedError()


class MonteCarloWidgetNerveShape(MonteCarloWidget):
    def __init__(self, nerve_shape, nerve_step_size, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidgetNerveShape, self).__init__(stimulus, time_axis, total_time, threshold_widget, parent)
        self.nerve_shape = nerve_shape
        self.nerve_step_size = nerve_step_size

    def run_diam_simulation(self, diam):
        axon_info = ns.AxonInformation(0, 0, 0, 0, 0, diam, 'MHH')
        neuron_sim = ns.NeuronSimNerveShape(axon_info, self.nerve_shape, self.nerve_step_size, self.time_axis, self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class MonteCarloWidgetEField(MonteCarloWidget):
    def __init__(self, e_field_list, interpolation_radius, nerve, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidgetEField, self).__init__(stimulus, time_axis, total_time, threshold_widget, parent)

        self.e_field_list = e_field_list
        self.nerve = nerve
        self.interpolation_radius_index = interpolation_radius

    def run_diam_simulation(self, diam):
        axon_info = ns.AxonInformation(self.nerve.x, self.nerve.y, self.nerve.z, self.nerve.angle, self.nerve.length,
                                       diam, 'MHH')
        neuron_sim = ns.NeuronSimEField(axon_info, self.e_field_list, self.interpolation_radius_index, self.time_axis,
                                        self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class MonteCarloWidgetEFieldWithNerveShape(MonteCarloWidget):
    def __init__(self, e_field_list, interpolation_radius, nerve_shape, nerve_step_size, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidgetEFieldWithNerveShape, self).__init__(stimulus, time_axis, total_time, threshold_widget, parent)

        self.e_field_list = e_field_list
        self.interpolation_radius_index = interpolation_radius
        self.nerve_shape = nerve_shape
        self.nerve_step_size = nerve_step_size

    def run_diam_simulation(self, diam):
        axon_info = ns.AxonInformation(0, 0, 0, self.nerve.angle, self.nerve.length,
                                       diam, 'MHH')
        neuron_sim = ns.NeuronSimEFieldWithNerveShape(axon_info, self.e_field_list, self.interpolation_radius_index,
                                                      self.nerve_shape, self.nerve_step_size, self.time_axis,
                                                      self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0

    # def run_diam_position_simulation(self, diam, start_pos_offset_x, start_pos_offset_y, start_pos_offset_z):
    def run_diam_position_simulation(self, diam, start_pos_offset_z):
        axon_info = ns.AxonInformation(0, 0, 0, 0, 0, diam, 'MHH')
        # self.nerve_shape.x = self.nerve_shape.x + start_pos_offset_x
        # self.nerve_shape.y = self.nerve_shape.y + start_pos_offset_y
        internal_nerve_shape = copy.copy(self.nerve_shape)
        internal_nerve_shape.z = internal_nerve_shape.z + start_pos_offset_z
        neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_list, self.interpolation_radius_index,
                                                      internal_nerve_shape, self.nerve_step_size, axon_info, self.time_axis,
                                                      self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        # fig3 = pt.figure(3)
        # neuron_sim.plot_simulation()
        # pt.show()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class ParameterWidget(QWidget_AxonDiamSweep, Ui_AxonDiamSweepWidget):

    def __init__(self, parent = None):
        super(ParameterWidget, self).__init__(parent)

        self.setupUi(self)
        self.type = None


