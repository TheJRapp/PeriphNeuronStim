import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog


Ui_MonteCarloWidget, QWidget_MonteCarlo = uic.loadUiType("ui_nerve_widget.ui")
Ui_AxonDimensionSweepWidget, QWidget_AxonDimensionSweep = uic.loadUiType("ui_nerve_dimension_widget.ui")


class monteCarloWidget(QWidget_MonteCarlo, Ui_MonteCarloWidget):
    e_field_changed = pyqtSignal()

    def __init__(self, parent = None):
        super(monteCarloWidget, self).__init__(parent)

        self.setupUi(self)
