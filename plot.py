'''
@author: Rapp & Braun
'''

import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import matplotlib.pyplot as plt
from neuron import h
from Axon_Models import mrg_axon, hh_axon, simple_axon
from matplotlib.ticker import FormatStrFormatter
import cv2


def plot_traces(name, trace_list, time_axis, stimulus, trace_height=100):
    trace_list = np.array(trace_list)
    # MAX_V = np.ones(30)*1000
    axes = plt.figure().add_axes([0.125, 0.125, 0.75, 0.8])
    # b=0

    for plt_it, voltage_trace in enumerate(trace_list):
        stimulus_trace = stimulus is not None
        y_lim = trace_height * (len(trace_list) + 5 * int(stimulus_trace))
        if stimulus_trace:
            y_step = trace_height * (plt_it + 5)
        else:
            y_step = trace_height * (plt_it + 1)
        plt.plot(time_axis, [y_lim - y_step for j in time_axis], 'k--', alpha=0.5, linewidth=1)
        line = plt.plot(time_axis, voltage_trace[:len(time_axis)] + y_lim - y_step, '-b')
        # MAX_V[b] = max(voltage_trace[:len(time_axis)])
        # b=b+1

    if stimulus is not None:
        zipped = np.array(list(zip(time_axis, stimulus)))
        x = zipped[:, 0]
        y = zipped[:, 1]
        plt.plot(x, y / max(abs(y)) * 100 + y_lim - 2 * trace_height)

        plt.yticks([y_lim - 2 * trace_height], ['Stimulus'], fontsize=12)

    else:
        if len(trace_list) > 1:
            plt.yticks('')
        else:
            plt.ylabel('Membrane Potential ($mV$)')

    if len(trace_list) > 1:
        middle_y = (axes.get_ylim()[1] - axes.get_ylim()[0]) / 2.
        slightly_left = (axes.get_xlim()[1] - axes.get_xlim()[0]) * 0.05 * -1
        plt.text(slightly_left, middle_y, 'Membrane Potential along Cell', rotation=90, ha='center', va='center')
    # print min(MAX_V)
    # ===============================================================================
    # scalebar
    # ===============================================================================
    x_loc = plt.gca().get_xlim()[1] * 0.85
    y_loc = y_lim - 5 * trace_height + 35
    plt.plot([x_loc, x_loc], [y_loc, y_loc + 100], 'k-_', linewidth=1)
    plt.text(x_loc, y_loc + 50, '  100 mV', ha='left', va='center', fontsize=12)
    plt.title(name)
    plt.xlabel('Time ($ms$)')
    # plt.xlim(0, max(time_axis))
    # plt.ylim(-50, y_lim)

    return axes


def plot_traces_and_field(name, time_axis, stimulus, model, trace_height=100):
    trace_list = np.array(model.potential_vector_node_list)
    # MAX_V = np.ones(30)*1000
    fig = plt.figure()
    axes2 = fig.add_axes([0.85, 0.125, 0.09, 0.8])
    axes = fig.add_axes([0.125, 0.125, 0.65, 0.8])
    # b=0

    e_field = []
    for sec, e_field_value in zip(model.sections, model.e_field_along_axon):
        if type(sec) == mrg_axon.Node or type(sec) == simple_axon.Node or type(sec) == hh_axon.Node:
            e_field.append(e_field_value)

    # axes2.plot(e_field[0::10], range(10*len(e_field))[-1::-100], 'g')
    axes2.plot(e_field, range(100 * len(e_field))[-1::-100], 'darkgray')
    # plt.tight_layout()

    n = 5
    for plt_it, voltage_trace in enumerate(trace_list[::n]):
        stimulus_trace = stimulus is not None
        y_lim = trace_height * (len(trace_list) + 5 * int(stimulus_trace))
        if stimulus_trace:
            y_step = trace_height * (n*plt_it + 5)
        else:
            y_step = trace_height * (n*plt_it + 1)
        axes.plot(time_axis, [y_lim - y_step for j in time_axis], 'k--', alpha=0.5, linewidth=1)
        line = axes.plot(time_axis, voltage_trace[:len(time_axis)] + y_lim - y_step)
        axes2.plot(time_axis, [y_lim - y_step for j in time_axis], 'w', alpha=0.5, linewidth=1)
        line2 = axes2.plot(e_field[n*plt_it], y_lim - y_step, '-x')
        # line2 = axes2.plot(e_field[plt_it], y_lim - y_step, '-x')
        # MAX_V[b] = max(voltage_trace[:len(time_axis)])
        # b=b+1

    if stimulus is not None:
        zipped = np.array(list(zip(time_axis, stimulus)))
        x = zipped[:, 0]
        y = zipped[:, 1]

        axes.plot(x, y / max(abs(y)) * 100 + y_lim - 2 * trace_height)
        axes2.plot(x, y / max(abs(y)) * 100 + y_lim - 2 * trace_height, 'w')

        axes.set_xticks([y_lim - 2 * trace_height])
        axes.set_xticklabels(['Stimulus'])

    else:
        if len(trace_list) > 1:
            axes.set_yticks('')
        else:
            axes.set_ylabel('Membrane Potential ($mV$)')

    if len(trace_list) > 1:
        middle_y = (axes.get_ylim()[1] - axes.get_ylim()[0]) / 2.
        slightly_left = (axes.get_xlim()[1] - axes.get_xlim()[0]) * 0.05 * -1.5
        axes.text(slightly_left, middle_y, 'Membrane Potential along Cell', rotation=90, ha='center', va='center')
    # print min(MAX_V)
    # a = np.arange(trace_list.shape[0], 0, n)
    #  axes.set_yticks(np.arange(trace_list.shape[0], 0, -1))

    # ticks = axes.get_yticks()
    # axes.set_yticklabels(round(ticks / plt_it))
    # axes.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    # ===============================================================================
    # scalebar
    # ===============================================================================
    x_loc = plt.gca().get_xlim()[1] * 0.85
    y_loc = y_lim - 5 * trace_height + 35
    axes.plot([x_loc, x_loc], [y_loc, y_loc + 100], 'k-_', linewidth=1)
    axes.text(x_loc, y_loc + 50, '  100 mV', ha='left', va='center', fontsize=12)
    axes2.plot([x_loc, x_loc], [y_loc, y_loc + 100], 'w', linewidth=1)
    # axes2.text(x_loc, y_loc + 50, '  100 mV', ha='left', va='center', fontsize=12)
    axes.set_title(name)
    axes2.set_title('E-Field')
    plt.xlabel('Time ($ms$)')
    plt.xlim(0, max(time_axis))
    plt.ylim(-50, y_lim)
    axes.yaxis.set_visible(False)
    axes2.yaxis.set_visible(False)

    # e_field = []
    # for sec, e_field_value in zip(model.sections, model.e_field_list):
    #     if type(sec) == mrg_axon.Node or type(sec) == simple_axon.Node or type(sec) == hh_axon.Node:
    #         e_field.append(e_field_value)
    #
    # axes2 = fig.add_axes([0.90, 0.125, 0.09, 0.7])
    # axes2.plot(e_field[0::10], range(10*len(e_field))[0::100], '-x')
    # plt.tight_layout()

    return axes, axes2


def plot_e_field_along_nerve(e_field_along_nerve):
    fig = plt.Figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(e_field_along_nerve)
    ax1.set_xlabel('Compartments')
    ax1.set_ylabel('E-field in V/m')
    return fig


def plot_potential_along_nerve(potential_along_nerve):
    fig = plt.Figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(potential_along_nerve)
    ax1.set_xlabel('Compartments')
    ax1.set_ylabel('Potential in V')
    return fig


def plot_axon_xy_coordinates(axon):
    fig = plt.Figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(axon.x, axon.y)
    ax1.set_xlabel('x in µm')
    ax1.set_ylabel('y in µm')
    return fig


def plot_axon_xy_coordinates_with_nodes(axon, internode_segments):
    # This works only for MHH model, whith nseg_internode=x and nseg_node=1
    fig = plt.Figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(axon.x, axon.y)
    ax1.plot(axon.x[::internode_segments], axon.y[::internode_segments], 'x')
    ax1.set_xlabel('x in µm')
    ax1.set_ylabel('y in µm')
    return fig


def plot_axon_nerve_shape_xy_coordinates(axon, nerve_shape):
    fig = plt.Figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(axon.x, axon.y, label='Axon')
    ax1.plot(nerve_shape.x, nerve_shape.y, label='Nerve shape')
    ax1.set_xlabel('x in µm')
    ax1.set_ylabel('y in µm')
    ax1.legend()
    return fig


def plot_2d_field_with_cable(e_field, layer, nerve, scale):
    e_modified = e_field.e_y[:,:,layer].copy()
    xdim = round(len(e_field.x)/2)
    ydim = round(len(e_field.y) / 2)

    xrange = nerve.length * np.cos(nerve.angle / 360 * 2 * np.pi)
    yrange = nerve.length * np.sin(nerve.angle / 360 * 2 * np.pi)
    test_1 = nerve.y[0]/scale
    test_2 = abs(e_field.y[1] - e_field.y[0])
    test_3 = int((nerve.y[0] / scale + ydim) / abs(e_field.y[1] - e_field.y[0]))
    img_mod = cv2.line(e_modified, (int(nerve.x[0]/scale + xdim), int( (nerve.y[0]/scale + ydim) / abs(e_field.y[1]/scale - e_field.y[0]/scale) )), (int(nerve.x[0]/scale + xdim +
                      xrange/scale), int(nerve.y[0]/scale + ydim + yrange/scale)), (255, 0, 0), 5)

    fig1 = plt.Figure()
    # cv2.imshow("Line", img_mod)
    ax1f1 = fig1.add_subplot(111)
    ax1f1.imshow(e_modified, extent=[min(e_field.y)/scale, max(e_field.y)/scale, max(e_field.x)/scale, min(e_field.x)/scale])
    return fig1