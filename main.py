'''
@author: Rapp & Braun
'''

from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

from config_widgets import stimulusWidget
from e_field_manipulation_widget import eFieldWidget
from nerve_widget import nerveWidget

import numpy as np
import sys
sys.path.insert(0, "C:/nrn/lib/python")

import nerve as ner
import stimulus as stim
import time
import pandas as pd
import e_field_manipulation_widget as em
import neuron_sim as ns
import neuron_sim_nerve_shape as ns_ns
import field_plot as fp


Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')
scaling = 1e3  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by scaling
interpolation_radius_index = 2
nerve_shape_step_size = 10

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()

        self.setupUi(self)

        self.e_field_widget = eFieldWidget()
        e_field_name = 'halsmodell'
        self.e_field_list = self.e_field_widget.get_e_field(e_field_name)

        self.add_plot(self.e_field_widget.plot_e_field(self.e_field_list[0]))
        self.nerve_widget = nerveWidget()
        self.nerve_layout.addWidget(self.nerve_widget)

        self.stimulus_widget = stimulusWidget()
        self.stimulus_widget.stim_combo_box.addItems(stim.stimulus_string_list())
        self.update_stimulus()

        # signal connections

        self.conf_efield_button.clicked.connect(self.configure_efield)
        self.e_field_widget.e_field_changed.connect(self.update_e_field)
        self.e_field_widget.e_field_changed.connect(self.set_mode)

        self.nerve_widget.e_field_changed.connect(self.update_e_field)

        self.stimulus_widget.stim_combo_box.currentTextChanged.connect(self.update_stimulus)
        self.stimulus_widget.total_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_widget.start_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_widget.stimulus_intensity_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_widget.stimulus_duration_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_button.clicked.connect(self.open_stimulus_widget)
        self.e_field_along_axon_button.clicked.connect(self.checkin_nerve)
        self.simulation_button.clicked.connect(self.start_simulation)

    def add_plot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.e_field_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                self.e_field_widget, coordinates=True)
        self.e_field_layout.addWidget(self.toolbar)

    def remove_plot(self,):
        self.e_field_layout.removeWidget(self.canvas)
        self.canvas.close()
        self.e_field_layout.removeWidget(self.toolbar)
        self.toolbar.close()

    def configure_efield(self):
        self.e_field_widget.show()
        # TODO: update field_plot_manager

    def update_e_field(self):
        if self.e_field_widget.mode == 1:
            self.e_field_list = self.e_field_widget.e_field_list
            if not self.nerve_widget.nerve_dict:
                self.remove_plot()
                self.add_plot(self.e_field_widget.plot_e_field(self.e_field_list[0]))
                return
            selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
            fig = self.e_field_widget.plot_2d_field_with_cable(self.e_field_list[0], selected_nerve, scaling)
        else:
            fig = self.e_field_widget.plot_nerve_shape(self.e_field_widget.nerve_shape)
        self.remove_plot()
        self.add_plot(fig)

    def set_mode(self):
        if self.e_field_widget.mode == 1:
            if not self.nerve_widget.nerve_dict:
                self.nerve_widget.properties_groupBox.setEnabled(False)
            else:
                self.nerve_widget.properties_groupBox.setEnabled(True)
        else:
            self.nerve_widget.properties_groupBox.setEnabled(False)

    def open_stimulus_widget(self):
        self.stimulus_widget.show()
        self.update_stimulus()

    def update_stimulus(self):
        if hasattr(self, 'stim_canvas'):
            self.stimulus_widget.stimulus_layout.removeWidget(self.stim_canvas)
            self.stim_canvas.close()
        self.time_axis, self.stimulus, self.stim_name = stim.get_stim_from_string(self.stimulus_widget.stim_combo_box.currentText(),
                                                                   self.stimulus_widget.total_time_spin_box.value(),
                                                                   self.stimulus_widget.start_time_spin_box.value(),
                                                                   self.stimulus_widget.stimulus_duration_spin_box.value())
        self.stimulus = self.stimulus * self.stimulus_widget.stimulus_intensity_spin_box.value()
        self.total_time = self.stimulus_widget.total_time_spin_box.value()
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(self.time_axis, self.stimulus)
        self.stim_canvas = FigureCanvas(fig1)
        self.stimulus_widget.stimulus_layout.addWidget(self.stim_canvas)
        self.stim_canvas.draw()

    def checkin_nerve(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        if not self.nerve_widget.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.nerve_widget.axon_list_view.currentIndex()

        if hasattr(self, 'field_axon_canvas'):
            self.potential_layout.removeWidget(self.field_axon_canvas)
            self.field_axon_canvas.close()
        if self.e_field_widget.mode == 1:
            neuron_sim = ns.NeuronSim(selected_nerve.axon_infos_list[selected_index.row()], self.e_field_list, self.time_axis, self.stimulus, self.total_time)
        else:
            neuron_sim = ns_ns.NeuronSimNerveShape(selected_nerve.axon_infos_list[selected_index.row()], self.e_field_widget.nerve_shape, self.time_axis, self.stimulus, self.total_time, nerve_shape_step_size)
            fig2 = Figure()
            ax = plt.gca(projection='3d')
            ax.scatter3D(neuron_sim.axon.x, neuron_sim.axon.y, neuron_sim.axon.z)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')
            plt.show()
        neuron_sim.quasipot(interpolation_radius_index)
        e_field_along_axon = neuron_sim.axon.e_field_along_axon
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(e_field_along_axon)
        self.field_axon_canvas = FigureCanvas(fig1)
        self.potential_layout.addWidget(self.field_axon_canvas)
        self.field_axon_canvas.draw()

    def start_simulation(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        for axon in selected_nerve.axon_infos_list:
            if self.e_field_widget.mode == 1:
                neuron_sim = ns.NeuronSim(axon, self.e_field_list,
                                          self.time_axis, self.stimulus, self.total_time)
            else:
                neuron_sim = ns_ns.NeuronSimNerveShape(axon,
                                                       self.e_field_widget.nerve_shape, self.time_axis, self.stimulus,
                                                       self.total_time, nerve_shape_step_size)
            neuron_sim.quasipot(interpolation_radius_index)
            neuron_sim.simple_simulation()
        plt.show()


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    pixmap = QtGui.QPixmap("splash.png")
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()
    main = Main()

    main.show()
    sys.exit(app.exec_())
