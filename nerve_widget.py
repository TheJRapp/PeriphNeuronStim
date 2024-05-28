import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import neuron_sim as ns
import database

Ui_NerveWidget, QWidget_Nerve = uic.loadUiType("ui_nerve_widget.ui")
Ui_NerveDimensionWidget, QWidget_NerveDimensions = uic.loadUiType("ui_nerve_dimension_widget.ui")

rmg_diameter_list = ["16.0", "15.0", "14.0", "12.8", "11.5", "10.0", "8.7", "7.3", "5.7"]

# This class does:


class NerveWidget(QWidget_Nerve, Ui_NerveWidget):
    e_field_changed = pyqtSignal()

    def __init__(self, scaling, nseg_node, nseg_internode, parent = None):
        super(NerveWidget, self).__init__(parent)

        self.setupUi(self)

        self.scaling = scaling  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by self.scaling
        self.nseg_node = nseg_node
        self.nseg_internode = nseg_internode
        self.axon_list_item_model = QtGui.QStandardItemModel(self.axon_list_view)

        # self.nerve_dimension_button.setEnabled(False)
        self.nerve_dimension_widget = nerveDimensionWidget()

        self.anatomical_nerve = None
        self.custom_nerve = self.add_custom_nerve()

        self.axon_diam_combo_box.setVisible(False)
        self.axon_diam_combo_box.addItems(rmg_diameter_list)

        # self.nerve_name_line_edit.setText('Default')

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

    def add_custom_nerve(self):
        custom_nerve = database.CustomNerve(
            x=self.nerve_dimension_widget.x_spin_box.value() * self.scaling,
            y=self.nerve_dimension_widget.y_spin_box.value() * self.scaling,
            z=self.nerve_dimension_widget.z_spin_box.value() * self.scaling,
            resolution=self.nerve_dimension_widget.res_spin_box.value(),
            angle=self.nerve_dimension_widget.angle_spin_box.value(),
            length=self.nerve_dimension_widget.length_spin_box.value() * self.scaling,
            nerv_diam=self.nerve_dimension_widget.diam_spin_box.value(),
            name='')
        self.e_field_changed.emit()
        return custom_nerve

    def add_anatomical_nerve(self, nerve_shape):
        self.anatomical_nerve = nerve_shape
        self.warningLabel.setText('Available')

    def get_selected_nerve(self):
        if self.anatomicalRadioButton.isChecked():
            selected_nerve = self.anatomical_nerve
        else:
            selected_nerve = self.custom_nerve
        return selected_nerve
    # def delete_nerve(self):
    #     if not self.nerve_dict:
    #         return
    #     self.nerve_dict.pop(self.nerve_combo_box.currentText())
    #     self.nerve_list_item_model.removeRow(self.nerve_combo_box.currentIndex())
    #     self.nerve_combo_box.setModel(self.nerve_list_item_model)
    #     self.update_axon_list()
    #     self.e_field_changed.emit()

    def add_axon_to_nerve(self):
        selected_nerve = self.get_selected_nerve()
        axon_type = self.axon_type_combo_box.currentText()
        if self.axon_type_combo_box.currentText() == "RMG":
            diameter = float(self.axon_diam_combo_box.currentText())
        else:
            diameter = self.axon_diam_spin_box.value()
        print(selected_nerve.x[0])
        model_info = ns.AxonInformation(selected_nerve.x[0], selected_nerve.y[0], selected_nerve.z[0], diameter,
                                        axon_type, self.nseg_node, self.nseg_internode)
        print('Check if i was here')
        selected_nerve.axon_infos_list.append(model_info)
        print('Check if i was here')
        self.update_axon_list()

    def update_axon_list(self):
        selected_nerve = self.get_selected_nerve()
        self.axon_list_item_model.clear()
        for axon_info in selected_nerve.axon_infos_list:
            item = QtGui.QStandardItem(axon_info.axon_type + "_" + str(axon_info.diameter))
            self.axon_list_item_model.appendRow(item)
        self.axon_list_view.setModel(self.axon_list_item_model)

    def update_axons(self):
        selected_nerve = self.get_selected_nerve()
        for axon_info in selected_nerve.axon_infos_list:
            axon_info.x = selected_nerve.x
            axon_info.y = selected_nerve.y
            axon_info.z = selected_nerve.z
            axon_info.angle = selected_nerve.angle
            axon_info.length = selected_nerve.length

    def delete_axon(self):
        selected_nerve = self.get_selected_nerve()
        if not self.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.axon_list_view.currentIndex()
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
        selected_nerve = self.custom_nerve
        self.update_axon_list()
        self.nerve_dimension_widget.name_label.setText(self.nerve_combo_box.currentText())
        self.nerve_dimension_widget.x_spin_box.setValue(selected_nerve.x / self.scaling)
        self.nerve_dimension_widget.y_spin_box.setValue(selected_nerve.y / self.scaling)
        self.nerve_dimension_widget.z_spin_box.setValue(selected_nerve.z / self.scaling)
        self.nerve_dimension_widget.angle_spin_box.setValue(selected_nerve.angle)
        self.nerve_dimension_widget.length_spin_box.setValue(selected_nerve.length / self.scaling)
        self.nerve_dimension_widget.diam_spin_box.setValue(selected_nerve.nerve_diameter)
        # self.e_field_changed.emit()

    def set_nerve_x(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.x = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_y(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.y = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_z(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.z = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_angle(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.angle = value
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_length(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.length = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.e_field_changed.emit()

    def set_nerve_diam(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.nerve_diameter = value
        self.e_field_changed.emit()


class nerveDimensionWidget(QWidget_NerveDimensions, Ui_NerveDimensionWidget):

    def __init__(self, parent = None):
        super(nerveDimensionWidget, self).__init__(parent)

        self.setupUi(self)
