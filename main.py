'''
@author: Rapp & Braun
'''

# https://miro.com/app/board/uXjVOQDTWvQ=/

from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

import matplotlib

import input_data_widget

matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

from stimulus_widget import stimulusWidget
from input_data_widget import InputDataWidget
from nerve_widget import NerveWidget
from threshold_widget import ThresholdWidget
from plot_widget import PlotWidget
import plot as plot_functions

import numpy as np
import sys
sys.path.insert(0, "C:/nrn/lib/python")

import neuron_sim as ns
import misc_functions as mf
from Axon_Models import mhh_model
from copy import deepcopy

import pandas as pd
from datetime import date
import glob
import os
import pickle

Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')
scaling = 1e3  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by scaling
interpolation_radius_index = 2
nerve_shape_step_size = 2
internode_segments = 10
node_segments = 5


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("MFE Neuro Simulation")

        # E-Field widget
        self.input_data_widget = InputDataWidget()

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

        # Simulation
        self.neuron_sim = None

        # signal connections
        self.conf_efield_button.clicked.connect(self.configure_efield)
        self.input_data_widget.e_field_changed.connect(self.update_plot_widget)
        self.input_data_widget.nerve_shape_changed.connect(self.set_nerve_shape)

        self.nerve_widget.nerve_shape_changed.connect(self.update_plot_widget)
        self.nerve_widget.axon_added.connect(self.update_plot_widget)

        self.stimulus_button.clicked.connect(self.open_stimulus_widget)
        self.stimulus_widget.stimulus_changed.connect(self.update_stimulus)

        self.threshold_config_button.clicked.connect(self.open_threshold_widget)
        self.threshold_search_button.clicked.connect(self.threshold_search)

        self.e_field_along_axon_button.clicked.connect(self.create_neuronal_model)
        self.simulation_button.clicked.connect(self.single_simulation)

        self.mc_button.clicked.connect(self.add_undulation_pattern_2)

    def add_plot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.e_field_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.input_data_widget, coordinates=True)
        self.e_field_layout.addWidget(self.toolbar)

    def remove_plot(self,):
        self.e_field_layout.removeWidget(self.canvas)
        self.canvas.close()
        self.e_field_layout.removeWidget(self.toolbar)
        self.toolbar.close()

    def configure_efield(self):
        self.input_data_widget.show()

    def update_plot_widget(self):
        self.plot_widget.clear_figures()
        if self.nerve_widget.anatomical_nerve:
            self.plot_widget.add_figure(self.input_data_widget.get_nerve_shape_plot(), 'Nerve Shape')
        if self.nerve_widget.custom_nerve and self.input_data_widget.e_field:
            self.plot_widget.add_figure(plot_functions.plot_2d_field_with_cable(self.input_data_widget.e_field,
                                                                                self.input_data_widget.e_field_layer_slider.value(),
                                                                                self.nerve_widget.custom_nerve,
                                                                                scaling), 'Custom Nerve in Field')
        if not self.nerve_widget.axon_list:
            return
        else:
            self.plot_widget.add_figure(plot_functions.plot_axon_xy_coordinates_with_nodes(self.nerve_widget.axon_list,
                                                                                           internode_segments),
                                        'Axon x y coordinates with nodes')
            self.plot_widget.add_figure(plot_functions.plot_axon_nerve_shape_xy_coordinates(self.nerve_widget.axon_list,
                                            self.nerve_widget.get_selected_nerve()), 'Axon and Nerve Shape coordinates')
        for axon in self.nerve_widget.axon_list:
            if axon.e_field_along_axon:
                self.plot_widget.add_figure(plot_functions.plot_e_field_along_nerve(self.neuron_sim.axon.e_field_along_axon),
                                            'E_field_along_nerve')
            if axon.potential_along_axon:
                self.plot_widget.add_figure(plot_functions.plot_potential_along_nerve(self.neuron_sim.axon.potential_along_axon),
                                            'Potential_along_nerve')
        # if self.neuron_sim and self.neuron_sim.axon.potential_vector_node_list:
        #     self.plot_widget.add_figure(plot_functions.plot_traces_and_field('', self.neuron_sim.time_axis,
        #                                                                      self.neuron_sim.stimulus,
        #                                                                      self.neuron_sim.axon), 'Voltage traces')

    def open_stimulus_widget(self):
        self.stimulus_widget.show()
        self.stimulus_widget.update_stimulus()

    def update_stimulus(self):
        self.stimulus = [self.stimulus_widget.stimulus, self.stimulus_widget.uni_stimulus]
        self.time_axis = self.stimulus_widget.time_axis
        self.total_time = self.stimulus_widget.total_time

    def create_neuronal_model(self):
        selected_nerve = self.nerve_widget.get_selected_nerve()
        if not self.nerve_widget.axon_list:
            return
        if not self.nerve_widget.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.nerve_widget.axon_list_view.currentIndex()
        if hasattr(self, 'field_axon_canvas'):
            self.potential_layout.removeWidget(self.field_axon_canvas)
            self.field_axon_canvas.close()
        axon = self.nerve_widget.axon_list[selected_index.row()]
        self.neuron_sim = ns.NeuronSim(self.input_data_widget.e_field, axon, interpolation_radius_index, self.time_axis,
                                       self.stimulus, self.total_time)
        self.neuron_sim.quasipot()
        self.update_plot_widget()

    def single_simulation(self):
        if not self.neuron_sim:
            return
        self.neuron_sim.simple_simulation()
        self.neuron_sim.plot_simulation()
        plt.show()
        # self.update_plot_widget()


    def threshold_search(self):
        selected_nerve = self.nerve_widget.custom_nerve
        if not selected_nerve.axon_list:
            return
        # Dict -----------------------------------------------------------------
        export_dict = {'Diameter': []}
        for axon in selected_nerve.axon_list:
            self.build_neuron_sim(axon)
            self.neuron_sim.quasipot()
            threshold = self.neuron_sim.threshold_simulation(self.threshold_widget)
            self.threshold_label.setText(str(threshold))
            current = 6000 * threshold
            print('Threshold coil current: ', current)
        # df = pd.DataFrame(export_dict)
        # today = date.today()
        # df.to_csv(str(today) + 'phrenic_rc_z_offset.csv', index=False, header=True)
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
        if not selected_nerve.axon_list:
            return
        axon = selected_nerve.axon_list[0]
        # Dict -----------------------------------------------------------------
        export_dict_efield = {}
        export_dict_potential = {}
        x_offset = np.arange(-190000, 190000, 400)
        for x in x_offset:
            self.nerve_widget.get_selected_nerve().x = self.nerve_widget.get_selected_nerve().x + x
            self.build_neuron_sim(axon)
            self.neuron_sim.quasipot()
            export_dict_efield[str(x)] = self.neuron_sim.axon.e_field_along_axon
            export_dict_potential[str(x)] = self.neuron_sim.axon.potential_along_axon
            self.nerve_widget.get_selected_nerve().x = self.nerve_widget.get_selected_nerve().x + x
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
        if not selected_nerve.axon_list:
            return
        axon = selected_nerve.axon_list[0]
        # Dict -----------------------------------------------------------------
        export_dict_efield = {}
        export_dict_potential = {}
        x_offset = np.arange(-190000, 190000, 400)
        for x in x_offset:
            axon.x = axon.x + x
            self.build_neuron_sim(axon)
            self.neuron_sim.quasipot()
            export_dict_efield[str(x)] = self.neuron_sim.axon.e_field_along_axon
            export_dict_potential[str(x)] = self.neuron_sim.axon.potential_along_axon
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
        if not selected_nerve.axon_list:
            return
        # Dict -----------------------------------------------------------------

        for axon in selected_nerve.axon_list:
            z_offset = np.arange(-25000, 26000, 5000)
            for z in z_offset:
                export_dict = {}
                self.nerve_widget.get_selected_nerve().z = self.nerve_widget.get_selected_nerve().z + z
                self.build_neuron_sim(axon)
                self.neuron_sim.quasipot()
                stim_matrix, e_field_along_axon, quasi_potentials, xpart, ypart, zpart, x_comp, y_comp, z_comp = mf.quasi_potentials_with_details(
                    self.neuron_sim.stimulus, self.neuron_sim.e_field, self.neuron_sim.axon, self.neuron_sim.interpolation_radius_index)
                export_dict['efield'] = e_field_along_axon
                export_dict['xcomp'] = x_comp
                export_dict['ycomp'] = y_comp
                export_dict['zcomp'] = z_comp
                self.nerve_widget.get_selected_nerve().z = self.nerve_widget.get_selected_nerve().z - z
                df = pd.DataFrame(export_dict)
                today = date.today()
                df.to_csv(str(today) + 'z_offset_' + str(z) + '.csv', index=False, header=True)
            print('Finished!')

    def add_undulation(self):
        if self.neuron_sim:
            distance = np.linspace(0,self.neuron_sim.axon.total_length, len(self.neuron_sim.axon.x))
            undulation_period = 200  # µm
            undulation_amplitude = 40  # µm
            undulation_sine = undulation_amplitude * np.sin(2 * np.pi * (1 / undulation_period) * distance)
            print(len(undulation_sine))
            print(len(self.neuron_sim.axon.x))
            self.neuron_sim.axon.x = self.neuron_sim.axon.x + undulation_sine

            # undulation_period = 50000  # µm
            # undulation_amplitude = 800  # µm
            # undulation_sine = undulation_amplitude * np.sin(2 * np.pi * (1 / undulation_period) * distance)
            # print(len(undulation_sine))
            # print(len(self.neuron_sim.axon.x))
            # self.neuron_sim.axon.x = self.neuron_sim.axon.x + undulation_sine
            self.plot_widget.add_figure(plot_functions.plot_axon_xy_coordinates(self.neuron_sim.axon),
                                        'Axon x y coordinates')
            self.plot_widget.add_figure(
                plot_functions.plot_axon_xy_coordinates_with_nodes(self.neuron_sim.axon, internode_segments),
                'Axon x y coordinates with nodes')
            
    def add_undulation_pattern_2(self):
        distance = np.linspace(0,self.nerve_widget.custom_nerve.length, len(self.nerve_widget.custom_nerve.x))
        undulation_period = 50000  # µm
        undulation_amplitude = 50000  # µm
        undulation_sine = undulation_amplitude * np.sin(2 * np.pi * (1 / undulation_period) * distance)
        self.nerve_widget.custom_nerve.x = self.nerve_widget.custom_nerve.x + undulation_sine
        self.plot_widget.add_figure(plot_functions.plot_2d_field_with_cable(self.input_data_widget.e_field,
                                                                            self.e_field_layer_slider.value(),
                                                                            self.nerve_widget.custom_nerve,
                                                                            scaling), 'Nerve in Field')
        # undulation_period = 200  # µm
        # undulation_amplitude = 40  # µm
        # undulation_sine = undulation_amplitude * np.sin(2 * np.pi * (1 / undulation_period) * distance)
        # delta_x_list = []
        # delta_y_list = []
        # for i in range(len(self.neuron_sim.axon.x)-1):
        #     delta_x_1 = self.neuron_sim.axon.x[i + 1] - self.neuron_sim.axon.x[i]
        #     delta_y_1 = self.neuron_sim.axon.y[i + 1] - self.neuron_sim.axon.y[i]
        #     print('dx:', delta_x_1)
        #     dist = np.sqrt(delta_x_1**2 + delta_y_1**2)
        #     ratio = undulation_sine[i] / dist
        #     delta_x_list.append(delta_y_1 * ratio)  # delta x gets delta y for the normal line to the tangential
        #     delta_y_list.append(delta_x_1 * ratio)
        # delta_x_list.append(delta_x_list[-1])
        # delta_y_list.append(delta_y_list[-1])
        # self.neuron_sim.axon.x = self.neuron_sim.axon.x + np.asarray(delta_x_list)
        # self.neuron_sim.axon.y = self.neuron_sim.axon.y + np.asarray(delta_y_list)
        # self.plot_widget.add_figure(plot_functions.plot_axon_xy_coordinates(self.neuron_sim.axon),
        #                             'Axon x y coordinates')
        # self.plot_widget.add_figure(
        #     plot_functions.plot_axon_xy_coordinates_with_nodes(self.neuron_sim.axon, internode_segments),
        #     'Axon x y coordinates with nodes')

    def open_threshold_widget(self):
        self.threshold_widget.show()

    def set_nerve_shape(self):
        self.nerve_widget.add_anatomical_nerve(self.input_data_widget.nerve_shape)


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
