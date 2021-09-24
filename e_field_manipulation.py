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

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

Ui_EFieldWidget, QWidget_EField = uic.loadUiType("ui_e_field_manipulation_widget.ui")


# This class does:
# - load field (from CST or E-Field-Matrix python file)
# - save field (E-Field-Matrix python file)
# - show field in widget
# - manipulate field (user input, offset)
class eFieldWidget(QWidget_EField, Ui_EFieldWidget):
    def __init__(self, parent = None):
        super(eFieldWidget, self).__init__(parent)
        self.setupUi(self)

        self.load_cst_button.clicked.connect(self.add_nerve)

# class and widget functions

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def load_cst_file(self, path, filename):
        storage = database.DataBase()
        # parser = file_parser.NewCSTFileParser("D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/", "Halsmodell_E_field_Phrenic.txt")
        parser = file_parser.NewCSTFileParser(path, filename)
        parser.parse_file(storage)
        storage.convert_units(1e3)  # convert mm from CST to um used for cable
        self.e_field_matrix_list = storage.generate_e_field_matrix()

    def save_e_field(self, file_name, path):
        with open("Biovoxel_phrenic_e_field_matrix_list", 'wb') as f:
            pickle.dump(self.e_field_matrix_list, f)

    def load_e_field(self, path, filename):
        # path = 'D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/'
        # path = 'H:/Doktorarbeit/Phrenicus/PeriphNeuronStim_gitHub/CST_files/'
        # with open(path + "20210325_biovoxel_e_field_matrix_list", 'rb') as e:
        with open(path + filename, 'rb') as e:
            self.e_field_matrix_list = pickle.load(e)

    # to be deleted
    def get_e_field(self, model_name):
        # storage = database.DataBase()
        # # parser = file_parser.NewCSTFileParser("D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/", "Halsmodell_E_field_Phrenic.txt")
        # parser = file_parser.NewCSTFileParser("H:/Doktorarbeit/Phrenicus/PeriphNeuronStim_gitHub/cst_files/",
        #                                       "Biovoxel_E_field.txt")
        # parser.parse_file(storage)
        # storage.convert_units(1e3)  # convert mm from CST to um used for cable
        #
        # # Save:
        # with open("biovoxel_phrenic", 'wb') as f:
        #     pickle.dump(storage, f)

        # Load:
        # with open("20210325_halsmodell", 'rb') as f:
        #     halsmodell_storage = pickle.load(f)
        # with open("20210325_biovoxel", 'rb') as f:
        #     biovoxel_storage = pickle.load(f)

        # # Save matrix list:
        # e_field_matrix_list = storage.generate_e_field_matrix()
        # with open("Biovoxel_phrenic_e_field_matrix_list", 'wb') as f:
        #     pickle.dump(e_field_matrix_list, f)

        # Open matrix list:
        path = 'D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/'
        # path = 'H:/Doktorarbeit/Phrenicus/PeriphNeuronStim_gitHub/CST_files/'
        with open(path + "20210325_biovoxel_e_field_matrix_list", 'rb') as e:
            biovoxel_e_field_matrix_list = pickle.load(e)
        with open(path + "20210325_halsmodell_e_field_matrix_list", 'rb') as e:
            halsmodell_e_field_matrix_list = pickle.load(e)

        if model_name == 'biovoxel':
            e_field_list = biovoxel_e_field_matrix_list

        else:
            e_field_list = halsmodell_e_field_matrix_list

            # for e_field in e_field_list:
            #
            #     # no = neck only
            #     e_x_no = e_field.e_x[182:228, 168:234]
            #     e_y_no = e_field.e_y[182:228, 168:234]
            #     e_z_no = e_field.e_z[182:228, 168:234]
            #
            #     e_field.e_x = np.zeros((101, 101))
            #     y_offset = 32
            #     x_offset = 17
            #     e_field.e_x[y_offset:(y_offset + e_x_no.shape[0]), x_offset:(x_offset + e_x_no.shape[1])] = e_x_no
            #     e_field.e_y = np.zeros((101, 101))
            #     e_field.e_y[y_offset:(y_offset + e_y_no.shape[0]), x_offset:(x_offset + e_y_no.shape[1])] = e_y_no
            #     e_field.e_z = np.zeros((101, 101))
            #     e_field.e_z[y_offset:(y_offset + e_z_no.shape[0]), x_offset:(x_offset + e_z_no.shape[1])] = e_z_no
            #
            #     e_field.x = e_field.x[168 - x_offset:234 + 1 + x_offset]
            #     e_field.y = e_field.y[182 - y_offset:228 + 1 + y_offset]
            #     e_field.shape = len(e_field.x[e_field.x_min:e_field.x_max+1])

        self.e_field_list = e_field_list
        fig = self.plot_e_field(e_field_list[0])
        self.add_plot(fig)
        return e_field_list

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

# ----------------------------------------------------------------------------------------------------------------------
# public functions

    def plot_e_field(self, e_field):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_field.e_y, extent=[min(e_field.y)/1e3, max(e_field.y)/1e3, min(e_field.y)/1e3, max(e_field.y)/1e3])
        # self.e_field_fig = fig1
        # fig1.colorbar(pos)
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
