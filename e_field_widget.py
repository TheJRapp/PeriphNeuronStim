import pickle
import database
import file_parser
import numpy as np
import cv2
from scipy import ndimage, misc

from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib import pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

from PyQt5.QtCore import pyqtSignal, Qt, QObject
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

Ui_EFieldWidget, QWidget_EField = uic.loadUiType("ui_e_field_widget.ui")

default_e_field_path = 'volume_box_default.pkl'
default_nerve_shape_path = 'volume_shape_default.pkl'
# This class does:
# - load field (from CST or E-Field-Matrix python file)
# - save field (E-Field-Matrix python file)
# - show field in widget
# - manipulate field (user input, offset)


class EFieldWidget(QWidget_EField, Ui_EFieldWidget):
    e_field_changed = pyqtSignal()

    def __init__(self, parent=None):
        super(EFieldWidget, self).__init__(parent)

        self.setupUi(self)
        self.updated_xlims = ()
        self.updated_ylims = ()
        self.e_field_list = self.load_default_field()
        self.configure_layer_slider()
        self.nerve_shape = self.load_default_nerve_shape()
        self.custom_nerve = None
        self.scaling = None

        self.E_FIELD_ONLY = 1
        self.NERVE_SHAPE_ONLY = 2
        self.E_FIELD_WITH_NERVE_SHAPE = 3
        self.state = self.E_FIELD_WITH_NERVE_SHAPE

        self.load_cst_button.clicked.connect(self.load_cst_file)
        self.load_e_field_button.clicked.connect(self.load_e_field)
        self.save_e_field_button.clicked.connect(self.save_e_field)
        self.confirm_button.clicked.connect(self.change_e_field)
        self.load_nerve_shape_button.clicked.connect(self.load_cst_nerve_shape)
        self.load_saved_nerve_shape_button.clicked.connect(self.load_nerve_shape)
        self.save_nerve_shape_button.clicked.connect(self.save_nerve_shape)
        self.smooth_push_button.clicked.connect(self.smooth_e_field)

        self.e_field_wtih_nerve_shape_radio_button.clicked.connect(self.state_changed)
        self.nerve_shape_only_radio_button.clicked.connect(self.state_changed)
        self.e_field_only_radio_button.clicked.connect(self.state_changed)

        self.e_field_layer_slider.valueChanged.connect(self.update_e_field_plot)

    # ------------------------------------------------------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------------------------------------------------------
    def openFileNameDialog(self, file_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  file_type, options=options)
        if fileName:
            return fileName

    def saveFileNameDialog(self, file_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  file_type, options=options)
        if fileName:
            return fileName

    def load_cst_file(self):
        filename = self.openFileNameDialog("Text Files (*.txt)")
        if not filename:
            # TODO: warning
            return
        storage = database.DataBase()
        parser = file_parser.NewCSTFileParser("", filename)
        parser.parse_file(storage)
        storage.convert_units(1e3)  # convert mm from CST to um used for cable
        self.e_field_list = storage.generate_e_field_matrix()
        # self.state = self.E_FIELD_ONLY
        self.update_e_field_plot()

    def load_e_field(self):
        filename = self.openFileNameDialog("Pickle Files (*.pkl)")
        # filename = self.openFileNameDialog("All Files (*);;Python Files (*.py)")

        if not filename:
            # TODO: warning
            return
        with open(filename, 'rb') as e:
            self.e_field_list = pickle.load(e)
        # self.state = self.E_FIELD_ONLY
        self.update_e_field_plot()

    def save_e_field(self):
        filename = self.saveFileNameDialog("Pickle Files (*.pkl)")
        if not filename:
            # TODO: warning
            return
        if filename[-4:] == ".pkl":
            with open(filename, 'wb') as f:
                pickle.dump(self.e_field_list, f)
        else:
            with open(filename + ".pkl", 'wb') as f:
                pickle.dump(self.e_field_list, f)

    def load_cst_nerve_shape(self):
        filename = self.openFileNameDialog("Text Files (*.txt)")
        if not filename:
            # TODO: warning
            return
        storage = database.DataBase()
        parser = file_parser.NewCSTFileParser("", filename)
        parser.parse_file(storage)
        storage.convert_units(1e3)  # convert mm from CST to um used for cable
        self.nerve_shape = storage.generate_nerve_shape()
        # self.state = self.NERVE_SHAPE_ONLY
        # self.nerve_shape_only_radio_button.setChecked(True)
        self.e_field_wtih_nerve_shape_radio_button.setEnabled(True)
        self.nerve_shape_only_radio_button.setEnabled(True)
        self.update_e_field_plot()

    def load_nerve_shape(self):
        filename = self.openFileNameDialog("Pickle Files (*.pkl)")
        if not filename:
            # TODO: warning
            return
        with open(filename, 'rb') as e:
            self.nerve_shape = pickle.load(e)
        # self.state = self.NERVE_SHAPE_ONLY
        # self.nerve_shape_only_radio_button.setChecked(True)
        self.e_field_wtih_nerve_shape_radio_button.setEnabled(True)
        self.nerve_shape_only_radio_button.setEnabled(True)
        self.update_e_field_plot()

    def save_nerve_shape(self):
        filename = self.saveFileNameDialog("Pickle Files (*.pkl)")
        if not filename:
            # TODO: warning
            return
        if filename[-4:] == ".pkl":
            with open(filename, 'wb') as f:
                pickle.dump(self.nerve_shape, f)
        else:
            with open(filename + ".pkl", 'wb') as f:
                pickle.dump(self.nerve_shape, f)

    def load_default_field(self):
        with open(default_e_field_path, 'rb') as e:
            self.e_field_list = pickle.load(e)
        fig = self.plot_e_field(self.e_field_list[0])
        self.add_plot(fig)
        return self.e_field_list

    def load_default_nerve_shape(self):
        with open(default_nerve_shape_path, 'rb') as e:
            self.nerve_shape = pickle.load(e)
        return self.nerve_shape
    # ------------------------------------------------------------------------------------------------------------------
    # Update main.py
    # ------------------------------------------------------------------------------------------------------------------
    def get_current_field_plot(self):
        if self.state == self.NERVE_SHAPE_ONLY:
            return self.plot_nerve_shape(self.nerve_shape)
        elif self.state == self.E_FIELD_WITH_NERVE_SHAPE:
            # ToDo: return e_field with nerve shape
            return self.plot_nerve_shape(self.nerve_shape)
            # return self.e_field_plot_with_nerve_shape(self.e_field_list[15], self.nerve_shape)
        else:
            if self.custom_nerve and self.scaling:
                return self.plot_2d_field_with_cable(self.e_field_list[15], self.custom_nerve, self.scaling)
            else:
                return self.plot_e_field(self.e_field_list[15])

    def change_e_field(self):
        if hasattr(self, 'e_field_list_mod'):
            self.e_field_list = self.e_field_list_mod
        self.e_field_changed.emit()

    def state_changed(self):
        if self.e_field_wtih_nerve_shape_radio_button.isChecked() and self.nerve_shape:
            self.state = self.E_FIELD_WITH_NERVE_SHAPE
        elif self.nerve_shape_only_radio_button.isChecked():
            self.state = self.NERVE_SHAPE_ONLY
        else:
            self.state = self.E_FIELD_ONLY

    # ------------------------------------------------------------------------------------------------------------------
    # Internal plot
    # ------------------------------------------------------------------------------------------------------------------

    def update_e_field_plot(self):
        if self.state == self.NERVE_SHAPE_ONLY:
            fig = self.plot_nerve_shape(self.nerve_shape)
            self.e_field_layer_slider.setEnabled(False)
        else:
            self.configure_layer_slider()
            self.layer_label.setText(str(self.e_field_list[self.e_field_layer_slider.value()].layer))
            fig = self.plot_e_field(self.e_field_list[self.e_field_layer_slider.value()])
            self.e_field_layer_slider.setEnabled(True)
        self.remove_plot()
        self.add_plot(fig)

    def add_plot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.e_field_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                self.e_field_widget, coordinates=True)
        self.e_field_layout.addWidget(self.toolbar)

    def remove_plot(self,):
        # if hasattr(self, 'canvas'):
        self.e_field_layout.removeWidget(self.canvas)
        self.canvas.close()
        self.e_field_layout.removeWidget(self.toolbar)
        self.toolbar.close()

    # ------------------------------------------------------------------------------------------------------------------
    # Create figures for e_field_only, e_field_only_with_custom_nerve, nerve_shape_only, and e_field_with nerve_shape
    # ------------------------------------------------------------------------------------------------------------------

    def plot_e_field(self, e_field):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        pos=ax1f1.imshow(e_field.e_y, extent=[min(e_field.x)/1e3, max(e_field.x)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3])
        # self.e_field_fig = fig1
        fig1.colorbar(pos)

        ax1f1.callbacks.connect('xlim_changed', self.on_xlims_change)
        ax1f1.callbacks.connect('ylim_changed', self.on_ylims_change)

        return fig1

    def plot_nerve_shape(self, nerve_shape):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111, projection='3d')
        ax1f1.scatter3D(nerve_shape.x, nerve_shape.y, nerve_shape.z, c=nerve_shape.e_y)
        # ax = plt.gca(projection='3d')
        # ax.scatter3D(nerve_shape.x/1000, nerve_shape.y/1000, nerve_shape.z/1000, c=nerve_shape.e_y)
        # ax.set_xlabel('x in mm')
        # ax.set_ylabel('y in mm')
        # ax.set_zlabel('z in mm')
        # plt.show()

        return fig1

    def plot_2d_field_with_cable(self, e_field, nerve, scale):
        e_modified = e_field.e_y.copy()
        xdim = round(e_field.xshape/2)
        ydim = round(e_field.yshape / 2)

        xrange = nerve.length * np.cos(nerve.angle / 360 * 2 * np.pi)
        yrange = nerve.length * np.sin(nerve.angle / 360 * 2 * np.pi)

        img_mod = cv2.line(e_modified, (int(nerve.x/scale + xdim), int(nerve.y/scale + ydim)), (int(nerve.x/scale + xdim +
                          xrange/scale), int(nerve.y/scale + ydim + yrange/scale)), (255, 0, 0), 5)

        fig1 = Figure()
        # cv2.imshow("Line", img_mod)
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_modified, extent=[min(e_field.y)/scale, max(e_field.y)/scale, min(e_field.x)/scale, max(e_field.x)/scale])
        return fig1

    def e_field_plot_with_nerve_shape(self, e_field, nerve_shape):
        pass

    def on_xlims_change(self, event_ax):
        print("updated xlims: ", event_ax.get_xlim())
        self.updated_xlims = event_ax.get_xlim()
        # self.cut_e_field()

    def on_ylims_change(self, event_ax):
        print("updated ylims: ", event_ax.get_ylim())
        self.updated_ylims = event_ax.get_ylim()
        # self.cut_e_field()

    def configure_layer_slider(self):
        self.e_field_layer_slider.setRange(0, len(self.e_field_list)-1)

    # ------------------------------------------------------------------------------------------------------------------
    # Modify E-field
    # ------------------------------------------------------------------------------------------------------------------

    def smooth_e_field(self):
        for field in self.e_field_list:
            e_field = field.e_x
            filtered_e_field = ndimage.uniform_filter(e_field, size=20)
            field.e_x = filtered_e_field
            e_field = field.e_y
            filtered_e_field = ndimage.uniform_filter(e_field, size=20)
            field.e_y = filtered_e_field
            e_field = field.e_z
            filtered_e_field = ndimage.uniform_filter(e_field, size=20)
            field.e_z = filtered_e_field
        self.update_e_field_plot()

class State(QObject):
    e_field_changed = pyqtSignal()

    def __init__(self, parent=None):
        super(State, self).__init__(parent)
        self.E_FIELD_ONLY = 1
        self.NERVE_SHAPE_ONLY = 2
        self.E_FIELD_WITH_NERVE_SHAPE = 3

        self.state = self.E_FIELD_ONLY