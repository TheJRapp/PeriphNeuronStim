from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

Ui_ThresholdWidget, QWidget_Threshold = uic.loadUiType("ui_threshold_widget.ui")

import sys
sys.path.insert(0, "C:/nrn/lib/python")
import numpy as np
from neuron import h
import copy
import misc_functions as mf


class ThresholdWidget(QWidget_Threshold, Ui_ThresholdWidget):

    def __init__(self, parent = None):
        super(ThresholdWidget, self).__init__(parent)

        self.setupUi(self)
        self.ap_threshold = self.ap_threshold_spin_box.value()
        self.start_amp = self.start_amp_spin_box.value()
        self.rough_step_size = self.steps_rough_spin_box.value()
        self.fine_step_size = self.steps_fine_spin_box.value()
        self.precission_step_size = self.steps_precission_spin_box.value()
        self.time_interval_start = self.time_interval_min_spin_box.value()
        self.time_interval_stop = self.time_interval_max_spin_box.value()

        self.ap_threshold_spin_box.valueChanged.connect(self.set_ap_threshold)
        self.start_amp_spin_box.valueChanged.connect(self.set_start_amp)
        self.steps_rough_spin_box.valueChanged.connect(self.set_rough_step_size)
        self.steps_fine_spin_box.valueChanged.connect(self.set_fine_step_size)
        self.steps_precission_spin_box.valueChanged.connect(self.set_precission_step_size)
        self.time_interval_min_spin_box.valueChanged.connect(self.set_min_time)
        self.time_interval_max_spin_box.valueChanged.connect(self.set_max_time)

    def set_ap_threshold(self):
        self.ap_threshold = self.ap_threshold_spin_box.value()

    def set_start_amp(self):
        self.start_amp = self.start_amp_spin_box.value()

    def set_rough_step_size(self):
        self.rough_step_size = self.steps_rough_spin_box.value()

    def set_fine_step_size(self):
        self.fine_step_size = self.steps_fine_spin_box.value()

    def set_precission_step_size(self):
        self.precission_step_size = self.steps_precission_spin_box.value()

    def set_min_time(self):
        self.time_interval_start = self.time_interval_min_spin_box.vlaue()

    def set_max_time(self):
        self.time_interval_stop = self.time_interval_max_spin_box.vlaue()

    def rough_to_fine_search(self, axon_model, total_time, time_axis, stimulus):
        axon_model_internal = copy.copy(axon_model)
        # axon_model MUST INCLUDE quasi_pot_list
        start_amp = self.start_amp
        event = 2  # 1 = propagation in one direction, 2 = propagation in both directions,

        # rough search
        event_result, pulse_amp = self.find_threshold(axon_model_internal, start_amp, self.rough_step_size, total_time,
                                                      time_axis, stimulus, event)
        pulse_amp = pulse_amp - self.rough_step_size
        # search start amp
        while event_result == 2:
            start_amp = start_amp / 2
            event_result, new_start_amp = self.find_threshold(axon_model_internal, start_amp, self.rough_step_size,
                                                          total_time, time_axis, stimulus, event=0)
            pulse_amp = new_start_amp
        if event_result == 3:
            return 0

        # finer search
        event, pulse_amp = self.find_threshold(axon_model_internal, pulse_amp,
                                               self.fine_step_size, total_time, time_axis, stimulus, event)

        # even finer search
        event, pulse_amp = self.find_threshold(axon_model_internal, pulse_amp - self.fine_step_size,
                                               self.precission_step_size, total_time, time_axis, stimulus, event)

        return pulse_amp

    def find_threshold(self, axon_model, start_amp, step, total_time, time_axis, stimulus, event):
        pulse_amp = start_amp
        first = True
        count = 0
        while 1:
            del axon_model.potential_vector_list

            mf.record_membrane_potentials(axon_model, 0.5)

            axon_model.stim_matrix = [pulse_amp * element * stimulus for element in axon_model.potential_along_axon]
            mf.play_stimulus_matrix(axon_model, time_axis)

            h.finitialize(-80)
            h.continuerun(total_time)

            this_event = self.event_detector(axon_model.potential_vector_list)

            if first:
                if this_event != 0:
                    return 2, pulse_amp
            first = False

            if this_event == event:
                return event, pulse_amp
            pulse_amp += step
            count += 1
            print('Pulse amp: ', pulse_amp)
            if count > 50:
                return 3, 0

    def event_detector(self, potential_vector_list):
        if np.amax(potential_vector_list) < self.ap_threshold:
            return 0  # nothing at all detected

        if np.amax(potential_vector_list) >= self.ap_threshold:
            if xor(max(potential_vector_list[0]) >= self.ap_threshold, max(potential_vector_list[-1]) >= self.ap_threshold):
                return 1  # propagation in one direction
            if max(potential_vector_list[0]) >= self.ap_threshold and max(potential_vector_list[-1]) >= self.ap_threshold:
                return 2  # propagation in both directions
        else:
            print('Problem occured')
            return 3  # something is not ok


    def find_threshold_bisection(self, axon_model, interval_max, interval_min, precission, total_time, e_field, r_interpol,
                                 time_axis, stimulus):
        axon_model_internal = copy.copy(axon_model)
        stim_matrix, e_field_list, quasi_pot_list = mf.quasi_potentials(stimulus, e_field, axon_model_internal,
                                                                        r_interpol)

        self.run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, interval_max)
        if np.amax(axon_model_internal.potential_vector_list) < 30:
            print("Interval Max too low")
            return

        self.run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, interval_min)
        if np.amax(axon_model_internal.potential_vector_list) >= 30:
            print("Interval Min too high")
            return

        # now the threshold should be within interval boarders
        # bisection starts
        while interval_max - interval_min > precission:
            self.run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time,
                                                 interval_max - (interval_max - interval_min) / 2)
            # if np.amax(axon_model_internal.potential_vector_list) < 30:
            if max(axon_model_internal.potential_vector_list[0]) < 30 or max(
                    axon_model_internal.potential_vector_list[-1]) < 30:
                interval_min = interval_min + (interval_max - interval_min) / 2
            # elif np.amax(axon_model_internal.potential_vector_list) >= 30:
            elif max(axon_model_internal.potential_vector_list[0]) >= 30 and max(
                    axon_model_internal.potential_vector_list[-1]) >= 30:
                interval_max = interval_max - (interval_max - interval_min) / 2

        puls_amp_final = interval_max - (interval_max - interval_min) / 2
        print(max(axon_model_internal.potential_vector_list[100]))
        print('Action potential achieved at pulse_amp=', interval_max - (interval_max - interval_min) / 2)

        return puls_amp_final

    def run_simulation_with_actual_pulse_amp(self, axon_model_internal, stim_matrix, time_axis, total_time, pulse_amp):
        del axon_model_internal.potential_vector_list

        mf.record_membrane_potentials(axon_model_internal, 0.5)

        axon_model_internal.stim_matrix = [element * pulse_amp for element in stim_matrix]
        mf.play_stimulus_matrix(axon_model_internal, time_axis)

        h.finitialize(-80)
        h.continuerun(total_time)
        print(pulse_amp)
        print(max(axon_model_internal.potential_vector_list[0]))
        print(max(axon_model_internal.potential_vector_list[-1]))

    def find_threshold_with_mdf(model, trigger_mdf, stimulus, pulse_amp, step):
        while model.mdf < trigger_mdf:
            pulse_amp += step
            mdf_new = mf.driving_function(model, pulse_amp * stimulus)
        return pulse_amp

def xor(x, y):
    return bool((x and not y) or (not x and y))