import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import neuron_sim as ns

Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_nerve_widget.ui")
Ui_AxonDiamSweepWidget, QWidget_AxonDiamSweep = uic.loadUiType("ui_nerve_dimension_widget.ui")

parameter_list = ['Axon Diam', 'Axon Position']


class monteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):

    def __init__(self, e_field, nerve, stimulus, threshold_widget, mode=1, parent=None):
        super(monteCarloWidget, self).__init__(parent)

        self.setupUi(self)
        self.mode = mode
        self.e_field = e_field
        self.nerve = nerve
        self.stimulus = stimulus
        self.threshold_widget = threshold_widget

        self.parameter_combobox.addItems(parameter_list)

        self.axon_diam_widget = axonDiamSweepWidget()

        self.parameter_combobox.currentTextChanged.connect(self.set_axon_diam_widget)
        self.start_mc_button.clicked.connect(self.start_monte_carlo)

    def set_parameter_widget(self):
        if not self.parameter_layout.isEmpty():
            self.parameter_layout.removeWidget()
        if self.axon_type_combo_box.currentText() == 'Axon Diam':
            self.parameter_layout.addWidget(self.axon_diam_widget)

    def start_monte_carlo(self):
        if self.axon_type_combo_box.currentText() == 'Axon Diam':
            self.start_mc_diam_sweep()

    def start_mc_diam_sweep(self):
        # gather information about interval for value selection and further parameters

        # get monte carlo diameters
        # for each diameter: (use parallel computing)
        #   assemble ns.AxonInormation
        #   create NeuronSim
        #   do threshold search

        axon_info = ns.AxonInformation(selected_nerve.x, selected_nerve.y, selected_nerve.z, selected_nerve.angle,
                                        selected_nerve.length, diameter, axon_type)
        if self.mode == 1:
            neuron_sim = ns.NeuronSim(axon_info, self.e_field,
                                      self.time_axis, self.stimulus, self.total_time)
        else:
            neuron_sim = ns.NeuronSimNerveShape(axon_info,
                                                   self.e_field, self.time_axis, self.stimulus,
                                                   self.total_time, nerve_shape_step_size)


class axonDiamSweepWidget(QWidget_AxonDiamSweep, Ui_AxonDiamSweepWidget):

    def __init__(self, parent = None):
        super(axonDiamSweepWidget, self).__init__(parent)

        self.setupUi(self)
