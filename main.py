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

from config_widgets import windowTest, stimulusWidget
from e_field_manipulation import eFieldWidget

import numpy as np
import sys
sys.path.insert(0, "C:/nrn/lib/python")

import nerve as ner
import stimulus as stim
import time
import pandas as pd
import e_field_manipulation as em
import neuron_sim as ns
import field_plot as fp


Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')


rmg_diameter_list = ["5.7", "7.3", "8.7", "10.0", "11.5", "12.8", "14.0", "15.0", "16"]
interpolation_radius_index = 2
scaling = 1e3  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by scaling


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()

        self.setupUi(self)

        self.e_field_widget = eFieldWidget()
        e_field_name = 'halsmodell'
        self.e_field_list = self.e_field_widget.get_e_field(e_field_name)
        # self.field_plot_manager = fp.FieldPlot(self.e_field_list[0])

        self.add_plot(self.e_field_widget.plot_e_field(self.e_field_list[0]))
        self.nerve_dict = {}
        self.axon_list_item_model = QtGui.QStandardItemModel(self.axon_list_view)
        self.nerve_list_item_model = QtGui.QStandardItemModel(self.nerve_combo_box)

        self.nerve_prop_widget = windowTest()
        self.nerve_prop_widget.setEnabled(False)
        self.property_layout.addWidget(self.nerve_prop_widget)
        self.axon_diam_spin_box.setVisible(False)
        self.axon_diam_combo_box.addItems(rmg_diameter_list)

        self.stimulus_widget = stimulusWidget()
        self.stimulus_widget.stim_combo_box.addItems(stim.stimulus_string_list())
        self.update_stimulus()

        # signal connections

        self.conf_efield_button.clicked.connect(self.configure_efield)
        self.e_field_widget.e_field_changed.connect(self.update_e_field)

        self.add_nerve_button.clicked.connect(self.add_nerve)
        self.delete_nerve_button.clicked.connect(self.delete_nerve)
        self.nerve_combo_box.currentTextChanged.connect(self.change_nerve_property_box)
        self.add_axon_button.clicked.connect(self.add_axon_to_nerve)
        self.delete_axon_button.clicked.connect(self.delete_axon)

        self.axon_type_combo_box.currentTextChanged.connect(self.set_axon_diam_widget)

        self.nerve_prop_widget.x_spin_box.valueChanged.connect(self.set_nerve_x)
        self.nerve_prop_widget.y_spin_box.valueChanged.connect(self.set_nerve_y)
        self.nerve_prop_widget.z_spin_box.valueChanged.connect(self.set_nerve_z)
        self.nerve_prop_widget.length_spin_box.valueChanged.connect(self.set_nerve_length)
        self.nerve_prop_widget.diam_spin_box.valueChanged.connect(self.set_nerve_diam)

        self.stimulus_widget.stim_combo_box.currentTextChanged.connect(self.update_stimulus)
        self.stimulus_widget.total_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_widget.start_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_widget.stimulus_duration_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_button.clicked.connect(self.open_stimulus_widget)
        self.quasipot_button.clicked.connect(self.checkin_nerve)

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

    def add_nerve(self):
        if self.nerve_name_line_edit.text() and self.nerve_name_line_edit.text() not in self.nerve_dict:
            test = self.nerve_prop_widget.length_spin_box.value()
            self.nerve_dict[self.nerve_name_line_edit.text()] = ner.Nerve(
                x=self.nerve_prop_widget.x_spin_box.value() * scaling, y=self.nerve_prop_widget.y_spin_box.value() * scaling,
                z=self.nerve_prop_widget.z_spin_box.value() * scaling,
                length=self.nerve_prop_widget.length_spin_box.value() * scaling,
                nerv_diam=self.nerve_prop_widget.diam_spin_box.value(), name=self.nerve_name_line_edit.text())
            item = QtGui.QStandardItem(self.nerve_name_line_edit.text())
            self.nerve_list_item_model.appendRow(item)
            self.nerve_combo_box.setModel(self.nerve_list_item_model)
            self.nerve_name_line_edit.setText("")
            self.update_e_field()


    def delete_nerve(self):
        if not self.nerve_dict:
            return
        self.nerve_dict.pop(self.nerve_combo_box.currentText())
        self.nerve_list_item_model.removeRow(self.nerve_combo_box.currentIndex())
        self.nerve_combo_box.setModel(self.nerve_list_item_model)
        self.update_e_field()

    def add_axon_to_nerve(self):
        if not self.nerve_dict:
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        axon_type = self.axon_type_combo_box.currentText()
        if self.axon_type_combo_box.currentText() == "RMG":
            diameter = float(self.axon_diam_combo_box.currentText())
        else:
            diameter = self.axon_diam_spin_box.value()
        model_info = ns.AxonInformation(selected_nerve.x, selected_nerve.y, selected_nerve.z, selected_nerve.length, diameter, axon_type)
        selected_nerve.axon_infos_list.append(model_info)
        self.update_axon_list()

    def update_axon_list(self):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        self.axon_list_item_model.clear()
        for axon_info in selected_nerve.axon_infos_list:
            item = QtGui.QStandardItem(axon_info.axon_type + "_" + str(axon_info.diameter))
            self.axon_list_item_model.appendRow(item)
        self.axon_list_view.setModel(self.axon_list_item_model)

    def update_axons(self):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        for axon_info in selected_nerve.axon_infos_list:
            axon_info.x = selected_nerve.x
            axon_info.y = selected_nerve.y
            axon_info.z = selected_nerve.z
            axon_info.length = selected_nerve.length

    def delete_axon(self):
        if not self.nerve_dict:
            return
        if not self.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.axon_list_view.currentIndex()
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        del selected_nerve.axon_infos_list[selected_index.row()]
        self.update_axon_list()

    def set_axon_diam_widget(self):
        if self.axon_type_combo_box.currentText() == "RMG":
            self.axon_diam_combo_box.setVisible(True)
            self.axon_diam_spin_box.setVisible(False)
        else:
            self.axon_diam_combo_box.setVisible(False)
            self.axon_diam_spin_box.setVisible(True)

    def change_nerve_property_box(self):
        if not self.nerve_dict:
            self.nerve_prop_widget.setEnabled(False)
            return
        self.nerve_prop_widget.setEnabled(True)
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        self.update_axon_list()
        self.nerve_prop_widget.name_label.setText(self.nerve_combo_box.currentText())
        self.nerve_prop_widget.x_spin_box.setValue(selected_nerve.x/scaling)
        self.nerve_prop_widget.y_spin_box.setValue(selected_nerve.y/scaling)
        self.nerve_prop_widget.z_spin_box.setValue(selected_nerve.z/scaling)
        self.nerve_prop_widget.length_spin_box.setValue(selected_nerve.length/scaling)
        self.nerve_prop_widget.diam_spin_box.setValue(selected_nerve.nerve_diameter)
        self.update_e_field()

    def set_nerve_x(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.x = value * scaling  # convert from mm to um
        self.update_axons()
        self.update_e_field()

    def set_nerve_y(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.y = value * scaling  # convert from mm to um
        self.update_axons()
        self.update_e_field()

    def set_nerve_z(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.z = value * scaling  # convert from mm to um
        self.update_axons()
        self.update_e_field()

    def set_nerve_length(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.length = value * scaling  # convert from mm to um
        self.update_axons()
        self.update_e_field()

    def set_nerve_diam(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.nerve_diameter = value
        self.update_e_field()

    def update_e_field(self):
        self.e_field_list = self.e_field_widget.e_field_list
        if not self.nerve_dict:
            self.remove_plot()
            self.add_plot(self.e_field_widget.plot_e_field(self.e_field_list[0]))
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        fig = self.e_field_widget.plot_2d_field_with_cable(self.e_field_list[0], selected_nerve, scaling)
        self.remove_plot()
        self.add_plot(fig)

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
        self.total_time = self.stimulus_widget.total_time_spin_box.value()
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(self.time_axis, self.stimulus)
        self.stim_canvas = FigureCanvas(fig1)
        self.stimulus_widget.stimulus_layout.addWidget(self.stim_canvas)
        self.stim_canvas.draw()

    def checkin_nerve(self):
        if not self.nerve_dict:
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        if not selected_nerve.axon_infos_list:
            return
        if not self.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.axon_list_view.currentIndex()

        if hasattr(self, 'field_axon_canvas'):
            self.potential_layout.removeWidget(self.field_axon_canvas)
            self.field_axon_canvas.close()
        selected_nerve.neuron_sim = ns.NeuronSim(selected_nerve.axon_infos_list[selected_index.row()], self.e_field_list, self.time_axis, self.stimulus, self.total_time)
        selected_nerve.neuron_sim.quasipot(interpolation_radius_index)
        e_field_along_axon = selected_nerve.neuron_sim.axon.e_field_along_axon
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(e_field_along_axon)
        self.field_axon_canvas = FigureCanvas(fig1)
        self.potential_layout.addWidget(self.field_axon_canvas)
        self.field_axon_canvas.draw()

if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    main.show()
    sys.exit(app.exec_())
