from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib import pyplot as plt

Ui_StimulusWidget, QWidget_Stim = uic.loadUiType("ui_stimulus_widget.ui")

import stimulus as stim

class stimulusWidget(QWidget_Stim, Ui_StimulusWidget):
    stimulus_changed = pyqtSignal()
    def __init__(self, parent = None):
        super(stimulusWidget, self).__init__(parent)
        self.setupUi(self)

        self.stim_combo_box.addItems(stim.stimulus_string_list())

        self.update_stimulus()

        self.stim_combo_box.currentTextChanged.connect(self.update_stimulus)
        self.total_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.start_time_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_intensity_spin_box.valueChanged.connect(self.update_stimulus)
        self.stimulus_duration_spin_box.valueChanged.connect(self.update_stimulus)

    def update_stimulus(self):
        if hasattr(self, 'stim_canvas'):
            self.stimulus_layout.removeWidget(self.stim_canvas)
            self.stim_canvas.close()
        self.time_axis, self.stimulus, self.stim_name = stim.get_stim_from_string(
            self.stim_combo_box.currentText(),
            self.total_time_spin_box.value(),
            self.start_time_spin_box.value(),
            self.stimulus_duration_spin_box.value())
        self.uni_stimulus = self.stimulus
        self.stimulus = self.stimulus * self.stimulus_intensity_spin_box.value()
        self.total_time = self.total_time_spin_box.value()
        figStim = Figure()
        ax1Stim = figStim.add_subplot(111)
        ax1Stim.plot(self.time_axis, self.stimulus)
        self.stim_canvas = FigureCanvas(figStim)
        self.stimulus_layout.addWidget(self.stim_canvas)
        self.stim_canvas.draw()

        self.stimulus_changed.emit()