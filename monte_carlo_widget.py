import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import neuron_sim as ns
import neuron_sim_nerve_shape as ns_ns

from numpy import random
from multiprocessing.pool import ThreadPool
import time
Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_monte_carlo_widget.ui")
Ui_AxonDiamSweepWidget, QWidget_AxonDiamSweep = uic.loadUiType("ui_nerve_dimension_widget.ui")

parameter_list = ['Axon Diam', 'Axon Position']


class monteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):

    def __init__(self, e_field_list, interpolation_radius, nerve, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(monteCarloWidget, self).__init__(parent)

        self.setupUi(self)
        self.e_field_list = e_field_list
        self.nerve = nerve
        self.interpolation_radius_index = interpolation_radius
        self.stimulus = stimulus
        self.time_axis = time_axis
        self.total_time = total_time
        self.threshold_widget = threshold_widget

        self.parameter_combobox.addItems(parameter_list)

        self.axon_diam_widget = axonDiamSweepWidget()
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
            self.start_mc_diam_sweep()

    def start_mc_diam_sweep(self):

        mean_1 = 9.33  # micrometer
        stdev_1 = 2.1  # micrometer

        mean_2 = 15.287  # micrometer
        stdev_2 = 2.133  # micrometer

        runs = 5

        diameters_1 = []
        diameters_2 = []
        for i in range(runs):
            normal_distribution_1 = random.normal(mean_1, stdev_1)
            diameters_1.append(normal_distribution_1)
            normal_distribution_2 = random.normal(mean_2, stdev_2)
            diameters_2.append(normal_distribution_2)

        start = time.time()
        t = ThreadPool()
        stimulation_success = t.map(self.run_diam_simulation, range(0, runs))
        print("Elapsed time:  %s " % (time.time() - start))
        return stimulation_success

    def run_diam_simulation(self, value):
        mean = 9.33  # micrometer
        stdev = 2.1  # micrometer
        diam = random.normal(mean, stdev)
        axon_info = ns.AxonInformation(self.nerve.x, self.nerve.y, self.nerve.z, self.nerve.angle, self.nerve.length,
                                       diam, 'MHH')
        neuron_sim = ns.NeuronSim(axon_info, self.e_field_list, self.time_axis, self.stimulus, self.total_time)

        # check if stimulation was successfull (eventdetector threshold widget)
        neuron_sim.quasipot(self.interpolation_radius_index)
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class axonDiamSweepWidget(QWidget_AxonDiamSweep, Ui_AxonDiamSweepWidget):

    def __init__(self, parent = None):
        super(axonDiamSweepWidget, self).__init__(parent)

        self.setupUi(self)


def test_mp(value):
    return value*2