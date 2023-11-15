from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

Ui_PlotWidget, QWidget_Plot = uic.loadUiType("ui_plot_widget.ui")
Ui_ShowPlotWidget, QWidget_Show_Plot = uic.loadUiType("ui_show_plot_widget.ui")


class ShowPlotWidget(QWidget_Show_Plot, Ui_ShowPlotWidget):
    # e_field_changed = pyqtSignal()

    def __init__(self, parent = None):
        super(ShowPlotWidget, self).__init__(parent)
        self.setupUi(self)
        self.add_plot(plt.figure())

    def add_plot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.show_plot_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.show_plot_widget, coordinates=True)
        self.show_plot_layout.addWidget(self.toolbar)

    def remove_plot(self, ):
        self.show_plot_layout.removeWidget(self.canvas)
        plt.close(self.canvas.figure)
        self.canvas.close()
        self.show_plot_layout.removeWidget(self.toolbar)
        self.toolbar.close()


class CustomFigure():
    def __init__(self, figure, label):
        self.fig = figure
        self.label = label


class PlotWidget(QWidget_Plot, Ui_PlotWidget):
    # e_field_changed = pyqtSignal()

    def __init__(self, parent = None):
        super(PlotWidget, self).__init__(parent)
        self.setupUi(self)

        self.show_widget = ShowPlotWidget()

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

    def plot_figure(self):
        current_index = self.plot_list_view.currentIndex().row()
        if current_index:
            self.show_widget.remove_plot()
            self.show_widget.add_plot(self.figure_list[current_index].fig)
            self.show_widget.show()

    def update_plot_list(self):
        self.plot_list_item_model.clear()
        for custom_fig in self.figure_list:
            item = QtGui.QStandardItem(custom_fig.label)
            self.plot_list_item_model.appendRow(item)
        self.plot_list_view.setModel(self.plot_list_item_model)