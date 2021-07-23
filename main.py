'''
@author: Rapp & Braun
'''


from PyQt5.uic import loadUiType

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
from matplotlib import pyplot as plt

Ui_MainWindow, QMainWindow = loadUiType('ui_master_sim.ui')


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        e_field_name = 'halsmodell'
        e_field_list = em.get_e_field(e_field_name)
        fig = self.plot_e_field(e_field_list[0])
        self.addmpl(fig)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                self.e_field_widget, coordinates=True)
        self.e_field_layout.addWidget(self.toolbar)

    def plot_e_field(self, e_field_matrix):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)

        ax1f1.imshow(e_field_matrix.e_y)
        plt.show()
        # fig1.colorbar(pos)
        return fig1


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets, QtCore

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    # main.addfigtolist('Default Field', fig1)
    # main.addfig('Two plots', fig2)
    # main.addfig('Pcolormesh', fig3)
    main.show()
    sys.exit(app.exec_())