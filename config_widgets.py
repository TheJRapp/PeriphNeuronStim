from PyQt5.uic import loadUiType
from PyQt5 import uic, QtGui, QtWidgets

Ui_PropertyWidget, QWidget = uic.loadUiType("ui_nerve_property_widget.ui")
Ui_StimulusWidget, QWidget_Stim = uic.loadUiType("ui_stimulus_widget.ui")

class windowTest(QWidget, Ui_PropertyWidget):
    def __init__(self, parent = None):
        super(windowTest, self).__init__(parent)
        self.setupUi(self)


class stimulusWidget(QWidget_Stim, Ui_StimulusWidget):
    def __init__(self, parent = None):
        super(stimulusWidget, self).__init__(parent)
        self.setupUi(self)

