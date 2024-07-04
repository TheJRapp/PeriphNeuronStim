import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

import neuron_sim as ns
from Axon_Models import mhh_model
import database

Ui_NerveWidget, QWidget_Nerve = uic.loadUiType("ui_nerve_widget.ui")
Ui_NerveDimensionWidget, QWidget_NerveDimensions = uic.loadUiType("ui_nerve_dimension_widget.ui")
from PyQt5.QtWidgets import QMessageBox

rmg_diameter_list = ["16.0", "15.0", "14.0", "12.8", "11.5", "10.0", "8.7", "7.3", "5.7"]

# This class does:


class NerveWidget(QWidget_Nerve, Ui_NerveWidget):
    nerve_shape_changed = pyqtSignal()
    axon_added = pyqtSignal()

    def __init__(self, scaling, nseg_node, nseg_internode, parent = None):
        super(NerveWidget, self).__init__(parent)

        self.setupUi(self)

        self.scaling = scaling  # ui and CST uses mm, we use um; elements from gui and e_field are scaled by self.scaling
        self.nseg_node = nseg_node
        self.nseg_internode = nseg_internode
        self.axon_list_item_model = QtGui.QStandardItemModel(self.axon_list_view)
        self.axon_list = []

        # self.nerve_dimension_button.setEnabled(False)
        self.nerve_dimension_widget = NerveDimensionWidget()

        self.anatomical_nerve = None
        self.custom_nerve= None
        self.add_custom_nerve()

        self.axon_diam_combo_box.setVisible(False)  # just visible in case RMG is selected
        self.axon_diam_combo_box.addItems(rmg_diameter_list)

        # self.nerve_name_line_edit.setText('Default')

        self.create_axon_button.clicked.connect(self.add_axon_to_nerve)
        self.delete_axon_button.clicked.connect(self.delete_axon)

        self.axon_type_combo_box.currentTextChanged.connect(self.set_axon_diam_widget)

        self.nerve_dimension_button.clicked.connect(self.show_nerve_dimension_widget)
        # TODO: is it sufficient to overwrite nerve shape or must the old one be deleted?
        self.nerve_dimension_widget.apply_button.clicked.connect(self.add_custom_nerve)

        self.anatomicalRadioButton.clicked.connect(self.nerve_shape_changed)
        self.customRadioButton.clicked.connect(self.nerve_shape_changed)
        self.anatomicalRadioButton.clicked.connect(self.update_axons)
        self.customRadioButton.clicked.connect(self.update_axons)

    def add_custom_nerve(self):
        self.custom_nerve = database.CustomNerve(
            x=self.nerve_dimension_widget.x_spin_box.value() * self.scaling,
            y=self.nerve_dimension_widget.y_spin_box.value() * self.scaling,
            z=self.nerve_dimension_widget.z_spin_box.value() * self.scaling,
            resolution=self.nerve_dimension_widget.res_spin_box.value(),
            angle=self.nerve_dimension_widget.angle_spin_box.value(),
            length=self.nerve_dimension_widget.length_spin_box.value() * self.scaling,
            nerv_diam=self.nerve_dimension_widget.diam_spin_box.value(),
            name='')
        self.nerve_shape_changed.emit()
        self.update_axons()

    def add_anatomical_nerve(self, nerve_shape):
        self.anatomical_nerve = nerve_shape
        self.anatomicalRadioButton.setEnabled(True)
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

    # ------------------------------------------------------------------------------------------------------------------
    # Axon
    # ------------------------------------------------------------------------------------------------------------------

    def add_axon_to_nerve(self):
        selected_nerve = self.get_selected_nerve()
        axon_type = self.axon_type_combo_box.currentText()
        if self.axon_type_combo_box.currentText() == "RMG":
            diameter = float(self.axon_diam_combo_box.currentText())
        else:
            diameter = self.axon_diam_spin_box.value()
        # TODO: Implement for RMG and HH
        axon_model = mhh_model.Axon(selected_nerve, self.nseg_node, self.nseg_internode,
                                    diameter)
        self.axon_list.append(axon_model)
        self.update_axon_list()

    def update_axon_list(self):
        selected_nerve = self.get_selected_nerve()
        self.axon_list_item_model.clear()
        for axon in self.axon_list:
            item = QtGui.QStandardItem(axon.type + "_" + str(axon.diameter))
            self.axon_list_item_model.appendRow(item)
        self.axon_list_view.setModel(self.axon_list_item_model)
        self.axon_added.emit()

    def update_axons(self):
        if not self.axon_list:
            return
        message_box = QMessageBox
        reply = message_box.question(self, 'Custom nerve changed', 'Rebuild existing axon models?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            new_axon_list = []
            for axon in self.axon_list:
                if axon.type == 'MHH':
                    new_axon_list.append(mhh_model.Axon(self.get_selected_nerve(), self.nseg_node, self.nseg_internode,
                                                        axon.diameter))
                    # TODO: repeat for RMG and HH
            self.axon_list = new_axon_list
        self.update_axon_list()


    def delete_axon(self):
        if not self.axon_list_view.currentIndex().isValid():
            return
        selected_index = self.axon_list_view.currentIndex()
        del self.axon_list[selected_index.row()]
        self.update_axon_list()

    def set_axon_diam_widget(self):
        if self.axon_type_combo_box.currentText() == "RMG":
            self.axon_diam_combo_box.setVisible(True)
            self.axon_diam_spin_box.setVisible(False)
        else:
            self.axon_diam_combo_box.setVisible(False)
            self.axon_diam_spin_box.setVisible(True)

    # ------------------------------------------------------------------------------------------------------------------
    # Custom nerve dimension
    # ------------------------------------------------------------------------------------------------------------------

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
        self.nerve_shape_changed.emit()

    def set_nerve_y(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.y = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.nerve_shape_changed.emit()

    def set_nerve_z(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.z = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.nerve_shape_changed.emit()

    def set_nerve_angle(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.angle = value
        self.update_axons()
        self.nerve_shape_changed.emit()

    def set_nerve_length(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.length = value * self.scaling  # convert from mm to um
        self.update_axons()
        self.nerve_shape_changed.emit()

    def set_nerve_diam(self, value):
        selected_nerve = self.custom_nerve
        selected_nerve.nerve_diameter = value
        self.nerve_shape_changed.emit()


class NerveDimensionWidget(QWidget_NerveDimensions, Ui_NerveDimensionWidget):

    def __init__(self, parent = None):
        super(NerveDimensionWidget, self).__init__(parent)

        self.setupUi(self)
