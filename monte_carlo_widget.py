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
from datetime import date
import copy
Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_monte_carlo_widget.ui")
Ui_AxonDiamSweepWidget, QWidget_AxonDiamSweep = uic.loadUiType("ui_mc_sim_widget.ui")

parameter_list = ['Axon Diam', 'Axon Position', 'Coil Current']


class MonteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):

    def __init__(self, stimulus, time_axis, total_time, threshold_widget, parent=None):
        super(MonteCarloWidget, self).__init__(parent)
        self.setupUi(self)
        self.stimulus = stimulus
        self.time_axis = time_axis
        self.total_time = total_time
        self.threshold_widget = threshold_widget

        self.mc_sim_widget_list = []
        self.add_simulation_push_button.clicked.connect(self.add_simulation)
        self.delete_all_pushbutton.clicked.connect(self.delete_parameters)
        self.start_mc_button.clicked.connect(self.prepare_parameters_for_sim)

    def add_simulation(self):
        mc_sim_widget = MCSimWidget()
        self.mc_sim_widget_list.append(mc_sim_widget)
        self.sim_layout.addWidget(mc_sim_widget)

    def delete_parameters(self):
        self.mc_sim_widget_list = []
        for i in range(self.sim_layout.count()):
            self.sim_layout.itemAt(i).widget().setVisible(False)
            self.sim_layout.itemAt(i).widget().deleteLater()

    def prepare_parameters_for_sim(self):
        for widget in self.mc_sim_widget_list:
            if widget.parameter_dict['Axon Diam'][4]:
                diameter = widget.parameter_dict['Axon Diam'][0]
            else:
                diameter = self.get_parameter_distribution(widget.parameter_dict['Axon Diam'][0],
                                                           widget.parameter_dict['Axon Diam'][1],
                                                           widget.parameter_dict['Axon Diam'][2],
                                                           widget.parameter_dict['Axon Diam'][3])
            if widget.parameter_dict['Axon Position'][4]:
                offset = widget.parameter_dict['Axon Position'][0]
            else:
                offset = self.get_parameter_distribution(widget.parameter_dict['Axon Position'][0],
                                                           widget.parameter_dict['Axon Position'][1],
                                                           widget.parameter_dict['Axon Position'][2],
                                                           widget.parameter_dict['Axon Position'][3])
            if widget.parameter_dict['Coil Current'][4]:
                current = widget.parameter_dict['Coil Current'][0]
            else:
                current = self.get_parameter_distribution(widget.parameter_dict['Coil Current'][0],
                                                           widget.parameter_dict['Coil Current'][1],
                                                           widget.parameter_dict['Coil Current'][2],
                                                           widget.parameter_dict['Coil Current'][3])

            self.start_mc_simulation(diameter, offset, current)

    def get_parameter_distribution(self, mean, stdev, min, max):
        distribution_list = []
        for i in range(self.runs_spinBox.value()):
            helper = False
            while not helper:
                normal_distribution = random.normal(mean, stdev)
                if max > normal_distribution > min:
                    helper = True
                    distribution_list.append(normal_distribution)
        return distribution_list

    def start_mc_simulation(self, diameter, offset, current):
        stimulation_success = []
        i = 0
        if isinstance(diameter, list) and isinstance(offset, list):
            diameter.sort()
            offset.sort()
            result_dict = {'Diameter': diameter}
            for pos in offset:
                result_dict[str(pos)] = []
                for diam in diameter:
                    is_stimulated = self.run_diam_position_current_simulation(diam, pos, current)
                    result_dict[str(pos)].append(is_stimulated)
                    stimulation_success.append(is_stimulated)
                    i += 1
                    print('Run ', i, '/ ', self.runs_spinBox.value())

            df = pd.DataFrame(result_dict)
            today = date.today()
            df.to_csv(str(today) + '_mc_diam_vs_coil_distance_half_cosine_200us_intensity1_volume_300mm.csv', index=False, header=True)

            results = np.asarray(stimulation_success)
            results = np.reshape(results, (self.runs_spinBox.value(), self.runs_spinBox.value()))
            fig5 = pt.figure(5)
            ax5 = fig5.gca()
            ax5 = pt.imshow(results, extent=[offset[0]/1000, offset[-1]/1000, diameter[-1], diameter[0]])
            pt.show()

        if isinstance(diameter, list) and isinstance(current, list):
            diameter.sort()
            current.sort()
            result_dict = {'Diameter': diameter}
            for cur in current:
                result_dict[str(cur)] = []
                for diam in diameter:
                    is_stimulated = self.run_diam_position_current_simulation(diam, offset, cur)
                    result_dict[str(cur)].append(is_stimulated)

            df = pd.DataFrame(result_dict)
            today = date.today()
            df.to_csv(str(today) + '_mc_diam_vs_current_half_cosine_200us_intensity1_volume_300mm.csv', index=False, header=True)

        if isinstance(offset, list) and isinstance(current, list):
            offset.sort()
            current.sort()
            result_dict = {'Diameter': offset}
            for cur in current:
                result_dict[str(cur)] = []
                for pos in offset:
                    is_stimulated = self.run_diam_position_current_simulation(diameter, pos, cur)
                    result_dict[str(cur)].append(is_stimulated)

            df = pd.DataFrame(result_dict)
            today = date.today()
            df.to_csv(str(today) + '_mc_offset_vs_current_half_cosine_200us_intensity1_volume_300mm.csv', index=False, header=True)

    def run_diam_position_current_simulation(self, diam, start_pos_offset_z, coil_current):
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

    # def run_diam_position_simulation(self, diam, start_pos_offset_x, start_pos_offset_y, start_pos_offset_z):
    def run_diam_position_current_simulation(self, diam, start_pos_offset_z, coil_current):
        axon_info = ns.AxonInformation(0, 0, 0, 0, 0, diam, 'MHH')
        internal_nerve_shape = copy.copy(self.nerve_shape)
        internal_nerve_shape.z = internal_nerve_shape.z + start_pos_offset_z
        neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_list, self.interpolation_radius_index,
                                                      internal_nerve_shape, self.nerve_step_size, axon_info, self.time_axis,
                                                      self.stimulus, self.total_time)

        neuron_sim.quasipot()
        neuron_sim.simple_simulation()
        if neuron_sim.is_axon_stimulated(self.threshold_widget):
            return 1
        else:
            return 0


class MCSimWidget(QWidget_AxonDiamSweep, Ui_AxonDiamSweepWidget):

    def __init__(self, parent = None):
        super(MCSimWidget, self).__init__(parent)

        self.setupUi(self)

        self.parameter_combobox.addItems(parameter_list)
        self.parameter_dict = dict.fromkeys(parameter_list)

        self.parameter_dict['Axon Diam'] = []
        self.parameter_dict['Axon Diam'].append(15.29)
        self.parameter_dict['Axon Diam'].append(2.133)
        self.parameter_dict['Axon Diam'].append(self.parameter_dict['Axon Diam'][0] - 2*self.parameter_dict['Axon Diam'][1])
        self.parameter_dict['Axon Diam'].append(self.parameter_dict['Axon Diam'][0] + 2*self.parameter_dict['Axon Diam'][1])
        self.parameter_dict['Axon Diam'].append(0)

        self.parameter_dict['Axon Position'] = []
        self.parameter_dict['Axon Position'].append(0)
        self.parameter_dict['Axon Position'].append(15000)
        self.parameter_dict['Axon Position'].append(self.parameter_dict['Axon Position'][0] - self.parameter_dict['Axon Position'][1])
        self.parameter_dict['Axon Position'].append(self.parameter_dict['Axon Position'][0] + self.parameter_dict['Axon Position'][1])
        self.parameter_dict['Axon Position'].append(0)

        self.parameter_dict['Coil Current'] = []
        self.parameter_dict['Coil Current'].append(1)  # 0.5
        self.parameter_dict['Coil Current'].append(0.1)  # 0.05
        self.parameter_dict['Coil Current'].append(self.parameter_dict['Coil Current'][0] - self.parameter_dict['Coil Current'][1])
        self.parameter_dict['Coil Current'].append(self.parameter_dict['Coil Current'][0] + self.parameter_dict['Coil Current'][1])
        self.parameter_dict['Coil Current'].append(1)

        self.update()

        self.parameter_combobox.currentTextChanged.connect(self.update)

        self.mean_spinbox.valueChanged.connect(self.set_mean)
        self.stdev_spinbox.valueChanged.connect(self.set_stdev)
        self.min_double_spin_box.valueChanged.connect(self.set_min)
        self.max_double_spin_box.valueChanged.connect(self.set_max)

        self.mc_radioButton.clicked.connect(self.state_changed)
        self.fixed_radioButton.clicked.connect(self.state_changed)

    def update(self):
        key = self.parameter_combobox.currentText()
        self.mean_spinbox.setValue(self.parameter_dict[key][0])
        self.stdev_spinbox.setValue(self.parameter_dict[key][1])
        self.min_double_spin_box.setValue(self.parameter_dict[key][2])
        self.max_double_spin_box.setValue(self.parameter_dict[key][3])
        if self.parameter_dict[key][4]:
            self.fixed_radioButton.setChecked(True)
            self.mc_radioButton.setChecked(False)
        else:
            self.fixed_radioButton.setChecked(False)
            self.mc_radioButton.setChecked(True)

    def set_mean(self):
        key = self.parameter_combobox.currentText()
        self.parameter_dict[key][0] = self.mean_spinbox.value()

    def set_stdev(self):
        key = self.parameter_combobox.currentText()
        self.parameter_dict[key][1] = self.stdev_spinbox.value()
        
    def set_min(self):
        key = self.parameter_combobox.currentText()
        self.parameter_dict[key][2] = self.min_double_spin_box.value()
        
    def set_max(self):
        key = self.parameter_combobox.currentText()
        self.parameter_dict[key][3] = self.max_double_spin_box.value()

    def state_changed(self):
        key = self.parameter_combobox.currentText()
        if self.mc_radioButton.isChecked():
            self.parameter_dict[key][4] = 0
        else:
            self.parameter_dict[key][4] = 1
