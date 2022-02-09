'''
@author: Rapp & Braun
'''

# https://miro.com/app/board/uXjVOQDTWvQ=/

from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

from stimulus_widget import stimulusWidget
from e_field_manipulation_widget import eFieldWidget
from nerve_widget import NerveWidget
from threshold_widget import ThresholdWidget
from monte_carlo_widget import MonteCarloWidgetEField, MonteCarloWidgetNerveShape

import numpy as np
import sys
sys.path.insert(0, "C:/nrn/lib/python")

import neuron_sim as ns
import neuron_sim_nerve_shape as ns_ns


Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')
scaling = 1e3  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by scaling
interpolation_radius_index = 2
nerve_shape_step_size = 10

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("MFE Neuro Simulation")

        # E-Field widget
        self.e_field_widget = eFieldWidget()
        e_field_name = 'halsmodell'
        self.e_field_list = self.e_field_widget.get_e_field(e_field_name)
        self.add_plot(self.e_field_widget.plot_e_field(self.e_field_list[0]))

        # Nerve widget
        self.nerve_widget = NerveWidget()
        self.nerve_layout.addWidget(self.nerve_widget)

        # Stimulus widget
        self.stimulus_widget = stimulusWidget()
        self.update_stimulus()

        # Threshold search widget
        self.threshold_widget = ThresholdWidget()

        # signal connections
        self.conf_efield_button.clicked.connect(self.configure_efield)
        self.e_field_widget.e_field_changed.connect(self.update_e_field)

        self.nerve_widget.e_field_changed.connect(self.update_e_field)

        self.stimulus_button.clicked.connect(self.open_stimulus_widget)
        self.stimulus_widget.stimulus_changed.connect(self.update_stimulus)

        self.threshold_config_button.clicked.connect(self.open_threshold_widget)
        self.threshold_search_button.clicked.connect(self.threshold_search)

        self.e_field_along_axon_button.clicked.connect(self.checkin_nerve)
        self.simulation_button.clicked.connect(self.start_simulation)

        self.mc_diameter_button.clicked.connect(self.monte_carlo_axon_diam_sweep)

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

    def open_stimulus_widget(self):
        self.stimulus_widget.show()
        self.stimulus_widget.update_stimulus()

    def update_stimulus(self):
        self.stimulus = [self.stimulus_widget.stimulus, self.stimulus_widget.uni_stimulus]
        self.time_axis = self.stimulus_widget.time_axis
        self.total_time = self.stimulus_widget.total_time

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
            neuron_sim = ns.NeuronSim(selected_nerve.axon_infos_list[selected_index.row()], self.e_field_list,
                                      self.time_axis, self.stimulus, self.total_time)
        else:
            neuron_sim = ns_ns.NeuronSimNerveShape(selected_nerve.axon_infos_list[selected_index.row()],
                                                   self.e_field_widget.nerve_shape, self.time_axis, self.stimulus,
                                                   self.total_time, nerve_shape_step_size)
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
            neuron_sim.plot_simulation()
        plt.show()

    def threshold_search(self):
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
            threshold = neuron_sim.threshold_simulation(self.threshold_widget)
            self.threshold_label.setText(str(threshold))
            neuron_sim.simple_simulation()
        plt.show()

    def open_threshold_widget(self):
        self.threshold_widget.show()

    def monte_carlo_axon_diam_sweep(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if self.e_field_widget.mode == 0:
            self.monte_carlo_widget = MonteCarloWidgetNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                       self.stimulus, self.time_axis, self.total_time, self.threshold_widget)

            self.monte_carlo_widget.show()
        else:
            self.monte_carlo_widget = MonteCarloWidgetEField(self.e_field_list, interpolation_radius_index, selected_nerve,
                                                       self.stimulus, self.time_axis, self.total_time, self.threshold_widget)

            self.monte_carlo_widget.show()


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
