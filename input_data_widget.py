import pickle
import database
import file_parser
import misc_functions
import numpy as np

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

Ui_InputDataWidget, QWidget_InputData = uic.loadUiType("ui_input_data_widget.ui")

default_e_field_path = 'volume_box_default.pkl'
default_nerve_shape_path = 'volume_shape_default.pkl'
# This class does:
# - load field (from CST or E-Field-Matrix python file)
# - save field (E-Field-Matrix python file)
# - show field in widget
# - manipulate field (user input, offset)


class InputDataWidget(QWidget_InputData, Ui_InputDataWidget):
    e_field_changed = pyqtSignal()
    nerve_shape_changed = pyqtSignal()

    def __init__(self, parent=None):
        super(InputDataWidget, self).__init__(parent)

        self.setupUi(self)
        self.updated_xlims = ()
        self.updated_ylims = ()
        self.add_e_field_plot(plt.figure())
        self.add_nerve_shape_plot(plt.figure())
        # self.configure_layer_slider()
        # self.nerve_shape = self.load_default_nerve_shape()
        self.custom_nerve = None
        self.nerve_shape = None
        self.e_field = None
        # self.nerve_shape = database.NerveShape(0,0,0,[],[],[],[],[],[])
        self.scaling = None

        self.load_e_field_button.clicked.connect(self.load_e_field)
        self.save_e_field_button.clicked.connect(self.save_e_field)
        self.smooth_push_button.clicked.connect(self.smooth_e_field)
        self.ex_button.clicked.connect(self.update_e_field_plot)
        self.ey_button.clicked.connect(self.update_e_field_plot)
        self.ez_button.clicked.connect(self.update_e_field_plot)

        self.load_nerve_shape_button.clicked.connect(self.load_nerve_shape)
        self.save_nerve_shape_button.clicked.connect(self.save_nerve_shape)
        self.xy_button.clicked.connect(self.update_nerve_shape_plot)
        self.xz_button.clicked.connect(self.update_nerve_shape_plot)
        self.yz_button.clicked.connect(self.update_nerve_shape_plot)
        self.smooth_nerve_shape_button.clicked.connect(self.smooth_nerve_shape)

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

    def load_e_field(self):
        filename = self.openFileNameDialog("Pickle Files (*.pkl);; Text Files (*.txt *.csv)")
        # filename = self.openFileNameDialog("All Files (*);;Python Files (*.py)")

        if not filename:
            # TODO: warning
            return

        if filename.endswith('.pkl'):
            with open(filename, 'rb') as e:
                self.e_field = pickle.load(e)
        elif filename.endswith('.txt'):
            storage = database.DataBase()
            parser = file_parser.NewCSTFileParser("", filename)
            parser.parse_file(storage)
            storage.convert_units(1e3)  # convert mm from CST to um used for cable
            self.e_field = storage.generate_e_field_matrix()

        self.e_field_changed.emit()
        self.update_e_field_plot()

    def save_e_field(self):
        filename = self.saveFileNameDialog("Pickle Files (*.pkl)")
        if not filename:
            # TODO: warning
            return
        if filename[-4:] == ".pkl":
            with open(filename, 'wb') as f:
                pickle.dump(self.e_field, f)
        else:
            with open(filename + ".pkl", 'wb') as f:
                pickle.dump(self.e_field, f)

    def load_nerve_shape(self):
        filename = self.openFileNameDialog("Pickle Files (*.pkl);; Text Files (*.txt *.csv)")
        if not filename:
            # TODO: warning
            return
        if filename.endswith('.pkl'):
            with open(filename, 'rb') as e:
                self.nerve_shape = pickle.load(e)
        elif filename.endswith('.txt'):
            storage = database.DataBase()
            parser = file_parser.NewCSTFileParser("", filename)
            parser.parse_file(storage)
            storage.convert_units(1e3)  # convert mm from CST to um used for cable
            self.nerve_shape = storage.generate_nerve_shape()
        elif filename.endswith('.csv'):
            storage = database.DataBase()
            parser = file_parser.CSVNerveShapeParser("", filename)
            parser.parse_file(storage)
            # storage.convert_units(1e3)  # convert mm from CST to um used for cable
            self.nerve_shape = storage.generate_nerve_shape()
        else:
            print('Error: Loading nerve shape')

        self.nerve_shape_changed.emit()
        self.update_nerve_shape_plot()

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

    # ------------------------------------------------------------------------------------------------------------------
    # Update main.py
    # ------------------------------------------------------------------------------------------------------------------
    def get_current_e_field_plot(self):
        return self.plot_e_field(self.e_field, self.e_field_layer_slider.value())

    def get_e_field_with_custom_nerve_plot(self):
        if self.custom_nerve:
            return self.plot_2d_field_with_cable(self.e_field, self.e_field_layer_slider.value(), self.custom_nerve, self.scaling)
        else:
            return self.plot_e_field(self.e_field, self.e_field_layer_slider.value())

    def get_nerve_shape_plot(self):
        return self.plot_3d_nerve_shape(self.nerve_shape)

    # ------------------------------------------------------------------------------------------------------------------
    # Internal plot
    # ------------------------------------------------------------------------------------------------------------------

    def update_e_field_plot(self):
        if not self.e_field:
            return
        if self.configure_layer_slider():
            self.layer_label.setText(str(self.e_field.z[self.e_field_layer_slider.value()]))
            fig = self.plot_e_field(self.e_field, self.e_field_layer_slider.value())
            self.e_field_layer_slider.setEnabled(True)
        else:
            fig = self.plot_e_field(self.e_field, 0)
        self.remove_e_field_plot()
        self.add_e_field_plot(fig)

    def update_nerve_shape_plot(self):
        if not self.nerve_shape:
            return
        if self.xy_button.isChecked():
            fig = self.plot_xy_nerve_shape(self.nerve_shape)
        elif self.xz_button.isChecked():
            fig = self.plot_xz_nerve_shape(self.nerve_shape)
        else:
            fig = self.plot_yz_nerve_shape(self.nerve_shape)
        self.remove_nerve_shape_plot()
        self.add_nerve_shape_plot(fig)

    def add_e_field_plot(self, fig):
        self.efield_canvas = FigureCanvas(fig)
        self.efield_canvas.setFocusPolicy(Qt.StrongFocus)
        self.efield_canvas.setFocus()
        self.e_field_layout.addWidget(self.efield_canvas)
        self.efield_canvas.draw()
        self.toolbar = NavigationToolbar(self.efield_canvas,
                                         self.e_field_widget, coordinates=True)
        self.e_field_layout.addWidget(self.toolbar)

    def remove_e_field_plot(self, ):
        # if hasattr(self, 'canvas'):
        self.e_field_layout.removeWidget(self.efield_canvas)
        self.efield_canvas.close()
        self.e_field_layout.removeWidget(self.toolbar)
        self.toolbar.close()

    def add_nerve_shape_plot(self, fig):
        self.nerve_shape_canvas = FigureCanvas(fig)
        self.nerve_shape_canvas.setFocusPolicy(Qt.StrongFocus)
        self.nerve_shape_canvas.setFocus()
        self.nerve_shape_layout.addWidget(self.nerve_shape_canvas)
        self.nerve_shape_canvas.draw()
        self.toolbar = NavigationToolbar(self.nerve_shape_canvas,
                                         self.nerve_shape_widget, coordinates=True)
        self.nerve_shape_layout.addWidget(self.toolbar)

    def remove_nerve_shape_plot(self, ):
        # if hasattr(self, 'canvas'):
        self.nerve_shape_layout.removeWidget(self.nerve_shape_canvas)
        self.nerve_shape_canvas.close()
        self.nerve_shape_layout.removeWidget(self.toolbar)
        self.toolbar.close()

    # ------------------------------------------------------------------------------------------------------------------
    # Create figures for e_field_only, e_field_only_with_custom_nerve, nerve_shape_only, and e_field_with nerve_shape
    # ------------------------------------------------------------------------------------------------------------------

    def plot_e_field(self, e_field, layer):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        if self.ex_button.isChecked():
            pos=ax1f1.imshow(e_field.e_x[:,:,layer], extent=[min(e_field.x)/1e3, max(e_field.x)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3])
        elif self.ez_button.isChecked():
            pos=ax1f1.imshow(e_field.e_z[:,:,layer], extent=[min(e_field.x)/1e3, max(e_field.x)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3])
        else:
            pos=ax1f1.imshow(e_field.e_y[:,:,layer], extent=[min(e_field.x)/1e3, max(e_field.x)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3])
        ax1f1.set_xlabel('x')
        ax1f1.set_ylabel('y')
        fig1.colorbar(pos)
        ax1f1.callbacks.connect('xlim_changed', self.on_xlims_change)
        ax1f1.callbacks.connect('ylim_changed', self.on_ylims_change)
        return fig1

    def plot_3d_nerve_shape(self, nerve_shape):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111, projection='3d')
        ax1f1.scatter3D(nerve_shape.x, nerve_shape.y, nerve_shape.z)

        return fig1

    def plot_xy_nerve_shape(self, nerve_shape):
        fig = Figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(nerve_shape.x, nerve_shape.y)
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        return fig

    def plot_xz_nerve_shape(self, nerve_shape):
        fig = Figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(nerve_shape.x, nerve_shape.z)
        ax1.set_xlabel('x')
        ax1.set_ylabel('z')
        return fig

    def plot_yz_nerve_shape(self, nerve_shape):
        fig = Figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(nerve_shape.y, nerve_shape.z)
        ax1.set_xlabel('y')
        ax1.set_ylabel('z')
        return fig

    # def plot_2d_field_with_cable(self, e_field, layer, nerve, scale):
    #     e_modified = e_field.e_y[:,:,layer].copy()
    #     xdim = round(len(e_field.x)/2)
    #     ydim = round(len(e_field.y) / 2)
    #
    #     xrange = nerve.length * np.cos(nerve.angle / 360 * 2 * np.pi)
    #     yrange = nerve.length * np.sin(nerve.angle / 360 * 2 * np.pi)
    #     test_1 = nerve.y[0]/scale
    #     test_2 = abs(e_field.y[1] - e_field.y[0])
    #     test_3 = int((nerve.y[0] / scale + ydim) / abs(e_field.y[1] - e_field.y[0]))
    #     img_mod = cv2.line(e_modified, (int(nerve.x[0]/scale + xdim), int( (nerve.y[0]/scale + ydim) / abs(e_field.y[1]/scale - e_field.y[0]/scale) )), (int(nerve.x[0]/scale + xdim +
    #                       xrange/scale), int(nerve.y[0]/scale + ydim + yrange/scale)), (255, 0, 0), 5)
    #
    #     fig1 = Figure()
    #     # cv2.imshow("Line", img_mod)
    #     ax1f1 = fig1.add_subplot(111)
    #     ax1f1.imshow(e_modified, extent=[min(e_field.y)/scale, max(e_field.y)/scale, max(e_field.x)/scale, min(e_field.x)/scale])
    #     return fig1

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
        if self.ex_button.isChecked():
            if (min(self.e_field.e_x.shape)-1) > 1:
                self.e_field_layer_slider.setRange(0, len(self.e_field.e_x[1,1,:])-1)
                return True
            else:
                self.e_field_layer_slider.setEnabled(False)
                return False
        elif self.ez_button.isChecked():
            if (min(self.e_field.e_z.shape)-1) > 1:
                self.e_field_layer_slider.setRange(0, len(self.e_field.e_z[1,1,:])-1)
                return True
            else:
                self.e_field_layer_slider.setEnabled(False)
                return False
        else:
            if (min(self.e_field.e_y.shape)-1) > 1:
                self.e_field_layer_slider.setRange(0, len(self.e_field.e_y[1,1,:])-1)
                return True
            else:
                self.e_field_layer_slider.setEnabled(False)
                return False

    # ------------------------------------------------------------------------------------------------------------------
    # Modify E-field
    # ------------------------------------------------------------------------------------------------------------------

    def smooth_e_field(self):
        if not self.e_field:
            return
        filtered_e_field = ndimage.uniform_filter(self.e_field.e_x, size=20)
        self.e_field.e_x = filtered_e_field
        filtered_e_field = ndimage.uniform_filter(self.e_field.e_y, size=20)
        self.e_field.e_y = filtered_e_field
        filtered_e_field = ndimage.uniform_filter(self.e_field.e_z, size=20)
        self.e_field.e_z = filtered_e_field
        self.e_field_changed.emit()
        self.update_e_field_plot()

    def smooth_nerve_shape(self):
        if not self.nerve_shape:
            return
        self.nerve_shape.y = np.asarray(misc_functions.moving_average(self.nerve_shape.y, 15))
        self.nerve_shape.y = np.asarray(misc_functions.moving_average(self.nerve_shape.y, 15))
        self.nerve_shape.z = np.asarray(misc_functions.moving_average(self.nerve_shape.z, 15))
        self.nerve_shape_changed.emit()