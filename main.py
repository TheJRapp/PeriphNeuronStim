'''
@author: Rapp & Braun
'''

# https://miro.com/app/board/uXjVOQDTWvQ=/

from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

import matplotlib

import e_field_widget

matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

from stimulus_widget import stimulusWidget
from e_field_widget import EFieldWidget
from nerve_widget import NerveWidget
from threshold_widget import ThresholdWidget
from monte_carlo_widget import MonteCarloWidgetEField, MonteCarloWidgetNerveShape, MonteCarloWidgetEFieldWithNerveShape
from plot_widget import PlotWidget
import plot as plot_functions

import numpy as np
import sys
sys.path.insert(0, "C:/nrn/lib/python")

import neuron_sim as ns
import misc_functions as mf
import neuron_sim_nerve_shape as ns_ns
from copy import deepcopy

import pandas as pd
from datetime import date
import glob
import os
import pickle

Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')
scaling = 1e3  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by scaling
interpolation_radius_index = 0
nerve_shape_step_size = 2
internode_segments = 20
node_segments = 1


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("MFE Neuro Simulation")

        # E-Field widget
        self.e_field_widget = EFieldWidget()

        # Plot widget
        self.plot_widget = PlotWidget()
        self.plot_layout.addWidget(self.plot_widget)

        # Nerve widget
        self.nerve_widget = NerveWidget(scaling, node_segments, internode_segments)
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

        self.e_field_along_axon_button.clicked.connect(self.calculate_field_along_axon)
        self.simulation_button.clicked.connect(self.single_simulation)

        self.mc_button.clicked.connect(self.af_nerve_position_nerve_shape)

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

    def update_e_field(self):
        if self.nerve_widget.nerve_dict:
            selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
            self.e_field_widget.custom_nerve = selected_nerve
            self.e_field_widget.scaling = scaling
            if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
                self.plot_widget.add_figure(self.e_field_widget.get_e_field_with_custom_nerve_plot(), 'Nerve in Field')
        else:
            self.e_field_widget.custom_nerve = None

        if self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
            self.plot_widget.add_figure(self.e_field_widget.get_nerve_shape_plot(), 'Nerve Shape')
        self.plot_widget.add_figure(self.e_field_widget.get_current_e_field_plot(), 'Current E-field')

    def open_stimulus_widget(self):
        self.stimulus_widget.show()
        self.stimulus_widget.update_stimulus()

    def update_stimulus(self):
        self.stimulus = [self.stimulus_widget.stimulus, self.stimulus_widget.uni_stimulus]
        self.time_axis = self.stimulus_widget.time_axis
        self.total_time = self.stimulus_widget.total_time

    def get_neuron_sim(self, axon):
        neuron_sim = None
        if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
            neuron_sim = ns.NeuronSimEField(self.e_field_widget.e_field, interpolation_radius_index,
                                            axon, self.time_axis, self.stimulus, self.total_time)
        elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
            neuron_sim = ns.NeuronSimNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                axon, self.time_axis, self.stimulus, self.total_time)
        elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
            neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_widget.e_field,
                                                          interpolation_radius_index,
                                                          self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                          axon, self.time_axis, self.stimulus, self.total_time)
        return neuron_sim

    def calculate_field_along_axon(self):
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
        neuron_sim = self.get_neuron_sim(selected_nerve.axon_infos_list[selected_index.row()])
        neuron_sim.quasipot()

        self.plot_widget.add_figure(plot_functions.plot_e_field_along_nerve(neuron_sim.axon.e_field_along_axon),
                                    'E_field_along_nerve')
        self.plot_widget.add_figure(plot_functions.plot_potential_along_nerve(neuron_sim.axon.potential_along_axon),
                                    'Potential_along_nerve')
        self.plot_widget.add_figure(plot_functions.plot_axon_xy_coordinates(neuron_sim.axon),
                                    'Axon x y coordinates')
        if self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
            self.plot_widget.add_figure(plot_functions.plot_axon_nerve_shape_xy_coordinates(neuron_sim.axon,
                                        self.e_field_widget.nerve_shape), 'Axon and Nerve Shape coordinates')

        e_field_along_axon = neuron_sim.axon.e_field_along_axon
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(e_field_along_axon)
        self.field_axon_canvas = FigureCanvas(fig1)
        self.potential_layout.addWidget(self.field_axon_canvas)
        self.field_axon_canvas.draw()


    def single_simulation(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        for axon in selected_nerve.axon_infos_list:
            neuron_sim = self.get_neuron_sim(axon)
            neuron_sim.quasipot()
            neuron_sim.simple_simulation()
            neuron_sim.plot_simulation()
        plt.show()

    def threshold_search(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        # Dict -----------------------------------------------------------------
        export_dict = {'Diameter': []}
        for axon in selected_nerve.axon_infos_list:
            export_dict['Diameter'].append(axon.diameter)
            z_offset = np.arange(-25000, 26000, 1000)
            for z in z_offset:
                if z not in export_dict:
                    export_dict[z] = []
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z + z
                neuron_sim = self.get_neuron_sim(axon)
                neuron_sim.quasipot()
                threshold = neuron_sim.threshold_simulation(self.threshold_widget)
                self.threshold_label.setText(str(threshold))
                current = 6000 * threshold
                print('Threshold coil current: ', current)
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z - z
                export_dict[z].append(current)
        df = pd.DataFrame(export_dict)
        today = date.today()
        df.to_csv(str(today) + 'phrenic_rc_z_offset.csv', index=False, header=True)
        print('Finished!')

    def af_nerve_position_nerve_shape(self):
        '''
        Description:
        - E field with e_field and nerve shape
        - Varies nerve position
        - Calculate quasipotenital
        - Write files
            - e_field_along_axon
            - potential along axon
        Required:
        Single axon, single e_field
        What is done here:
        Different postions of the axon
        Output:
        Dict with activation function for each offset
        '''
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        axon = selected_nerve.axon_infos_list[0]
        # Dict -----------------------------------------------------------------
        export_dict_efield = {}
        export_dict_potential = {}
        x_offset = np.arange(-190000, 190000, 400)
        for x in x_offset:
            self.e_field_widget.nerve_shape.x = self.e_field_widget.nerve_shape.x + x
            neuron_sim = self.get_neuron_sim(axon)
            neuron_sim.quasipot()
            export_dict_efield[str(x)] = neuron_sim.axon.e_field_along_axon
            export_dict_potential[str(x)] = neuron_sim.axon.potential_along_axon
            self.e_field_widget.nerve_shape.x = self.e_field_widget.nerve_shape.x + x
        path = 'Y:/Sonstiges/Stimit AG/'
        project = 'phrenic'
        file_name = '001'
        df = pd.DataFrame(export_dict_efield)
        df.to_csv(path + project + '_' + file_name + 'e_field_'+ '.csv', index=False, header=True)
        df = pd.DataFrame(export_dict_potential)
        df.to_csv(path + project + '_' + file_name + 'potential_'+ '.csv', index=False, header=True)
        print('Finished!')

    def af_nerve_position_custom_nerve(self):
        '''
        Description:
        - E field with custom nerve shape
        - Varies nerve position
        - Calculate quasipotenital
        - Write files
            - e_field_along_axon
            - potential along axon
        Required:
        Single axon, single e_field
        What is done here:
        Different postions of the axon
        Output:
        Dict with activation function for each offset
        '''
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        axon = selected_nerve.axon_infos_list[0]
        # Dict -----------------------------------------------------------------
        export_dict_efield = {}
        export_dict_potential = {}
        x_offset = np.arange(-190000, 190000, 400)
        for x in x_offset:
            axon.x = axon.x + x
            neuron_sim = self.get_neuron_sim(axon)
            neuron_sim.quasipot()
            export_dict_efield[str(x)] = neuron_sim.axon.e_field_along_axon
            export_dict_potential[str(x)] = neuron_sim.axon.potential_along_axon
            axon.x = axon.x - x
        today = date.today()
        path = 'Y:/Sonstiges/Stimit AG/'
        project = 'phrenic'
        file_name = '001'
        df = pd.DataFrame(export_dict_efield)
        df.to_csv(path + project + '_' + file_name + 'e_field_' + '.csv', index=False, header=True)
        df = pd.DataFrame(export_dict_potential)
        df.to_csv(path + project + '_' + file_name + 'potential_' + '.csv', index=False, header=True)
        print('Finished!')

    def analyze_field_contributions(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        # Dict -----------------------------------------------------------------

        for axon in selected_nerve.axon_infos_list:
            z_offset = np.arange(-25000, 26000, 5000)
            for z in z_offset:
                export_dict = {}
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z + z
                if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
                    neuron_sim = ns.NeuronSimEField(self.e_field_widget.e_field, interpolation_radius_index,
                                                    axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
                    neuron_sim = ns.NeuronSimNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                        axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
                    neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_widget.e_field,
                                                                  interpolation_radius_index,
                                                                  self.e_field_widget.nerve_shape,
                                                                  nerve_shape_step_size,
                                                                  axon, self.time_axis, self.stimulus, self.total_time)
                neuron_sim.quasipot()
                stim_matrix, e_field_along_axon, quasi_potentials, xpart, ypart, zpart, x_comp, y_comp, z_comp = mf.quasi_potentials_with_details(
                    neuron_sim.stimulus, neuron_sim.e_field, neuron_sim.axon, neuron_sim.interpolation_radius_index)
                export_dict['efield'] = e_field_along_axon
                export_dict['xcomp'] = x_comp
                export_dict['ycomp'] = y_comp
                export_dict['zcomp'] = z_comp
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z - z
                df = pd.DataFrame(export_dict)
                today = date.today()
                df.to_csv(str(today) + 'z_offset_' + str(z) + '.csv', index=False, header=True)
            print('Finished!')

    def open_threshold_widget(self):
        self.threshold_widget.show()

    def monte_carlo_axon_diam_sweep(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
            self.monte_carlo_widget = MonteCarloWidgetEField(self.e_field_widget.e_field,
                                                             interpolation_radius_index, selected_nerve, self.stimulus,
                                                             self.time_axis, self.total_time, self.threshold_widget)
            self.monte_carlo_widget.show()
        elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
            self.monte_carlo_widget = MonteCarloWidgetNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                                 self.stimulus, self.time_axis, self.total_time,
                                                                 self.threshold_widget)
            self.monte_carlo_widget.show()
        elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
            self.monte_carlo_widget = MonteCarloWidgetEFieldWithNerveShape(self.e_field_widget.e_field,
                                                                           interpolation_radius_index,
                                                                           self.e_field_widget.nerve_shape,
                                                                           nerve_shape_step_size,
                                                                           self.stimulus, self.time_axis,
                                                                           self.total_time, self.threshold_widget)
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
