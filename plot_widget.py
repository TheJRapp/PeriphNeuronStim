from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

Ui_PlotWidget, QWidget_Plot = uic.loadUiType("ui_plot_widget.ui")

class CustomFigure():
    def __init__(self, figure, label):
        self.fig = figure
        self.label = label


class PlotWidget(QWidget_Plot, Ui_PlotWidget):
    plot_requested = pyqtSignal()

    def __init__(self, parent = None):
        super(PlotWidget, self).__init__(parent)
        self.setupUi(self)

        self.figure_list = []
        self.plot_list_item_model = QtGui.QStandardItemModel(self.plot_list_view)
        self.show_plot_button.clicked.connect(self.plot_figure)

    def add_figure(self, figure, label):
        for i in range(len(self.figure_list)):
            if self.figure_list[i].label == label:
                self.figure_list[i].fig = figure
                self.update_plot_list()
                return
        self.figure_list.append(CustomFigure(figure, label))
        self.update_plot_list()

    def clear_figures(self):
        self.figure_list = []
        self.update_plot_list()

    def plot_figure(self):
        self.plot_requested.emit()

    def get_plot(self):
        current_index = self.plot_list_view.currentIndex().row()
        if self.figure_list:
            return self.figure_list[current_index].fig

    def update_plot_list(self):
        self.plot_list_item_model.clear()
        for custom_fig in self.figure_list:
            item = QtGui.QStandardItem(custom_fig.label)
            self.plot_list_item_model.appendRow(item)
        self.plot_list_view.setModel(self.plot_list_item_model)