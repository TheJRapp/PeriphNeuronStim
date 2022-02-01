import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import nerve as ner
import neuron_sim as ns

Ui_NerveWidget, QWidget_Nerve = uic.loadUiType("ui_nerve_widget.ui")
Ui_NerveDimensionWidget, QWidget_NerveDimensions = uic.loadUiType("ui_nerve_dimension_widget.ui")


class nerveWidget(QWidget_Nerve, Ui_NerveWidget):
    e_field_changed = pyqtSignal()

    def __init__(self, parent = None):
        super(nerveWidget, self).__init__(parent)

        self.setupUi(self)

        self.nerve_dict = {}
        self.axon_list_item_model = QtGui.QStandardItemModel(self.axon_list_view)
        self.nerve_list_item_model = QtGui.QStandardItemModel(self.nerve_combo_box)

        self.nerve_dimension_button.setEnabled(False)
        self.nerve_dimension_widget = nerveDimensionWidget()

        self.axon_diam_combo_box.setVisible(False)
        self.axon_diam_combo_box.addItems(rmg_diameter_list)

        self.add_nerve_button.clicked.connect(self.add_nerve)
        self.delete_nerve_button.clicked.connect(self.delete_nerve)
        self.nerve_combo_box.currentTextChanged.connect(self.change_nerve_property_box)
        self.add_axon_button.clicked.connect(self.add_axon_to_nerve)
        self.delete_axon_button.clicked.connect(self.delete_axon)

        self.axon_type_combo_box.currentTextChanged.connect(self.set_axon_diam_widget)

        self.nerve_dimension_button.clicked.connect(self.show_nerve_dimension_widget)

        self.nerve_dimension_widget.x_spin_box.valueChanged.connect(self.set_nerve_x)
        self.nerve_dimension_widget.y_spin_box.valueChanged.connect(self.set_nerve_y)
        self.nerve_dimension_widget.z_spin_box.valueChanged.connect(self.set_nerve_z)
        self.nerve_dimension_widget.angle_spin_box.valueChanged.connect(self.set_nerve_angle)
        self.nerve_dimension_widget.length_spin_box.valueChanged.connect(self.set_nerve_length)
        self.nerve_dimension_widget.diam_spin_box.valueChanged.connect(self.set_nerve_diam)

    def add_nerve(self):
        if self.nerve_name_line_edit.text() and self.nerve_name_line_edit.text() not in self.nerve_dict:
            self.nerve_dict[self.nerve_name_line_edit.text()] = ner.Nerve(
                x=self.nerve_dimension_widget.x_spin_box.value() * scaling,
                y=self.nerve_dimension_widget.y_spin_box.value() * scaling,
                z=self.nerve_dimension_widget.z_spin_box.value() * scaling,
                angle=self.nerve_dimension_widget.angle_spin_box.value(),
                length=self.nerve_dimension_widget.length_spin_box.value() * scaling,
                nerv_diam=self.nerve_dimension_widget.diam_spin_box.value(),
                name=self.nerve_name_line_edit.text())
            item = QtGui.QStandardItem(self.nerve_name_line_edit.text())
            self.nerve_list_item_model.appendRow(item)
            self.nerve_combo_box.setModel(self.nerve_list_item_model)
            self.nerve_name_line_edit.setText("")
            self.e_field_changed.emit()

    def delete_nerve(self):
        if not self.nerve_dict:
            return
        self.nerve_dict.pop(self.nerve_combo_box.currentText())
        self.nerve_list_item_model.removeRow(self.nerve_combo_box.currentIndex())
        self.nerve_combo_box.setModel(self.nerve_list_item_model)
        self.update_axon_list()
        self.e_field_changed.emit()

    def add_axon_to_nerve(self):
        if not self.nerve_dict:
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        axon_type = self.axon_type_combo_box.currentText()
        if self.axon_type_combo_box.currentText() == "RMG":
            diameter = float(self.axon_diam_combo_box.currentText())
        else:
            diameter = self.axon_diam_spin_box.value()
        model_info = ns.AxonInformation(selected_nerve.x, selected_nerve.y, selected_nerve.z, selected_nerve.angle,
                                        selected_nerve.length, diameter, axon_type)
        selected_nerve.axon_infos_list.append(model_info)
        self.update_axon_list()

    def update_axon_list(self):
        if not self.nerve_dict:
            self.axon_list_item_model.clear()
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        self.axon_list_item_model.clear()
        for axon_info in selected_nerve.axon_infos_list:
            item = QtGui.QStandardItem(axon_info.axon_type + "_" + str(axon_info.diameter))
            self.axon_list_item_model.appendRow(item)
        self.axon_list_view.setModel(self.axon_list_item_model)

    def update_axons(self):
        if not self.nerve_dict:
            return
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        for axon_info in selected_nerve.axon_infos_list:
            axon_info.x = selected_nerve.x
            axon_info.y = selected_nerve.y
            axon_info.z = selected_nerve.z
            axon_info.angle = selected_nerve.angle
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

    def show_nerve_dimension_widget(self):
        self.nerve_dimension_widget.show()

    def change_nerve_property_box(self):
        if not self.nerve_dict:
            self.nerve_dimension_button.setEnabled(False)
            return
        self.nerve_dimension_button.setEnabled(True)
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        self.update_axon_list()
        self.nerve_dimension_widget.name_label.setText(self.nerve_combo_box.currentText())
        self.nerve_dimension_widget.x_spin_box.setValue(selected_nerve.x / scaling)
        self.nerve_dimension_widget.y_spin_box.setValue(selected_nerve.y / scaling)
        self.nerve_dimension_widget.z_spin_box.setValue(selected_nerve.z / scaling)
        self.nerve_dimension_widget.angle_spin_box.setValue(selected_nerve.angle)
        self.nerve_dimension_widget.length_spin_box.setValue(selected_nerve.length / scaling)
        self.nerve_dimension_widget.diam_spin_box.setValue(selected_nerve.nerve_diameter)
        # self.e_field_changed.emit()

    def set_nerve_x(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.x = value * scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_y(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.y = value * scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_z(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.z = value * scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_angle(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.angle = value
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_length(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.length = value * scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_diam(self, value):
        selected_nerve = self.nerve_dict[self.nerve_combo_box.currentText()]
        selected_nerve.nerve_diameter = value
        self.e_field_changed.emit()


class nerveDimensionWidget(QWidget_NerveDimensions, Ui_NerveDimensionWidget):

    def __init__(self, parent = None):
        super(nerveDimensionWidget, self).__init__(parent)

        self.setupUi(self)