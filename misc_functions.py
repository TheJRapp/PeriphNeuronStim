import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import neuron
from neuron import h
from Axon_Models import mrg_axon, hh_axon, simple_axon, mhh_model
import stimulus
import matplotlib.pyplot as plt
import copy
import time
import cv2

def play_stimulus_matrix(model, time_axis):
    """
    Plays the stimulus into each node.
    """
    segment_list = model.get_segments()
    time_vector = h.Vector()
    time_vector.from_python(time_axis)

    stimulus_vector_list = []
    for node_stimulus, segment in zip(model.stim_matrix, segment_list):
        stimulus_vector = h.Vector()
        stimulus_vector.from_python(np.array(node_stimulus, float))
        stimulus_vector.play(segment._ref_e_extracellular, time_vector)
        stimulus_vector_list.append(stimulus_vector)

    # save vectors from garbage collector
    model.stimulus_vector_list = stimulus_vector_list
    model.time_vector = time_vector


def homogeneous_medium(stimulus, model):
    """
    Stimulation in homogeneous medium with 300 Ohm cm.
    """
    radial_distance = np.sqrt(model.x ** 2 + model.y ** 2 + model.z ** 2)
    node_factors = 1 / (4 * np.pi * radial_distance) * 300e4

    # simulate electric field as superposition of potential field points (?)
    # 1. convert electric field to potential field
    # 2. calculate node factors for each segment - potential field connection
    stim_matrix = np.outer(node_factors, stimulus)

    # plt.imshow(stim_matrix, aspect='auto')
    # plt.colorbar()
    # plt.show()

    return stim_matrix


def record_membrane_potentials(model, location=None):
    '''
    Returns a list of Vector() objects which record the membrane potentials
    in each segment at the given locations. location = None records potentials in all segments.
    '''
    model.potential_vector_list = []
    model.potential_vector_node_list = []
    model.potential_vector_stin_list = []

    if location is None:
        for sec in model.sections:
            for seg in sec:
                v_vector = h.Vector()
                v_vector.record(seg._ref_v)
                model.potential_vector_list.append(v_vector)
                if type(sec) == mrg_axon.Node or type(sec) == mhh_model.Node or type(sec) == hh_axon.Node:
                    model.potential_vector_node_list.append(v_vector)
    else:
        for sec in model.sections:
            v_vector = h.Vector()
            v_vector.record(sec(location)._ref_v)
            model.potential_vector_list.append(v_vector)
            if type(sec) == mrg_axon.Node or type(sec) == mhh_model.Node or type(sec) == hh_axon.Node:
                model.potential_vector_node_list.append(v_vector)
    return model.potential_vector_list

def remove_from_simulation(model):
    for vector in model.potential_vector_list:
        vector.play_remove()
    for vector in model.potential_vector_node_list:
        vector.play_remove()
    for vector in model.stimulus_vector_list:
        vector.play_remove()
    model.time_vector.play_remove()


def quasi_potentials(stimulus, e_field, cable, interpolation_radius_index):
    # quasi potential described by Aberra 2019
    # for(each segment)
    #   find e_field coordinates within segment +- deltaX +- deltaY +- deltaZ
    #   e_field_current = interpolate e_field
    #   quasi_pot_current = quasi_pot_prev - (1/2)(e_field_current + e_field_previous) * displacement #calc displacement from model?
    #   generate h.vector with (stimulus and e_field as amplitude) and (time_vector)
    #   play generated vector on segment.e_extracellular

    stim_matrix = []  # contains a row for each segment where the corresponding e-field is multiplied w. stimulus
    e_field_along_axon = []
    quasi_pot_along_axon = []

    r = interpolation_radius_index  # interpolation radius

    cable_x_min = round(min(cable.x))
    cable_x_max = round(max(cable.x))
    cable_y_min = round(min(cable.y))
    cable_y_max = round(max(cable.y))
    cable_z_min = round(min(cable.z))
    cable_z_max = round(max(cable.z))

    x_axis = e_field.x  # indexes of e_field, e.g. -200,...,0,...200
    y_axis = e_field.y
    z_axis = e_field.z

    x_min_ind = np.argmin(abs(x_axis - cable_x_min)) # x-index of e_field where cable starts
    x_max_ind = np.argmin(abs(x_axis - cable_x_max))
    y_min_ind = np.argmin(abs(y_axis - cable_y_min))
    y_max_ind = np.argmin(abs(y_axis - cable_y_max))
    z_min_ind = np.argmin(abs(z_axis - cable_z_min))
    z_max_ind = np.argmin(abs(z_axis - cable_z_max))

    e_average_prev = 0
    quasi_pot_prev = 0

    offset = 0
    for j in range(len(cable.x)):
        # identify relevant e_field points
        # small e-field: limited by cable limits
        # large e-field: original field
        if cable_x_max - cable_x_min:
            x_position_relative = (cable.x[j] - cable_x_min) / (cable_x_max - cable_x_min)  # number between 0 and 1
        else:
            x_position_relative = 0
        e_field_index_x = x_position_relative * (len(x_axis[x_min_ind:x_max_ind]))  # e_field_index_x in small e-field
        ix = x_min_ind + int(e_field_index_x)  # index in large e-field

        if cable_y_max - cable_y_min:
            y_position_relative = (cable.y[j] - cable_y_min) / (cable_y_max - cable_y_min)  # number between 0 and 1
        else:
            y_position_relative = 0
        e_field_index_y = y_position_relative * (len(y_axis[y_min_ind:y_max_ind]))  # e_field_index_y in small e-field
        iy = y_min_ind + int(e_field_index_y)  # index in large e-field

        if cable_z_max - cable_z_min:
            z_position_relative = (cable.z[j] - cable_z_min) / (cable_z_max - cable_z_min)  # number between 0 and 1
        else:
            z_position_relative = 0
        e_field_index_z = z_position_relative * (len(z_axis[z_min_ind:z_max_ind]))  # e_field_index_z in small e-field
        iz = z_min_ind + int(e_field_index_z)  # index in large e-field
        # check if cable starts outside defined e_field
        if round(cable.y[j]) < min(y_axis) or round(cable.y[j]) > max(y_axis) or round(cable.x[j]) < min(x_axis) or round(cable.x[j]) > max(x_axis) \
                or round(cable.z[j]) < min(z_axis) or round(cable.z[j]) > max(z_axis):
            e_average_current = 0
        else:
            e_x = e_field.e_x
            e_y = e_field.e_y
            e_z = e_field.e_z
            # Simple:
            #---------
            # e_average_current = cable.seg_unit_vectors[j][0] * e_x[iy, ix, iz] + \
            #                     cable.seg_unit_vectors[j][1] * e_y[iy, ix, iz] + \
            #                     cable.seg_unit_vectors[j][2] * e_z[iy, ix, iz]
            # ----------------------------------------------------------------------------------------------------------
            # using interpolation radius: (just possible when e_field is not a single plane)
            # --------
            e_average_current = cable.seg_unit_vectors[j][0] * e_x[iy - r:iy + r, ix - r:ix + r, iz - r:iz + r].sum() + \
                                cable.seg_unit_vectors[j][1] * e_y[iy - r:iy + r, ix - r:ix + r, iz - r:iz + r].sum() + \
                                cable.seg_unit_vectors[j][2] * e_z[iy - r:iy + r, ix - r:ix + r, iz - r:iz + r].sum()

            # this section is new and must be evaluated ----------------------------------------------------------------
            if e_x[iy - r:iy + r, ix - r:ix + r, iz - r:iz + r].size > 0:
                e_average_current = e_average_current / e_x[iy - r:iy + r, ix - r:ix + r, iz - r:iz + r].size
            else:
                e_average_current = cable.seg_unit_vectors[j][0] * e_x[iy, ix, iz] + \
                                    cable.seg_unit_vectors[j][1] * e_y[iy, ix, iz] + \
                                    cable.seg_unit_vectors[j][2] * e_z[iy, ix, iz]
            # ----------------------------------------------------------------------------------------------------------
        if j == 0:
            k = 1
            offset = e_average_current
        else:
            k = j

        e_average_current = e_average_current - offset
        if np.isnan(e_average_current):
            e_average_current = e_average_prev
        e_field_integral = (1 / 2) * (e_average_current + e_average_prev)
        displacement = np.sqrt(
            (cable.x[k] - cable.x[k-1]) ** 2 + (cable.y[k] - cable.y[k-1]) ** 2 + (
                    cable.z[k] - cable.z[k-1]) ** 2) * 1e-3
        quasi_pot_current = quasi_pot_prev - (e_field_integral * displacement)

        # quasi_pot_current in mV; displacement given in um
        #  units? displacement given in um, must me converted with 10e-6 for quasipotentials in V,
        #  but v_ext from NEURON is in mV !!!!!! --> 1e-3

        e_average_prev = e_average_current
        quasi_pot_prev = quasi_pot_current

        e_field_along_axon.append(e_average_current)
        stim_matrix.append(stimulus * quasi_pot_current)
        quasi_pot_along_axon.append(quasi_pot_current)

    # fig = plt.figure()
    # plt.plot(e_field_along_axon)
    # plt.show()
    print('Quasipotential done')
    return stim_matrix, e_field_along_axon, quasi_pot_along_axon


def quasi_potentials_with_details(stimulus, e_field_list, cable, interpolation_radius_index):
    # quasi potential described by Aberra 2019
    # for(each segment)
    #   find e_field coordinates within segment +- deltaX +- deltaY +- deltaZ
    #   e_field_current = interpolate e_field
    #   quasi_pot_current = quasi_pot_prev - (1/2)(e_field_current + e_field_previous) * displacement #calc displacement from model?
    #   generate h.vector with (stimulus and e_field as amplitude) and (time_vector)
    #   play generated vector on segment.e_extracellular
    segment_list = cable.get_segments()

    stim_matrix = []  # contains a row for each segment where the corresponding e-field is multiplied w. stimulus
    e_field_along_axon = []
    quasi_pot_along_axon = []
    x_part = []
    y_part = []
    z_part = []
    x_component = []
    y_component = []
    z_component = []

    r = interpolation_radius_index  # interpolation radius

    cable_x_min = round(min(cable.x))
    cable_x_max = round(max(cable.x))
    cable_y_min = round(min(cable.y))
    cable_y_max = round(max(cable.y))

    # old version, to be deleted
    # x_axis = e_field_list[0].x[:e_field_list[0].e_x.shape[1]]  # indexes of e_field, e.g. -200,...,0,...200
    # x_axis = np.asarray(x_axis)

    x_axis = np.unique(e_field_list[0].x)  # indexes of e_field, e.g. -200,...,0,...200
    y_axis = np.unique(e_field_list[0].y)

    x_min_ind = np.argmin(abs(x_axis - cable_x_min)) # x-index of e_field where cable starts
    x_max_ind = np.argmin(abs(x_axis - cable_x_max))
    y_min_ind = np.argmin(abs(y_axis - cable_y_min))
    y_max_ind = np.argmin(abs(y_axis - cable_y_max))

    e_average_prev = 0
    quasi_pot_prev = 0

    offset = 0
    for j in range(len(segment_list)):
        # identify relevant e_field points
        # small e-field: limited by cable limits
        # large e-field: original field

        if cable_x_max - cable_x_min:
            x_position_relative = (cable.x[j] - cable_x_min) / (cable_x_max - cable_x_min)  # number between 0 and 1
        else:
            x_position_relative = 0
        e_field_index_x = x_position_relative * (len(x_axis[x_min_ind:x_max_ind]))  # e_field_index_x in small e-field
        ix = x_min_ind + int(e_field_index_x)  # index in large e-field

        if cable_y_max - cable_y_min:
            y_position_relative = (cable.y[j] - cable_y_min) / (cable_y_max - cable_y_min)  # number between 0 and 1
        else:
            y_position_relative = 0
        e_field_index_y = y_position_relative * (len(y_axis[y_min_ind:y_max_ind]))  # e_field_index_y in small e-field
        iy = y_min_ind + int(e_field_index_y)  # index in large e-field

        step_vector = cable.get_segment_indices()

        # check if cable starts outside defined e_field
        if cable.y[j] < min(y_axis) or cable.y[j] > max(y_axis) or cable.x[j] < min(x_axis) or cable.x[j] > max(x_axis):
            e_average_current = 0

        else:

            # choose the proper z layer or combination of layers
            e_field_layer_list = []
            for e_field in e_field_list:
                e_field_layer_list.append(e_field.layer)
            index_layer = np.argmin(np.abs(np.asarray(e_field_layer_list) - cable.z[j]))
            e_field = e_field_list[index_layer]
            e_x = e_field.e_x
            e_y = e_field.e_y
            e_z = e_field.e_z
            # efeld_1 = efeld[y_min_ind:y_max_ind, x_min_ind-30:x_max_ind+30]


            e_average_current = cable.get_unitvector()[int(step_vector[j])][0] * e_x[iy - r:iy + r, ix - r:ix + r].sum() + \
                                cable.get_unitvector()[int(step_vector[j])][1] * e_y[iy - r:iy + r, ix - r:ix + r].sum() + \
                                cable.get_unitvector()[int(step_vector[j])][2] * e_z[iy - r:iy + r, ix - r:ix + r].sum()

            x_part.append(cable.get_unitvector()[int(step_vector[j])][0])
            y_part.append(cable.get_unitvector()[int(step_vector[j])][1])
            z_part.append(cable.get_unitvector()[int(step_vector[j])][2])
            x_component.append(cable.get_unitvector()[int(step_vector[j])][0] * e_x[iy, ix])
            y_component.append(cable.get_unitvector()[int(step_vector[j])][1] * e_y[iy, ix])
            z_component.append(cable.get_unitvector()[int(step_vector[j])][1] * e_z[iy, ix])

            # this section is new and must be evaluated ----------------------------------------------------------------
            if e_x[iy - r:iy + r, ix - r:ix + r].size > 0:
                e_average_current = e_average_current / e_x[iy - r:iy + r, ix - r:ix + r].size
            else:
                e_average_current = cable.get_unitvector()[int(step_vector[j])][0] * e_x[iy, ix] + \
                                    cable.get_unitvector()[int(step_vector[j])][1] * e_y[iy, ix] + \
                                    cable.get_unitvector()[int(step_vector[j])][2] * e_z[iy, ix]
            # ----------------------------------------------------------------------------------------------------------

        if j == 0:
            k = 1
            offset = e_average_current
        else:
            k = j

        e_average_current = e_average_current - offset

        e_field_integral = (1 / 2) * (e_average_current + e_average_prev)
        displacement = np.sqrt(
            (cable.x[k] - cable.x[k-1]) ** 2 + (cable.y[k] - cable.y[k-1]) ** 2 + (
                    cable.z[k] - cable.z[k-1]) ** 2) * 1e-3
        quasi_pot_current = quasi_pot_prev - (e_field_integral * displacement)

        # quasi_pot_current in mV; displacement given in um
        #  units? displacement given in um, must me converted with 10e-6 for quasipotentials in V,
        #  but v_ext from NEURON is in mV !!!!!! --> 1e-3

        e_average_prev = e_average_current
        quasi_pot_prev = quasi_pot_current

        e_field_along_axon.append(e_average_current)
        stim_matrix.append(stimulus * quasi_pot_current)
        quasi_pot_along_axon.append(quasi_pot_current)

    # fig = plt.figure()
    # plt.imshow(efeld)
    # plt.colorbar()
    # plt.plot(e_field_along_axon)
    # plt.show()

    return stim_matrix, e_field_along_axon, quasi_pot_along_axon, x_part, y_part, z_part, x_component, y_component, z_component


def find_threshold(axon_model, threshold_step, pulse_amp, total_time, e_field, r_interpol, stimulus):
    axon_model_internal = copy.copy(axon_model)
    time_axis, stimulus = stimulus.get_squarewave_stimulus(1)
    stim_matrix, e_field_list, quasi_pot_list = quasi_potentials(stimulus, e_field, axon_model_internal,
                                                     r_interpol)
    while np.amax(axon_model_internal.potential_vector_list) < 30: #np.amax(model.stimulus_vector_list) < 100:
        print(max(axon_model_internal.potential_vector_list[100]))
        del axon_model_internal.potential_vector_list

        record_membrane_potentials(axon_model_internal, 0.5)
        pulse_amp += threshold_step

        axon_model_internal.stim_matrix = [element * pulse_amp for element in stim_matrix]
        play_stimulus_matrix(axon_model_internal, time_axis)

        # apc_list = []
        # for section in axon_model_internal.sections:
        #     apc = h.APCount(section(0.5))
        #     # print('Treshold: ', apc.thresh)
        #     # print('Treshold: ', apc.n)
        #     # print('Potential: ', section(0.5)._ref_v)
        #     apc_list.append(apc.n)
        # print(apc_list)

        h.finitialize(-80)
        h.continuerun(total_time)
        print(pulse_amp)
    print(max(axon_model_internal.potential_vector_list[100]))
    print('Action potential achieved at pulse_amp=', pulse_amp)

    return stimulus, time_axis

def find_threshold_bisection(axon_model, interval_max, interval_min, precission, total_time, e_field, r_interpol, time_axis, stimulus):
    axon_model_internal = copy.copy(axon_model)
    stim_matrix, e_field_list, quasi_pot_list = quasi_potentials(stimulus, e_field, axon_model_internal,
                                                     r_interpol)


    run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, interval_max)
    if np.amax(axon_model_internal.potential_vector_list) < 30:
        print("Interval Max too low")
        return

    run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, interval_min)
    if np.amax(axon_model_internal.potential_vector_list) >= 30:
        print("Interval Min too high")
        return

    # now the threshold should be within interval boarders
    # bisection starts
    while interval_max - interval_min > precission:
        run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, interval_max - (interval_max - interval_min)/2)
        # if np.amax(axon_model_internal.potential_vector_list) < 30:
        if max(axon_model_internal.potential_vector_list[0]) < 30 or max(axon_model_internal.potential_vector_list[-1]) < 30:
            interval_min = interval_min + (interval_max - interval_min)/2
        # elif np.amax(axon_model_internal.potential_vector_list) >= 30:
        elif max(axon_model_internal.potential_vector_list[0]) >= 30 and max(axon_model_internal.potential_vector_list[-1]) >= 30:
            interval_max = interval_max - (interval_max - interval_min) / 2

    puls_amp_final  = interval_max - (interval_max - interval_min)/2
    print(max(axon_model_internal.potential_vector_list[100]))
    print('Action potential achieved at pulse_amp=', interval_max - (interval_max - interval_min)/2)

    return puls_amp_final

def run_simulation_with_actual_pulse_amp(axon_model_internal, stim_matrix, time_axis, total_time, pulse_amp):
    del axon_model_internal.potential_vector_list

    record_membrane_potentials(axon_model_internal, 0.5)

    axon_model_internal.stim_matrix = [element * pulse_amp for element in stim_matrix]
    play_stimulus_matrix(axon_model_internal, time_axis)

    h.finitialize(-80)
    h.continuerun(total_time)
    print(pulse_amp)
    print(max(axon_model_internal.potential_vector_list[0]))
    print(max(axon_model_internal.potential_vector_list[-1]))

def find_threshold_with_mdf(model, trigger_mdf, stimulus, pulse_amp, step):
    while model.mdf < trigger_mdf:
        pulse_amp += step
        mdf_new = driving_function(model, pulse_amp*stimulus)
    return pulse_amp


def driving_function(model, stimulus, location=None):
    # Driving function (Davids 2020)
    # positive MDF represents current flows from the intracellular space to the extracellular space, and for a negative MDF, the nerve experiences the opposite transmembrane current.
    quasi_pot_matrix_node_only=[]
    MDF=[]

    quasi_pot_matrix_node_only = get_nodes_only(model.sections, model.potential_along_axon)
    quasi_pot_matrix_node_only = [qp * np.amax(stimulus) for qp in quasi_pot_matrix_node_only]  # quasi_pot_list has not yet been multiplied with stimulus
    for i in range(1, len(quasi_pot_matrix_node_only)-1, 1):            #ignore calculation for first and last element to allow iteration (should be changed)
        MDF.append((quasi_pot_matrix_node_only[int(i-1)]-2*quasi_pot_matrix_node_only[i]+quasi_pot_matrix_node_only[int(i+1)])/(model.internode_length + model.node_length)**2)

    return MDF


def get_nodes_only(model_sections, model_trace, location=None):
    output_list = []
    if location is None:
        for sec, trace in zip(model_sections, model_trace):
            for seg in sec:
                if type(sec) == mrg_axon.Node or type(sec) == mhh_model.Node or type(sec) == hh_axon.Node:
                   output_list.append(trace)
    else:
        for sec, trace in zip(model_sections, model_trace):
            if type(sec) == mrg_axon.Node or type(sec) == mhh_model.Node or type(sec) == hh_axon.Node:
                output_list.append(trace)

    return output_list


def filter_efield(e_field):
    r = 30  # how narrower the window is
    ham = np.hamming(e_field.shape[0])[:, None]  # 1D hamming
    ham2d = np.sqrt(np.dot(ham, ham.T)) ** r  # expand to 2D hamming

    f = cv2.dft(e_field.astype(np.float32), flags=cv2.DFT_COMPLEX_OUTPUT)
    f_shifted = np.fft.fftshift(f)
    f_complex = f_shifted[:, :, 0] * 1j + f_shifted[:, :, 1]
    f_filtered = ham2d * f_complex

    f_filtered_shifted = np.fft.fftshift(f_filtered)
    inv_img = np.fft.ifft2(f_filtered_shifted)  # inverse F.T.
    filtered_img = np.abs(inv_img)
    filtered_img -= filtered_img.min()
    # filtered_img = filtered_img * 255 / filtered_img.max()
    # filtered_img = filtered_img.astype(np.uint8)

    return filtered_img


def e_field_offset(e_field):
    e_x = e_field.e_x
    e_y = e_field.e_y
    e_z = e_field.e_z

    offset_x = e_x[0, 0] + e_x[-1, -1] / 2
    offset_y = (e_y[0, 0] + e_y[-1, -1]) / 2
    offset_y_2 = (np.mean(e_y[0, :]) + np.mean(e_y[-1, :]) + np.mean(e_y[:, 0]) + np.mean(e_y[0, -1])) / 4
    offset_z = e_z[0, 0] + e_z[-1, -1] / 2


def generate_new_start_point(x1, y1, z1, x2, y2, z2, offset):
    vec_x = x2 - x1
    vec_y = y2 - y1
    vec_z = z2 - z1

    length = np.sqrt(vec_x**2 + vec_y**2 + vec_z**2)

    new_x = x1 + offset * (vec_x / length)
    new_y = y1 + offset * (vec_y / length)
    new_z = z1 + offset * (vec_z / length)

    return new_x, new_y, new_z


def moving_average(curve, window=18):
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


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
