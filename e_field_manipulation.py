import pickle
import database
import file_parser
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

Ui_EFieldWidget, QWidget_EField = uic.loadUiType("ui_e_field_manipulation_widget.ui")

default_e_field_path = 'H:/Doktorarbeit/Phrenicus/e_field_data/biovoxel_phrenic_e_field_matrix_list'
from matplotlib.backend_bases import key_press_handler

# This class does:
# - load field (from CST or E-Field-Matrix python file)
# - save field (E-Field-Matrix python file)
# - show field in widget
# - manipulate field (user input, offset)
class eFieldWidget(QWidget_EField, Ui_EFieldWidget):
    e_field_changed = pyqtSignal()

    def __init__(self, parent = None):
        super(eFieldWidget, self).__init__(parent)

        self.setupUi(self)
        self.press_coordinates = ()
        self.release_coordinates = ()

        self.load_cst_button.clicked.connect(self.load_cst_file)
        self.load_e_field_button.clicked.connect(self.load_e_field)
        self.save_e_field_button.clicked.connect(self.save_e_field)
        self.confirm_button.clicked.connect(self.change_e_field)


# class and widget functions
    def openFileNameDialog(self, file_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  file_type, options=options)
        if fileName:
            return fileName

    def saveFileNameDialog(self, file_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
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
        # parser = file_parser.NewCSTFileParser("D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/", "Halsmodell_E_field_Phrenic.txt")
        parser = file_parser.NewCSTFileParser("", filename)
        parser.parse_file(storage)
        storage.convert_units(1e3)  # convert mm from CST to um used for cable
        self.e_field_list = storage.generate_e_field_matrix()
        self.update_e_field()

    def load_e_field(self):
        filename = self.openFileNameDialog("Pickle Files (*.pkl)")
        # filename = self.openFileNameDialog("All Files (*);;Python Files (*.py)")

        if not filename:
            # TODO: warning
            return
        # path = 'D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/'
        # path = 'H:/Doktorarbeit/Phrenicus/PeriphNeuronStim_gitHub/CST_files/'
        # with open(path + "20210325_biovoxel_e_field_matrix_list", 'rb') as e:
        with open(filename, 'rb') as e:
            self.e_field_list = pickle.load(e)
        self.update_e_field()

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

    def update_e_field(self):
        fig = self.plot_e_field(self.e_field_list[0])
        self.remove_plot()
        self.add_plot(fig)

    # to be deleted
    def get_e_field(self, model_name):
        with open(default_e_field_path, 'rb') as e:
            self.e_field_list = pickle.load(e)
        fig = self.plot_e_field(self.e_field_list[0])
        self.add_plot(fig)
        return self.e_field_list

    def change_e_field(self):
        self.e_field_changed.emit()

    def add_plot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.canvas.setFocus()
        self.canvas.setFocusPolicy(Qt.StrongFocus)
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

# ----------------------------------------------------------------------------------------------------------------------
# public functions

    def plot_e_field(self, e_field):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_field.e_y, extent=[min(e_field.y)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3, max(e_field.y)/1e3])
        # self.e_field_fig = fig1
        # fig1.colorbar(pos)

        cid = fig1.canvas.mpl_connect('button_press_event', self.onclick)
        cidr = fig1.canvas.mpl_connect('button_release_event', self.relclick)
        cidk = fig1.canvas.mpl_connect('key_press_event', self.keyclick)

        return fig1

    def plot_2d_field_with_cable(self, e_field, nerve, scale):
        e_modified = e_field.e_y.copy()
        dim = round(e_field.shape/2)
        # for x, y in zip(nerve.x, nerve.y):
        #     e_modified[(int(y/scale + dim)), (int(x/scale + dim))] = 800

        e_modified[int(nerve.y/scale + dim):int(nerve.y/scale + dim + (nerve.length/scale)), int(nerve.x/scale + dim)] = 800

        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_modified, extent=[min(e_field.y)/scale, max(e_field.y)/scale, min(e_field.y)/scale, max(e_field.y)/scale])
        return fig1

    def onclick(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        self.press_coordinates = (event.x, event.y)

    def relclick(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        self.release_coordinates = (event.x, event.y)

    def keyclick(self, event):
        print("I was here")
        key_press_handler(event, self.canvas, self.toolbar)