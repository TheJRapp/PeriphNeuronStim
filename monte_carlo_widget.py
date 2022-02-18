import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import neuron_sim as ns
import neuron_sim_nerve_shape as ns_ns

import numpy as np
from numpy import random
from matplotlib import pyplot as pt
import threading, queue
import time
Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_monte_carlo_widget.ui")
Ui_AxonDiamSweepWidget, QWidget_AxonDiamSweep = uic.loadUiType("ui_nerve_dimension_widget.ui")

parameter_list = ['Axon Diam', 'Axon Position']


class MonteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):

    def __init__(self, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidget, self).__init__(parent)

        self.setupUi(self)
        self.stimulus = stimulus
        self.time_axis = time_axis
        self.total_time = total_time
        self.threshold_widget = threshold_widget

        self.parameter_combobox.addItems(parameter_list)

        self.axon_diam_widget = AxonDiamSweepWidget()
        self.parameter_layout.addWidget(self.axon_diam_widget)
        self.axon_diam_widget.setVisible(False)

        self.parameter_combobox.currentTextChanged.connect(self.set_parameter_widget)
        self.start_mc_button.clicked.connect(self.start_monte_carlo)

    def set_parameter_widget(self):
        if self.parameter_combobox.currentText() == "Axon Diam":
            self.axon_diam_widget.setVisible(True)
        else:
            self.axon_diam_widget.setVisible(False)

    def start_monte_carlo(self):
        if self.parameter_combobox.currentText() == 'Axon Diam':
            self.start_mc_diam_pos_sweep()

    def start_mc_diam_pos_sweep(self):

        mean_1 = 9.33  # micrometer
        stdev_1 = 2.1  # micrometer

        mean_2 = 15.287  # micrometer
        stdev_2 = 2.133  # micrometer

        start_pos_offset_mean = 0
        start_pos_offset_stdev = 3000

        runs = 5

        diameters_1 = []
        diameters_2 = []
        start_pos_offset_x = []
        start_pos_offset_y = []
        start_pos_offset_z = []
        for i in range(runs):
            normal_distribution_1 = random.normal(mean_1, stdev_1)
            diameters_1.append(normal_distribution_1)
            normal_distribution_2 = random.normal(mean_2, stdev_2)
            diameters_2.append(normal_distribution_2)
            normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
            start_pos_offset_x.append(normal_distribution_3)
            normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
            start_pos_offset_y.append(normal_distribution_3)
            normal_distribution_3 = random.normal(start_pos_offset_mean, start_pos_offset_stdev)
            start_pos_offset_z.append(normal_distribution_3)

        # start = time.time()
        # q = queue.Queue()
        # for diam in range(11):
        #     threading.Thread(target=self.run_diam_simulation).start()
        # q.join()
        # print("Elapsed time:  %s " % (time.time() - start))

        start = time.time()
        stimulation_success_1 = []
        for diam, i in zip(diameters_1, range(len(diameters_1))):
            for j in range(len(start_pos_offset_x)):
                print('Run, ', i*j, '/', runs*runs)
                stimulation_success_1.append(self.run_diam_position_simulation(diam, start_pos_offset_z[j]))
        print("Elapsed time:  %s " % (time.time() - start))

        results = np.asarray(stimulation_success_1)
        results = np.reshape(results, (runs, runs))
        fig8 = pt.figure(2)
        ax8 = fig8.gca()
        ax8 = pt.imshow(results)
        ax8.set_xticks(start_pos_offset_z)
        ax8.set_yticks(diameters_1)
        ax8.set_xlabel('Offset in um')
        ax8.set_ylabel('Diameter')
        pt.show()

        # stimulation_success_1 = []
        # for diam, i in zip(diameters_1, range(len(diameters_1))):
        #     print('Diam1, ', i, '/', runs)
        #     stimulation_success_1.append(self.run_diam_simulation(diam))
        # print("Elapsed time:  %s " % (time.time() - start))
        #
        # start = time.time()
        # stimulation_success_2 = []
        # for diam, i in zip(diameters_2, range(len(diameters_2))):
        #     print('Diam2, ', i, '/', runs)
        #     stimulation_success_2.append(self.run_diam_simulation(diam))
        # print("Elapsed time:  %s " % (time.time() - start))

        # print(stimulation_success_1)
        # print(stimulation_success_2)
        # return stimulation_success_1

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
        self.nerve_shape.z = self.nerve_shape.z + start_pos_offset_z
        neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_list, self.interpolation_radius_index,
                                                      self.nerve_shape, self.nerve_step_size, axon_info, self.time_axis,
                                                      self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class AxonDiamSweepWidget(QWidget_AxonDiamSweep, Ui_AxonDiamSweepWidget):

    def __init__(self, parent = None):
        super(AxonDiamSweepWidget, self).__init__(parent)

        self.setupUi(self)
