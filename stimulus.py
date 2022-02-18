import numpy as np
# from neuron import h
import pandas as pd
import matplotlib.pyplot as plt
import pickle

h_replacement = 0.001 # ms

class Stimulus(object):

    def __init__(self, total_time, start_time, duration):
        super(Stimulus, self).__init__()

        self.total_time = total_time
        self.duration = duration
        self.start_pulse = start_time
        self.sine_f = 1/0.000500


def get_squarewave(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a square wave signal pulse.
    """
    first_pulse_duration = duration / 5

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    # 1 x square wave signal
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + first_pulse_duration) / h_replacement)] = pulse_amp
    # stim[int((self.start_pulse + first_pulse_duration) / h_replacement + 1): int(
    #     (self.start_pulse + self.duration) / h_replacement)] = - pulse_amp * first_pulse_duration / (
    #             self.duration - first_pulse_duration)

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse_amp

    return time_axis, stim, 'rect'


def get_inverted_squarewave(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted square wave signal pulse.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    # 1 x inverted square wave signal
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + first_pulse_duration) / h_replacement)] = - pulse_amp
    # stim[int((self.start_pulse + first_pulse_duration)/h_replacement +1) : int((self.start_pulse + self.duration) / h_replacement)] = pulse_amp * first_pulse_duration/(self.duration - first_pulse_duration)

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = - pulse_amp

    return time_axis, stim, 'inv_rect'


def get_real_squarewave(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a squarewave of length duration followed by an inverted squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    # 1 x inverted square wave signal
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + first_pulse_duration) / h_replacement)] = - pulse_amp
    # stim[int((self.start_pulse + first_pulse_duration)/h_replacement +1) : int((self.start_pulse + self.duration) / h_replacement)] = pulse_amp * first_pulse_duration/(self.duration - first_pulse_duration)

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse_amp

    stim[int((start_time + duration) / h_replacement): int((start_time + duration + 4 * duration) / h_replacement)] = (-0.25) * pulse_amp

    return time_axis, stim, 'real_rect'


def get_inverted_real_squarewave(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted squarewave of length duration followed by a squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    # 1 x inverted square wave signal
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + first_pulse_duration) / h_replacement)] = - pulse_amp
    # stim[int((self.start_pulse + first_pulse_duration)/h_replacement +1) : int((self.start_pulse + self.duration) / h_replacement)] = pulse_amp * first_pulse_duration/(self.duration - first_pulse_duration)

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = - pulse_amp

    stim[int((start_time + duration) / h_replacement): int((start_time + duration + 4 * duration) / h_replacement)] = 0.25 * pulse_amp
    return time_axis, stim, 'inv_real_rect'


def get_real_squarewave_mod_end(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a squarewave of length duration followed by an inverted squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    stim[int((start_time) / h_replacement): int((start_time + 4 * duration) / h_replacement)] = (-0.25) * pulse_amp
    stim[int((start_time + 4 * duration) / h_replacement): int((start_time + 5 * duration) / h_replacement)] = pulse_amp

    return time_axis, stim, 'real_rect_mod_end'


def get_inverted_real_squarewave_mod_end(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a squarewave of length duration followed by an inverted squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    stim[int((start_time) / h_replacement): int((start_time + 4 * duration) / h_replacement)] = (0.25) * pulse_amp
    stim[int((start_time + 4 * duration) / h_replacement): int((start_time + 5 * duration) / h_replacement)] = (-1) * pulse_amp

    return time_axis, stim, 'inv_real_rect_mod_end'


def get_real_squarewave_mod_centre(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a squarewave of length duration followed by an inverted squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    stim[int((start_time) / h_replacement): int((start_time + 2 * duration) / h_replacement)] = (-0.25) * pulse_amp
    stim[int((start_time + 2 * duration) / h_replacement): int((start_time + 3 * duration) / h_replacement)] = pulse_amp
    stim[int((start_time + 3 * duration) / h_replacement): int((start_time + 5 * duration) / h_replacement)] = (-0.25) * pulse_amp

    return time_axis, stim, 'real_rect_mod_centre'


def get_inverted_real_squarewave_mod_centre(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a squarewave of length duration followed by an inverted squarewave 4 times duration but only 1/4 amplitude.
    """

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    stim[int((start_time) / h_replacement): int((start_time + 2 * duration) / h_replacement)] = 0.25 * pulse_amp
    stim[int((start_time + 2 * duration) / h_replacement): int((start_time + 3 * duration) / h_replacement)] = (-1) * pulse_amp
    stim[int((start_time + 3 * duration) / h_replacement): int((start_time + 5 * duration) / h_replacement)] = 0.25 * pulse_amp

    return time_axis, stim, 'inv_real_rect_mod_centre'


def get_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a symmetric biphasic pulse. Sine shape
    """
    stim = np.zeros(int(total_time / h_replacement))
    #stim_time = np.arange(0, 1e3 / self.sine_f, h_replacement)
    stim_time = np.arange(0, duration, h_replacement)

    time_axis = np.arange(0, total_time, h_replacement)

    # 1 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp

    # 2 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp

    # 3 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp

    # 4 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp

    # 5 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 4e3 / sine_f) / h_replacement : (self.start_pulse + 5e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp

    # 6 x sin
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 4e3 / sine_f) / h_replacement : (self.start_pulse + 5e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # stim[(self.start_pulse + 5e3 / sine_f) / h_replacement : (self.start_pulse + 6e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp
    # Last = stim_time[len(stim_time) - 1]

    # # 1 x burst
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + 1e3 / self.sine_f) / h_replacement)] = np.sin(
    #    stim_time * (self.sine_f / 1e3) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    # 1 x burst
    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
       stim_time * (1/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    # 2 x burst
    # stim[int(self.start_pulse / h_replacement) : int((self.start_pulse + 1e3 / sine_f) / h_replacement)] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*stim_time/1e3)
    # stim[int((self.start_pulse + 2e3 / sine_f) / h_replacement) : int((self.start_pulse + 3e3 / sine_f) / h_replacement)] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 2* Last) /1e3)

    # 3 x burst
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*stim_time/1e3)
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 2* Last) /1e3)
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 3* Last) /1e3)

    # 4 x burst
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*stim_time/1e3)
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 2* Last) /1e3)
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 3* Last) /1e3)
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 4* Last) /1e3)

    # 5 x burst
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*stim_time/1e3)
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 2* Last) /1e3)
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 3* Last) /1e3)
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 4* Last) /1e3)
    # stim[(self.start_pulse + 4e3 / sine_f) / h_replacement : (self.start_pulse + 5e3 / sine_f) / h_replacement] = -np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*(stim_time + 5* Last) /1e3)

    # 6 x burst
    # stim[self.start_pulse / h_replacement : (self.start_pulse + 1e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210*stim_time/1e3)
    # stim[(self.start_pulse + 1e3 / sine_f) / h_replacement : (self.start_pulse + 2e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210* (stim_time + Last) /1e3)
    # stim[(self.start_pulse + 2e3 / sine_f) / h_replacement : (self.start_pulse + 3e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210* (stim_time + 2* Last) /1e3)
    # stim[(self.start_pulse + 3e3 / sine_f) / h_replacement : (self.start_pulse + 4e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210* (stim_time + 3* Last) /1e3)
    # stim[(self.start_pulse + 4e3 / sine_f) / h_replacement : (self.start_pulse + 5e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210* (stim_time + 4* Last) /1e3)
    # stim[(self.start_pulse + 5e3 / sine_f) / h_replacement : (self.start_pulse + 6e3 / sine_f) / h_replacement] = np.sin(stim_time * sine_f / 1e3 * 2 * np.pi) * pulse_amp* np.exp(-1210* (stim_time + 5* Last) /1e3)

    # 1 x inverted burst
    # stim[int(self.start_pulse / h_replacement): int((self.start_pulse + 1e3 / self.sine_f) / h_replacement)] = np.sin(
    #     stim_time * (self.sine_f / 1e3) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'sine'


def get_inverted_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a symmetric inverted biphasic pulse. Sine shaped.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
        stim_time * (1/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_sine'


def get_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a cosine pulse.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (1/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'cosine'


def get_inverted_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted cosine pulse.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (1/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_cosine'


def get_half_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns half a cosine pulse.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (0.5/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'half_cosine'


def get_inverted_half_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted half cosine pulse.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (0.5/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_half_cosine'


def get_polyphasic_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns two symmetric inverted biphasic pulse. Sine shaped.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
        stim_time * (2/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'polyphasic_sine'


def get_inverted_polyphasic_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns two symmetric inverted biphasic pulse. Sine shaped.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
        stim_time * (2/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_polyphasic_sine'


def get_polyphasic_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns two cosine pulses. Sine shaped.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (2/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'polyphasic_cosine'


def get_inverted_polyphasic_cosine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns two symmetric inverted biphasic pulse. Sine shaped.
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.cos(
        stim_time * (2/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_polyphasic_cosine'



def get_monophasic_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a symmetric monophasic pulse (half sine).
    """
    stim = np.zeros(int(total_time / h_replacement))
    #stim_time = np.arange(0, 1e3 / self.sine_f, h_replacement)
    stim_time = np.arange(0, duration, h_replacement)

    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
       stim_time * (0.5/duration) * 2 * np.pi) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'monophasic_sine'


def get_inverted_monophasic_sine(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a symmetric inverted monophasic pulse (half sine).
    """
    stim = np.zeros(int(total_time / h_replacement))
    # stim_time = np.arange(0, self.duration, h_replacement)
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, duration, len(interval))

    # 1 x inverted burst
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
        stim_time * (0.5/duration) * 2 * np.pi) * (-1) * pulse_amp  # * np.exp(-1210 * stim_time / 1e3)

    return time_axis, stim, 'inv_monophasic_sine'


def get_triangle(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a triangle pulse with increasing edge.
    """
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, 1, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = stim_time * pulse_amp

    return time_axis, stim, 'triangle'


def get_decreasing_triangle(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a triangle pulse which is 1 in the beginning and a increasing edge.
    """
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(1, 0, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = stim_time * pulse_amp

    return time_axis, stim, 'decreasing_triangle'


def get_inverted_triangle(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted triangle pulse with decresing edge (from 0 to -1).
    """
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(0, 1, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = (-1) * stim_time * pulse_amp

    return time_axis, stim, 'inv_triangle'


def get_inverted_decreasing_triangle(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted triangle pulse which is -1 in the beginning and an increasing edge (from -1 to 0).
    """
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time = np.linspace(1, 0, len(interval))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = (-1) * stim_time * pulse_amp

    return time_axis, stim, 'inv_decreasing_triangle'


def get_biphasic_descender(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns a square wave signal pulse followed by a flank and again followed by an inverted square.
    The pulse_amp denotes the amplitude of the first phase of the pulse.
    """
    half_pulse_duration = duration/2 + (1/4) * flank_time
    square_time = round((half_pulse_duration - (1/2) * flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time + square_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)]
    flank = np.linspace(1, -1, len(interval))

    stim[int(start_time / h_replacement): int((start_time + square_time) / h_replacement)] = 1 * pulse_amp
    stim[int((start_time + square_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)] = flank * pulse_amp
    stim[int((start_time + flank_time + square_time) / h_replacement): int(
        (start_time + flank_time + 2 * square_time) / h_replacement)] = -1 * pulse_amp

    return time_axis, stim, 'biphasic_descender'


def get_inverted_biphasic_descender(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns an inverted square wave signal pulse followed by a flank and again followed by a square.
    The pulse_amp denotes the amplitude of the first phase of the pulse.
    """
    half_pulse_duration = duration/2 + (1/4) * flank_time
    square_time = round((half_pulse_duration - (1/2) * flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time + square_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)]
    flank = np.linspace(1, -1, len(interval))

    stim[int(start_time / h_replacement): int((start_time + square_time) / h_replacement)] = -1 * pulse_amp
    stim[int((start_time + square_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)] = (-1) * flank * pulse_amp
    stim[int((start_time + flank_time + square_time) / h_replacement): int(
        (start_time + flank_time + 2 * square_time) / h_replacement)] = 1 * pulse_amp

    return time_axis, stim, 'inv_biphasic_descender'


def get_monophasic_descender(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns a positive square wave pulse followed by a falling flank.
    """
    duration = duration + (1/2) * flank_time
    square_time = round((duration - flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time + square_time) / h_replacement): int(
        (start_time + square_time + flank_time) / h_replacement)]
    stim_time = np.linspace(1, 0, len(interval))

    stim[int(start_time / h_replacement): int((start_time + square_time) / h_replacement)] = 1 * pulse_amp
    stim[int((start_time + square_time) / h_replacement): int(
        (start_time + square_time + flank_time) / h_replacement)] = stim_time * pulse_amp

    return time_axis, stim, 'monophasic_descender'


def get_inverted_monophasic_descender(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns an inverted square followed by a rising flank (-1 to 0)
    """
    duration = duration + (1/2) * flank_time
    square_time = round((duration - flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time + square_time) / h_replacement): int(
        (start_time + square_time + flank_time) / h_replacement)]
    stim_time = np.linspace(1, 0, len(interval))

    stim[int(start_time / h_replacement): int((start_time + square_time) / h_replacement)] = -1 * pulse_amp
    stim[int((start_time + square_time) / h_replacement): int(
        (start_time + square_time + flank_time) / h_replacement)] = (-1) * stim_time * pulse_amp

    return time_axis, stim, 'inv_monophasic_descender'


def get_monophasic_increaser(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns a rising flank followed by a positve square pulse.
    """
    duration = duration + (1/2) * flank_time
    square_time = round((duration - flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time) / h_replacement): int((start_time + flank_time) / h_replacement)]
    stim_time = np.linspace(0, 1, len(interval))

    stim[int((start_time) / h_replacement): int(
        (start_time + flank_time) / h_replacement)] = stim_time * pulse_amp
    stim[int((start_time + flank_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)] = 1 * pulse_amp

    return time_axis, stim, 'monophasic_increaser'


def get_inverted_monophasic_increaser(total_time, start_time, duration, flank_time, pulse_amp=1):
    """
    Returns a falling flank (0 to -1) followed by a negative square pulse.
    """
    duration = duration + (1/2) * flank_time
    square_time = round((duration - flank_time), 4)

    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)

    interval = stim[int((start_time) / h_replacement): int((start_time + flank_time) / h_replacement)]
    stim_time = np.linspace(0, 1, len(interval))

    stim[int((start_time) / h_replacement): int(
        (start_time + flank_time) / h_replacement)] = stim_time * pulse_amp * (-1)
    stim[int((start_time + flank_time) / h_replacement): int(
        (start_time + flank_time + square_time) / h_replacement)] = -1 * pulse_amp

    return time_axis, stim, 'inv_monophasic_increaser'


def get_real_monophasic(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a monophasic pulse which decreases exponentially.
    """
    stim = np.zeros(int(total_time / h_replacement))
    #stim_time = np.arange(0, 1e3 / self.sine_f, h_replacement)

    time_axis = np.arange(0, total_time, h_replacement)

    interval_1 = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    stim_time_1 = np.linspace(0, duration, len(interval_1))
    interval_2 = stim[int((start_time + duration)/ h_replacement): int((start_time + 6*duration) / h_replacement)]
    stim_time_2 = np.linspace(-1, 6, len(interval_2))

    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = np.sin(
       stim_time_1 * (0.35/duration) * 2 * np.pi) * pulse_amp

    last_sine_element = np.sin(stim_time_1 * (0.35/duration) * 2 * np.pi)[-1]

    stim[int((start_time + duration)/ h_replacement): int((start_time + 6*duration) / h_replacement)] = (1/np.exp(
       stim_time_2) / np.amax(1/np.exp(stim_time_2))) * last_sine_element * pulse_amp

    stim_av = moving_average(stim, 4)
    L = 12e-6

    phi = [i * L for i in stim_av]
    emf = (-1) * np.diff(phi) / np.diff(time_axis)
    emf = np.asarray(moving_average(emf))
    stim = (emf / np.amax(abs(emf))) * pulse_amp

    return time_axis[1:], stim, 'real_monophasic'


def get_inverted_real_monophasic(total_time, start_time, duration, pulse_amp=1):
    """
    Returns an inverted monophasic pulse which decreases exponentially.
    """
    time_axis, stim, name = get_real_monophasic(total_time, start_time, duration, pulse_amp)
    stim = stim * (-1)

    return time_axis, stim, 'inv_real_monophasic'


def get_ideal_monophasic(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a monophasic pulse which decreases exponentially.
    """
    stim = np.zeros(int(total_time / h_replacement))
    #stim_time = np.arange(0, 1e3 / self.sine_f, h_replacement)

    time_axis = np.arange(0, total_time, h_replacement)

    interval_1 = stim[int(start_time / h_replacement): int((start_time + duration/6) / h_replacement)]
    stim_time_1 = np.linspace(0, duration, len(interval_1))
    interval_2 = stim[int((start_time + duration/6)/ h_replacement): int((start_time + duration) / h_replacement)]
    stim_time_2 = np.linspace(-1, 6, len(interval_2))

    stim[int(start_time / h_replacement): int((start_time + duration/6) / h_replacement)] = np.sin(
       stim_time_1 * (0.22/duration) * 2 * np.pi) * pulse_amp

    last_sine_element = np.sin(stim_time_1 * (0.22/duration) * 2 * np.pi)[-1]

    stim[int((start_time + duration/6)/ h_replacement): int((start_time + duration) / h_replacement)] = (1/np.exp(
       stim_time_2) / np.amax(1/np.exp(stim_time_2))) * last_sine_element * pulse_amp

    stim_av = moving_average(stim, 4)
    L = 12e-6

    phi = [i * L for i in stim_av]
    emf = (-1) * np.diff(phi) / np.diff(time_axis)
    emf = np.asarray(moving_average(emf))
    stim = (emf / np.amax(abs(emf))) * pulse_amp

    return time_axis[1:], stim, 'ideal_monophasic'


def get_inverted_ideal_monophasic(total_time, start_time, duration, pulse_amp=1):
    """
    Returns a monophasic pulse which decreases exponentially.
    """
    time_axis, stim, name = get_ideal_monophasic(total_time, start_time, duration, pulse_amp)
    stim = stim * (-1)

    return time_axis, stim, 'inv_ideal_monophasic'


def get_custom_spice_1100V_22u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_22u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * pulse_amp

    return time_axis, stim, 'custom_spice_1100V_22u'


def get_inverted_custom_spice_1100V_22u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_22u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * (-1) * pulse_amp

    return time_axis, stim, 'inv_custom_spice_1100V_22u'


def get_custom_spice_400V_100u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_400V_100u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * pulse_amp

    return time_axis, stim, 'custom_spice_400V_100u'


def get_inverted_custom_spice_400V_100u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_400V_100u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * (-1) * pulse_amp

    return time_axis, stim, 'inv_custom_spice_400V_100u'


def get_custom_spice_1100V_12u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_12u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * pulse_amp

    return time_axis, stim, 'custom_spice_1100V_12u'


def get_inverted_custom_spice_1100V_12u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_12u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * (-1) * pulse_amp

    return time_axis, stim, 'inv_custom_spice_1100V_12u'


def get_custom_spice_1100V_66u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_66u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * pulse_amp

    return time_axis, stim, 'custom_spice_1100V_66u'


def get_inverted_custom_spice_1100V_66u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_1100V_66u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * (-1)  * pulse_amp

    return time_axis, stim, 'inv_custom_spice_1100V_66u'


def get_custom_spice_2200V_66u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_2200V_66u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * pulse_amp

    return time_axis, stim, 'custom_spice_2200V_66u'


def get_inverted_custom_spice_2200V_66u(total_time, start_time, duration, pulse_amp=1):
    """
    Returns electric field pulse according to current simulated in LTSPice.
    """

    stim = np.zeros(int(total_time / h_replacement))

    time_axis = np.arange(0, total_time, h_replacement)

    df = pd.read_csv('D:/Files/Doktorarbeit/NEURON_Axon_Evaluation/Custom_Stimuli/20210222_LTSpicsStimulus_2200V_66u.csv', index_col=0)
    shape = np.asarray(df.values.tolist())
    pulse_indices = stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)]
    indexes = np.round(np.linspace(0, len(shape) - 1, len(pulse_indices))).astype(int)
    pulse = shape[indexes.tolist()] / np.amax(abs(shape))
    stim[int(start_time / h_replacement): int((start_time + duration) / h_replacement)] = pulse.transpose() * (-1) * pulse_amp

    return time_axis, stim, 'inv_custom_spice_2200V_66u'

def get_stefan_simulation(total_time, start_time, duration, pulse_amp=1):
    # the pulse has a fixed length, the duration is not considered
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)
    with open('D:/Files/Doktorarbeit/stefans_pulse/Python_Calculations/stimulus_stefan', 'rb') as e:
        data = pickle.load(e)

    pulse_indices = stim[int(start_time / h_replacement): int((start_time + data['simulation_duration']) / h_replacement)]
    indexes = np.round(np.linspace(0, len(data['simulation_data']) - 1, len(pulse_indices))).astype(int)
    pulse = data['simulation_data'][indexes.tolist()]

    stim[int(start_time / h_replacement): int((start_time + data['simulation_duration']) / h_replacement)] = pulse.transpose()

    return time_axis, stim, 'stefan_simulation'

def get_stefan_sissy(total_time, start_time, duration, pulse_amp=1):
    # the pulse has a fixed length, the duration is not considered
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)
    with open('D:/Files/Doktorarbeit/stefans_pulse/Python_Calculations/stimulus_stefan', 'rb') as e:
        data = pickle.load(e)

    pulse_indices = stim[int(start_time / h_replacement): int((start_time + data['sissy_duration']) / h_replacement)]
    indexes = np.round(np.linspace(0, len(data['sissy_data']) - 1, len(pulse_indices))).astype(int)
    pulse = data['sissy_data'][indexes.tolist()]

    stim[int(start_time / h_replacement): int((start_time + data['sissy_duration']) / h_replacement)] = pulse.transpose()

    return time_axis, stim, 'sissy_simulation'

def get_stefan_messung_11(total_time, start_time, duration, pulse_amp=1):
    # the pulse has a fixed length, the duration is not considered
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)
    with open('D:/Files/Doktorarbeit/stefans_pulse/Python_Calculations/stimulus_stefan', 'rb') as e:
        data = pickle.load(e)

    pulse_indices = stim[int(start_time / h_replacement): int((start_time + data['messung_11_duration']) / h_replacement)]
    indexes = np.round(np.linspace(0, len(data['messung_11_data']) - 1, len(pulse_indices))).astype(int)
    pulse = data['messung_11_data'][indexes.tolist()]

    stim[int(start_time / h_replacement): int((start_time + data['messung_11_duration']) / h_replacement)] = pulse.transpose()

    return time_axis, stim, 'stefan_messung_11'

def get_stefan_messung_13(total_time, start_time, duration, pulse_amp=1):
    # the pulse has a fixed length, the duration is not considered
    stim = np.zeros(int(total_time / h_replacement))
    time_axis = np.arange(0, total_time, h_replacement)
    with open('D:/Files/Doktorarbeit/stefans_pulse/Python_Calculations/stimulus_stefan', 'rb') as e:
        data = pickle.load(e)

    pulse_indices = stim[int(start_time / h_replacement): int((start_time + data['messung_13_duration']) / h_replacement)]
    indexes = np.round(np.linspace(0, len(data['messung_13_data']) - 1, len(pulse_indices))).astype(int)
    pulse = data['messung_13_data'][indexes.tolist()]

    stim[int(start_time / h_replacement): int((start_time + data['messung_13_duration']) / h_replacement)] = pulse.transpose()

    return time_axis, stim, 'stefan_messung_13'

def moving_average(curve, window=4):
    curve_averaged = []
    for i in range(len(curve)):
        if i < window:
            curve_averaged.append(curve[i:i + window].sum() / curve[i:i + window].size)
        elif (i + window) > len(curve):
            curve_averaged.append(curve[i - window:i].sum() / curve[i - window:i].size)
        else:
            av = curve[i - window:i + window].sum() / curve[i - window:i + window].size
            curve_averaged.append(av)

    return curve_averaged


def get_list_of_selected_stimuli(total_time, start_time, duration, flank_percentage=10, pulse_amp=1):
    stimulus_dict = {}
    time_axis, stimulus_th, name = get_real_monophasic(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_half_cosine(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_cosine(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_polyphasic_cosine(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_real_squarewave(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_real_squarewave_mod_end(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th
    time_axis, stimulus_th, name = get_real_squarewave_mod_centre(total_time, start_time, duration, 1)
    stimulus_dict[name] = stimulus_th

    return time_axis, stimulus_dict


def stimulus_string_list():
    stim_list = [
        'half_cosine',
        'cosine',
        'double_cosine',
        'half_sine',
        'sine',
        'double_sine',
        'ideal_rect',
        'real_rect_a',
        'real_rect_b',
        'real_rect_c',
        'triangle',
        'decreasing_triangle',
        'stefan_simulation',
        'stefan_sissy',
        'stefan_messung_11',
        'stefan_messung_13'
    ]
    return stim_list


def get_stim_from_string(stim_name, total_time, start_time, duration):
    if stim_name == 'half_cosine':
        return get_half_cosine(total_time, start_time, duration)
    if stim_name == 'cosine':
        return get_cosine(total_time, start_time, duration)
    if stim_name == 'double_cosine':
        return get_polyphasic_cosine(total_time, start_time, duration)
    if stim_name == 'half_sine':
        return get_monophasic_sine(total_time, start_time, duration)
    if stim_name == 'sine':
        return get_sine(total_time, start_time, duration)
    if stim_name == 'double_sine':
        return get_polyphasic_sine(total_time, start_time, duration)
    if stim_name == 'ideal_rect':
        return get_squarewave(total_time, start_time, duration)
    if stim_name == 'real_rect_a':
        return get_real_squarewave(total_time, start_time, duration)
    if stim_name == 'real_rect_b':
        return get_real_squarewave_mod_end(total_time, start_time, duration)
    if stim_name == 'real_rect_c':
        return  get_real_squarewave_mod_centre(total_time, start_time, duration)
    if stim_name == 'triangle':
        return get_triangle(total_time, start_time, duration)
    if stim_name == 'decreasing_triangle':
        return get_decreasing_triangle(total_time, start_time, duration)
    if stim_name == 'stefan_simulation':
        return get_stefan_simulation(total_time, start_time, duration)
    if stim_name == 'stefan_sissy':
        return get_stefan_sissy(total_time, start_time, duration)
    if stim_name == 'stefan_messung_11':
        return get_stefan_messung_11(total_time, start_time, duration)
    if stim_name == 'stefan_messung_13':
        return get_stefan_messung_13(total_time, start_time, duration)