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
Ui_PropertyWidget, QWidget = uic.loadUiType("ui_nerve_property_widget.ui")

rmg_diameter_list = ["5.7", "7.3", "8.7", "10.0", "11.5", "12.8", "14.0", "15.0", "16"]

class windowTest(QWidget, Ui_PropertyWidget):
    def __init__(self, parent = None):
        super(windowTest, self).__init__(parent)
        self.setupUi(self)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        e_field_name = 'halsmodell'
        e_field_list = em.get_e_field(e_field_name)
        self.field_plot_manager = fp.FieldPlot(e_field_list[0])

        self.add_plot(self.field_plot_manager.plot_e_field())
        self.nerve_dict = {}
        self.axon_list_item_model = QtGui.QStandardItemModel(self.axon_list_view)
        self.nerve_list_item_model = QtGui.QStandardItemModel(self.nerve_combo_box)

        self.nerve_prop_widget = windowTest()
        self.nerve_prop_widget.setEnabled(False)
        self.property_layout.addWidget(self.nerve_prop_widget)
        self.axon_diam_spin_box.setVisible(False)
        self.axon_diam_combo_box.addItems(rmg_diameter_list)
        # for diam in rmg_diameter_list:
        #     self.axon_diam_combo_box.setModel(self.nerve_list_item_model)

        # signal connections
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

    def add_nerve(self):
        if self.nerve_name_line_edit.text() and self.nerve_name_line_edit.text() not in self.nerve_dict:
            self.nerve_dict[self.nerve_name_line_edit.text()] = ner.Nerve(name=self.nerve_name_line_edit.text())
            # self.nerve_combo_box.addItem(self.nerve_name_line_edit.text())
            item = QtGui.QStandardItem(self.nerve_name_line_edit.text())
            self.nerve_list_item_model.appendRow(item)
            self.nerve_combo_box.setModel(self.nerve_list_item_model)
            self.nerve_name_line_edit.setText("")

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
            item = QtGui.QStandardItem(axon_info.type + "_" + str(axon_info.diameter))
            self.axon_list_item_model.appendRow(item)
        self.axon_list_view.setModel(self.axon_list_item_model)

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
            # self.axon_diam_layout.addWidget(self.axon_diam_combo_box)
        else:
            self.axon_diam_combo_box.setVisible(False)
            self.axon_diam_spin_box.setVisible(True)
        # if self.axon_type_combo_box.currentText() == "RMG":
        #     self.axon_diam_layout.replaceWidget(self.axon_diam_spin_box, self.axon_diam_combo_box)
        # else:
        #     self.axon_diam_layout.replaceWidget(self.axon_diam_combo_box, self.axon_diam_spin_box)

    def change_nerve_property_box(self):
        if not self.nerve_dict:
            self.nerve_prop_widget.setEnabled(False)
            return
        self.nerve_prop_widget.setEnabled(True)
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        self.update_axon_list()
        self.nerve_prop_widget.name_label.setText(self.nerve_combo_box.currentText())
        self.nerve_prop_widget.x_spin_box.setValue(selected_nerve.x)
        self.nerve_prop_widget.y_spin_box.setValue(selected_nerve.y)
        self.nerve_prop_widget.z_spin_box.setValue(selected_nerve.z)
        self.nerve_prop_widget.length_spin_box.setValue(selected_nerve.length)
        self.nerve_prop_widget.diam_spin_box.setValue(selected_nerve.nerve_diameter)
        self.update_e_field()

    def set_nerve_x(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.x = value
        self.update_e_field()

    def set_nerve_y(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.y = value
        self.update_e_field()

    def set_nerve_z(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.z = value
        self.update_e_field()

    def set_nerve_length(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.length = value
        self.update_e_field()

    def set_nerve_diam(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.nerve_diameter = value
        self.update_e_field()

    def update_e_field(self):
        if not self.nerve_dict:
            self.remove_plot()
            self.add_plot(self.field_plot_manager.plot_e_field())
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        fig = self.field_plot_manager.plot_2d_field_with_cable(selected_nerve, 1e3)
        self.remove_plot()
        self.add_plot(fig)


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    main.show()
    sys.exit(app.exec_())
