'''
@author: Rapp & Braun
'''


from PyQt5.uic import loadUiType
from PyQt5 import uic

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


# from PySide2.QtUiTools import QUiLoader
# from PySide2.QtCore import QFile

Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')
Ui_PropertyWidget, QWidget = uic.loadUiType("ui_nerve_property_widget.ui")

class windowTest(QWidget, Ui_PropertyWidget):
    def __init__(self, parent = None):
        super(windowTest, self).__init__(parent)
        self.setupUi(self)

# def create_widget():
#     ui_file = QFile("ui_nerve_property_widget.ui")
#     # if ui_file.open(QFile.ReadOnly):
#     ui_file.open(QFile.ReadOnly)
#     loader = QUiLoader()
#     window = loader.load(ui_file)
#     ui_file.close()
#     return window


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        e_field_name = 'halsmodell'
        e_field_list = em.get_e_field(e_field_name)
        self.e_field_fig = self.plot_e_field(e_field_list[0])
        self.add_plot(self.e_field_fig)
        self.nerve_dict = {}

        self.add_nerve_button.clicked.connect(self.add_nerve)
        self.nerve_combo_box.currentTextChanged.connect(self.change_property_box)
    #
    def plot_e_field(self, e_field_matrix):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_field_matrix.e_y)
        self.e_field_fig = fig1
        # fig1.colorbar(pos)
        return fig1

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
        if self.nerve_name_line_edit.text():
            self.nerve_dict[self.nerve_name_line_edit.text()] = ner.Nerve(name=self.nerve_name_line_edit.text())
            self.nerve_combo_box.addItem(self.nerve_name_line_edit.text())

    def add_axon_to_nerve(self):


    def change_property_box(self):
        a = 1
        self.prop_widget = windowTest()
        self.property_layout.addWidget(self.prop_widget)


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    main.show()
    sys.exit(app.exec_())
